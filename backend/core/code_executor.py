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
from typing import Dict, Any, Optional, Tuple
import docker
from docker.errors import DockerException
import logging

logger = logging.getLogger(__name__)


class CodeExecutor:
    def __init__(self, use_docker: bool = True, timeout: int = 30):
        """Initialize code executor
        
        Args:
            use_docker: Whether to use Docker for sandboxed execution
            timeout: Maximum execution time in seconds
        """
        self.use_docker = use_docker
        self.timeout = timeout
        self.docker_client = None
        
        if use_docker:
            try:
                self.docker_client = docker.from_env()
                logger.info("Docker client initialized successfully")
            except DockerException:
                logger.warning("Docker not available, falling back to subprocess execution")
                self.use_docker = False
        
        # Language configurations
        self.language_config = {
            'python': {
                'extension': '.py',
                'command': [sys.executable],
                'docker_image': 'python:3.9-slim',
                'docker_command': 'python'
            },
            'javascript': {
                'extension': '.js',
                'command': ['node'],
                'docker_image': 'node:16-alpine',
                'docker_command': 'node'
            },
            'typescript': {
                'extension': '.ts',
                'command': ['npx', 'ts-node'],
                'docker_image': 'node:16-alpine',
                'docker_command': 'npx ts-node',
                'setup_commands': ['npm install -g typescript ts-node']
            },
            'java': {
                'extension': '.java',
                'compile_command': ['javac'],
                'command': ['java'],
                'docker_image': 'openjdk:11-slim',
                'needs_compile': True
            },
            'cpp': {
                'extension': '.cpp',
                'compile_command': ['g++', '-o', 'program'],
                'command': ['./program'],
                'docker_image': 'gcc:latest',
                'needs_compile': True
            },
            'c': {
                'extension': '.c',
                'compile_command': ['gcc', '-o', 'program'],
                'command': ['./program'],
                'docker_image': 'gcc:latest',
                'needs_compile': True
            },
            'go': {
                'extension': '.go',
                'command': ['go', 'run'],
                'docker_image': 'golang:1.19-alpine',
                'docker_command': 'go run'
            },
            'rust': {
                'extension': '.rs',
                'compile_command': ['rustc', '-o', 'program'],
                'command': ['./program'],
                'docker_image': 'rust:latest',
                'needs_compile': True
            },
            'ruby': {
                'extension': '.rb',
                'command': ['ruby'],
                'docker_image': 'ruby:3.0-slim',
                'docker_command': 'ruby'
            },
            'php': {
                'extension': '.php',
                'command': ['php'],
                'docker_image': 'php:8.0-cli',
                'docker_command': 'php'
            }
        }
    
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
        
        if self.use_docker and self.docker_client:
            return self._execute_with_docker(code, language, input_data)
        else:
            return self._execute_with_subprocess(code, language, input_data)
    
    def _execute_with_subprocess(self, code: str, language: str, input_data: str) -> Dict[str, Any]:
        """Execute code using subprocess (less secure)"""
        config = self.language_config[language]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Write code to file
            file_path = os.path.join(temp_dir, f'main{config["extension"]}')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code)
            
            start_time = time.time()
            
            try:
                # Compile if needed
                if config.get('needs_compile', False):
                    compile_cmd = config['compile_command'] + [file_path]
                    compile_result = subprocess.run(
                        compile_cmd,
                        cwd=temp_dir,
                        capture_output=True,
                        text=True,
                        timeout=self.timeout
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
                    run_cmd = config['command']
                else:
                    run_cmd = config['command'] + [file_path]
                
                result = subprocess.run(
                    run_cmd,
                    cwd=temp_dir,
                    input=input_data,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout
                )
                
                execution_time = time.time() - start_time
                
                return {
                    'output': result.stdout,
                    'error': result.stderr,
                    'execution_time': execution_time,
                    'status': 'success' if result.returncode == 0 else 'runtime_error',
                    'exit_code': result.returncode
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
                    'error': str(e),
                    'execution_time': time.time() - start_time,
                    'status': 'error'
                }
    
    def _execute_with_docker(self, code: str, language: str, input_data: str) -> Dict[str, Any]:
        """Execute code in a Docker container (secure)"""
        config = self.language_config[language]
        
        try:
            # Create a temporary directory for the code
            with tempfile.TemporaryDirectory() as temp_dir:
                file_name = f'main{config["extension"]}'
                file_path = os.path.join(temp_dir, file_name)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(code)
                
                # Prepare Docker command
                docker_cmd = []
                
                # Setup commands if needed
                if 'setup_commands' in config:
                    for cmd in config['setup_commands']:
                        docker_cmd.extend(['sh', '-c', f'{cmd} && '])
                
                # Main execution command
                if config.get('needs_compile', False):
                    compile_cmd = ' '.join(config['compile_command'] + [file_name])
                    run_cmd = ' '.join(config['command'])
                    docker_cmd = ['sh', '-c', f'{compile_cmd} && {run_cmd}']
                else:
                    if 'docker_command' in config:
                        docker_cmd = config['docker_command'].split() + [file_name]
                    else:
                        docker_cmd = config['command'] + [file_name]
                
                start_time = time.time()
                
                # Run container
                container = self.docker_client.containers.run(
                    config['docker_image'],
                    command=docker_cmd,
                    volumes={temp_dir: {'bind': '/app', 'mode': 'ro'}},
                    working_dir='/app',
                    stdin_open=True,
                    detach=True,
                    mem_limit='512m',
                    cpu_quota=50000,  # 50% of one CPU
                    remove=True
                )
                
                # Send input if provided
                if input_data:
                    container.attach(stdin=True).send(input_data.encode())
                
                # Wait for completion with timeout
                result = container.wait(timeout=self.timeout)
                logs = container.logs(stdout=True, stderr=True).decode('utf-8')
                
                execution_time = time.time() - start_time
                
                # Parse output and error
                # Docker logs combine stdout and stderr, so we need to handle this
                output_lines = logs.split('\n')
                
                return {
                    'output': logs,
                    'error': '',
                    'execution_time': execution_time,
                    'status': 'success' if result['StatusCode'] == 0 else 'runtime_error',
                    'exit_code': result['StatusCode']
                }
                
        except Exception as e:
            return {
                'output': '',
                'error': f'Docker execution error: {str(e)}',
                'execution_time': 0,
                'status': 'error'
            }
    
    def validate_code(self, code: str, language: str) -> Dict[str, Any]:
        """Validate code syntax without executing it"""
        language = language.lower()
        
        if language == 'python':
            try:
                compile(code, '<string>', 'exec')
                return {'valid': True, 'error': None}
            except SyntaxError as e:
                return {'valid': False, 'error': str(e)}
        
        # For other languages, we might need to use language-specific tools
        # or attempt compilation without execution
        return {'valid': True, 'error': None}
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported programming languages"""
        return list(self.language_config.keys())
    
    def format_code(self, code: str, language: str) -> str:
        """Format code according to language standards"""
        language = language.lower()
        
        if language == 'python':
            try:
                import black
                return black.format_str(code, mode=black.Mode())
            except:
                pass
        
        # Return unformatted code if formatting is not available
        return code 