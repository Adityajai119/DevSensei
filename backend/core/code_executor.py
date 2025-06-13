"""
Code Execution Service for running code in multiple languages
"""
import subprocess
import tempfile
import os
import sys
import time
import threading
import queue
from typing import Dict, Any, Optional, Tuple, List
import logging
import shutil
import signal
import re
try:
    import resource
    HAS_RESOURCE = True
except ImportError:
    HAS_RESOURCE = False

logger = logging.getLogger(__name__)


class CodeExecutor:
    def __init__(self, timeout: int = 30, max_memory: int = 512):
        """Initialize code executor
        
        Args:
            timeout: Maximum execution time in seconds
            max_memory: Maximum memory usage in MB
        """
        self.timeout = timeout
        self.max_memory = max_memory * 1024 * 1024  # Convert to bytes
        
        # Language configurations
        self.language_config = {
            'python': {
                'extension': '.py',
                'command': [sys.executable],
                'allowed_imports': {'math', 'random', 'datetime', 'json', 'collections', 'itertools', 'functools'}
            },
            'javascript': {
                'extension': '.js',
                'command': ['node'],
                'allowed_globals': {'console', 'Math', 'Date', 'JSON', 'Array', 'Object', 'String', 'Number'}
            },
            'typescript': {
                'extension': '.ts',
                'command': ['npx', 'ts-node'],
                'setup_commands': ['npm install -g typescript ts-node'],
                'allowed_globals': {'console', 'Math', 'Date', 'JSON', 'Array', 'Object', 'String', 'Number'}
            },
            'java': {
                'extension': '.java',
                'compile_command': ['javac'],
                'command': ['java'],
                'needs_compile': True,
                'allowed_packages': {'java.util', 'java.lang', 'java.math', 'java.time'}
            },
            'cpp': {
                'extension': '.cpp',
                'compile_command': ['g++', '-o', 'program'],
                'command': ['./program'],
                'needs_compile': True,
                'allowed_headers': {'iostream', 'string', 'vector', 'map', 'set', 'algorithm'}
            },
            'c': {
                'extension': '.c',
                'compile_command': ['gcc', '-o', 'program'],
                'command': ['./program'],
                'needs_compile': True,
                'allowed_headers': {'stdio.h', 'stdlib.h', 'string.h', 'math.h', 'time.h'}
            },
            'go': {
                'extension': '.go',
                'command': ['go', 'run'],
                'allowed_packages': {'fmt', 'math', 'time', 'strings', 'strconv'}
            },
            'rust': {
                'extension': '.rs',
                'compile_command': ['rustc', '-o', 'program'],
                'command': ['./program'],
                'needs_compile': True,
                'allowed_crates': {'std'}
            },
            'ruby': {
                'extension': '.rb',
                'command': ['ruby'],
                'allowed_requires': {'json', 'time', 'math', 'set'}
            },
            'php': {
                'extension': '.php',
                'command': ['php'],
                'allowed_extensions': {'json', 'date', 'math'}
            }
        }
    
    def _validate_code(self, code: str, language: str) -> Tuple[bool, str]:
        """Validate code for security and allowed features"""
        try:
            config = self.language_config[language]
            
            if language == 'python':
                # Check for dangerous imports
                import_pattern = re.compile(r'import\s+(\w+)|from\s+(\w+)\s+import')
                imports = import_pattern.findall(code)
                for imp in imports:
                    module = imp[0] or imp[1]
                    if module not in config['allowed_imports']:
                        return False, f"Import of {module} not allowed"
                
                # Check for dangerous functions
                dangerous_funcs = {'eval', 'exec', 'os.system', 'subprocess.call'}
                for func in dangerous_funcs:
                    if func in code:
                        return False, f"Use of {func} not allowed"
            
            elif language in ['javascript', 'typescript']:
                # Check for dangerous globals
                dangerous_globals = {'process', 'require', 'eval', 'Function'}
                for global_var in dangerous_globals:
                    if global_var in code:
                        return False, f"Use of {global_var} not allowed"
            
            elif language == 'java':
                # Check for dangerous packages
                import_pattern = re.compile(r'import\s+([\w.]+)')
                imports = import_pattern.findall(code)
                for imp in imports:
                    if not any(imp.startswith(pkg) for pkg in config['allowed_packages']):
                        return False, f"Import of {imp} not allowed"
            
            elif language in ['cpp', 'c']:
                # Check for dangerous headers
                include_pattern = re.compile(r'#include\s+[<"]([\w./]+)[>"]')
                includes = include_pattern.findall(code)
                for inc in includes:
                    if inc not in config['allowed_headers']:
                        return False, f"Include of {inc} not allowed"
            
            return True, ""
            
        except Exception as e:
            logger.error(f"Error validating code: {str(e)}")
            return False, f"Validation error: {str(e)}"
    
    def _set_resource_limits(self):
        """Set resource limits for the process (Unix only)"""
        if not HAS_RESOURCE:
            return
        try:
            resource.setrlimit(resource.RLIMIT_AS, (self.max_memory, self.max_memory))
            resource.setrlimit(resource.RLIMIT_CPU, (self.timeout, self.timeout))
            resource.setrlimit(resource.RLIMIT_FSIZE, (1024 * 1024, 1024 * 1024))
            resource.setrlimit(resource.RLIMIT_NPROC, (1, 1))
        except Exception as e:
            logger.error(f"Error setting resource limits: {str(e)}")
    
    def execute_code(self, code: str, language: str, input_data: str = "") -> Dict[str, Any]:
        """Execute code in the specified language
        
        Args:
            code: The code to execute
            language: Programming language
            input_data: Input to provide to the program
            
        Returns:
            Dictionary with output, error, execution time, and status
        """
        language = language.lower()
        if language not in self.language_config:
            return {
                'output': '',
                'error': f'Unsupported language: {language}',
                'execution_time': 0,
                'status': 'error'
            }
        
        # Validate code
        is_valid, error_msg = self._validate_code(code, language)
        if not is_valid:
            return {
                'output': '',
                'error': error_msg,
                'execution_time': 0,
                'status': 'validation_error'
            }
        
        return self._execute_with_subprocess(code, language, input_data)
    
    def _execute_with_subprocess(self, code: str, language: str, input_data: str) -> Dict[str, Any]:
        """Execute code using subprocess with security measures"""
        config = self.language_config[language]
        temp_dir = None
        
        try:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            
            # For Java, extract class name and use it as filename
            if language == 'java':
                class_match = re.search(r'public\s+class\s+(\w+)', code)
                if class_match:
                    class_name = class_match.group(1)
                    file_path = os.path.join(temp_dir, f'{class_name}.java')
                else:
                    return {
                        'output': '',
                        'error': 'No public class found in Java code',
                        'execution_time': 0,
                        'status': 'error'
                    }
            else:
                # For other languages, use default filename
                file_path = os.path.join(temp_dir, f'main{config["extension"]}')
            
            # Write code to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code)
            
            start_time = time.time()
            
            # Compile if needed
            if config.get('needs_compile', False):
                compile_cmd = config['compile_command'] + [file_path]
                compile_result = subprocess.run(
                    compile_cmd,
                    cwd=temp_dir,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    preexec_fn=self._set_resource_limits
                )
                
                if compile_result.returncode != 0:
                    return {
                        'output': '',
                        'error': f'Compilation error: {compile_result.stderr}',
                        'execution_time': time.time() - start_time,
                        'status': 'compilation_error'
                    }
            
            # Run the code
            if config.get('needs_compile', False):
                if language == 'java':
                    run_cmd = config['command'] + [os.path.splitext(os.path.basename(file_path))[0]]
                else:
                    run_cmd = config['command']
            else:
                run_cmd = config['command'] + [file_path]
            
            result = subprocess.run(
                run_cmd,
                cwd=temp_dir,
                input=input_data,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                preexec_fn=self._set_resource_limits
            )
            
            execution_time = time.time() - start_time
            
            return {
                'output': result.stdout,
                'error': result.stderr,
                'execution_time': execution_time,
                'status': 'success' if result.returncode == 0 else 'error'
            }
            
        except subprocess.TimeoutExpired:
            return {
                'output': '',
                'error': f'Execution timed out after {self.timeout} seconds',
                'execution_time': self.timeout,
                'status': 'timeout'
            }
        except Exception as e:
            return {
                'output': '',
                'error': f'Execution error: {str(e)}',
                'execution_time': time.time() - start_time if 'start_time' in locals() else 0,
                'status': 'error'
            }
        finally:
            # Clean up temporary directory
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    logger.error(f"Error cleaning up temporary directory: {str(e)}")
    
    def validate_code(self, code: str, language: str) -> Dict[str, Any]:
        """Validate code for syntax errors and security
        
        Args:
            code: The code to validate
            language: Programming language
            
        Returns:
            Dictionary with validation status and errors
        """
        is_valid, error_msg = self._validate_code(code, language)
        return {
            'status': 'valid' if is_valid else 'invalid',
            'errors': [] if is_valid else [error_msg]
        }
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported programming languages"""
        return list(self.language_config.keys())
    
    def format_code(self, code: str, language: str) -> str:
        """Format code according to language standards
        
        Args:
            code: The code to format
            language: Programming language
            
        Returns:
            Formatted code
        """
        try:
            if language == 'python':
                import black
                return black.format_str(code, mode=black.FileMode())
            elif language in ['javascript', 'typescript']:
                import subprocess
                with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{language}', delete=False) as f:
                    f.write(code)
                    f.flush()
                    result = subprocess.run(['npx', 'prettier', '--write', f.name], capture_output=True, text=True)
                    if result.returncode == 0:
                        with open(f.name, 'r') as f:
                            return f.read()
            return code
        except Exception as e:
            logger.error(f"Error formatting code: {str(e)}")
            return code 