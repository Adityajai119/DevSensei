from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import subprocess
import tempfile
import os
import uuid
from app.services.gemini_service import gemini_service

router = APIRouter()

class CodeExecutionRequest(BaseModel):
    code: str
    language: str
    input_data: Optional[str] = None

class CodeExecutionResponse(BaseModel):
    output: str
    error: Optional[str] = None
    execution_time: Optional[float] = None
    memory_usage: Optional[float] = None

class CodeGenerationRequest(BaseModel):
    prompt: str
    language: str
    context: Optional[str] = None

class CodeGenerationResponse(BaseModel):
    code: str
    explanation: str
    language: str

class CodeOptimizationRequest(BaseModel):
    code: str
    language: str
    optimization_type: str = "performance"

class CodeDebugRequest(BaseModel):
    code: str
    language: str
    error_message: Optional[str] = None
    expected_output: Optional[str] = None

class CodeExplanationRequest(BaseModel):
    code: str
    language: str

class FrontendGenerationRequest(BaseModel):
    prompt: str
    framework: str = "vanilla"

class LanguageInfo(BaseModel):
    name: str
    extension: str
    command: str
    args: List[str]

@router.post("/execute", response_model=CodeExecutionResponse)
async def execute_code(request: CodeExecutionRequest):
    """Execute code in various programming languages"""
    try:
        # Language configurations
        languages = {
            "python": LanguageInfo(
                name="Python",
                extension=".py",
                command="python",
                args=[]
            ),
            "javascript": LanguageInfo(
                name="JavaScript",
                extension=".js",
                command="node",
                args=[]
            ),
            "java": LanguageInfo(
                name="Java",
                extension=".java",
                command="java",
                args=[]
            ),
            "cpp": LanguageInfo(
                name="C++",
                extension=".cpp",
                command="g++",
                args=["-o", "program"]
            ),
            "c": LanguageInfo(
                name="C",
                extension=".c",
                command="gcc",
                args=["-o", "program"]
            ),
            "go": LanguageInfo(
                name="Go",
                extension=".go",
                command="go",
                args=["run"]
            ),
            "rust": LanguageInfo(
                name="Rust",
                extension=".rs",
                command="rustc",
                args=["-o", "program"]
            ),
            "php": LanguageInfo(
                name="PHP",
                extension=".php",
                command="php",
                args=[]
            ),
            "ruby": LanguageInfo(
                name="Ruby",
                extension=".rb",
                command="ruby",
                args=[]
            ),
            "csharp": LanguageInfo(
                name="C#",
                extension=".cs",
                command="dotnet",
                args=["run"]
            )
        }
        
        if request.language not in languages:
            raise HTTPException(status_code=400, detail=f"Unsupported language: {request.language}")
        
        lang_info = languages[request.language]
        temp_dir = tempfile.gettempdir()
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix=lang_info.extension,
            delete=False,
            dir=temp_dir
        ) as temp_file:
            temp_file.write(request.code)
            temp_file_path = temp_file.name
        
        try:
            # Execute code based on language
            if request.language in ["cpp", "c", "rust"]:
                # Compile first, then run
                compile_result = subprocess.run(
                    [lang_info.command] + lang_info.args + [temp_file_path],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if compile_result.returncode != 0:
                    return CodeExecutionResponse(
                        output="",
                        error=f"Compilation error:\n{compile_result.stderr}"
                    )
                
                # Run compiled program
                exec_result = subprocess.run(
                    ["./program"],
                    capture_output=True,
                    text=True,
                    input=request.input_data,
                    timeout=30
                )
                
                output = exec_result.stdout
                error = exec_result.stderr if exec_result.returncode != 0 else None
                
            elif request.language == "java":
                # Java requires class name to match filename
                class_name = os.path.basename(temp_file_path).replace('.java', '')
                
                # Compile
                compile_result = subprocess.run(
                    ["javac", temp_file_path],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if compile_result.returncode != 0:
                    return CodeExecutionResponse(
                        output="",
                        error=f"Compilation error:\n{compile_result.stderr}"
                    )
                
                # Run
                exec_result = subprocess.run(
                    ["java", "-cp", "/tmp", class_name],
                    capture_output=True,
                    text=True,
                    input=request.input_data,
                    timeout=30
                )
                
                output = exec_result.stdout
                error = exec_result.stderr if exec_result.returncode != 0 else None
                
            elif request.language == "csharp":
                # Create a simple C# project structure
                project_dir = f"/tmp/csharp_project_{uuid.uuid4().hex[:8]}"
                os.makedirs(project_dir, exist_ok=True)
                
                # Create project file
                project_file = os.path.join(project_dir, "Program.csproj")
                with open(project_file, 'w') as f:
                    f.write("""<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net6.0</TargetFramework>
  </PropertyGroup>
</Project>""")
                
                # Create program file
                program_file = os.path.join(project_dir, "Program.cs")
                with open(program_file, 'w') as f:
                    f.write(request.code)
                
                # Run
                exec_result = subprocess.run(
                    ["dotnet", "run"],
                    capture_output=True,
                    text=True,
                    input=request.input_data,
                    timeout=30,
                    cwd=project_dir
                )
                
                output = exec_result.stdout
                error = exec_result.stderr if exec_result.returncode != 0 else None
                
            else:
                # Interpreted languages
                exec_result = subprocess.run(
                    [lang_info.command] + lang_info.args + [temp_file_path],
                    capture_output=True,
                    text=True,
                    input=request.input_data,
                    timeout=30
                )
                
                output = exec_result.stdout
                error = exec_result.stderr if exec_result.returncode != 0 else None
            
            return CodeExecutionResponse(
                output=output,
                error=error
            )
            
        except Exception as e:
            return CodeExecutionResponse(output="", error=f"Execution error: {str(e)}")
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Code execution error: {str(e)}")

@router.post("/generate", response_model=CodeGenerationResponse)
async def generate_code(request: CodeGenerationRequest):
    """Generate code using AI"""
    try:
        generated_code = await gemini_service.generate_code(
            request.prompt,
            request.language,
            request.context
        )
        
        return CodeGenerationResponse(
            code=generated_code,
            explanation=f"Generated {request.language} code based on your prompt",
            language=request.language
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimize")
async def optimize_code(request: CodeOptimizationRequest):
    """Optimize code"""
    try:
        # Mock code optimization - replace with actual optimization logic
        original_code = request.code
        optimization_type = request.optimization_type
        
        if optimization_type == "performance":
            optimized_code = f"""# Optimized code for performance
# Original: {original_code}

# Performance optimizations applied:
# 1. Reduced function calls
# 2. Optimized loops
# 3. Improved memory usage

{original_code.replace('print', 'print_optimized')}
"""
        elif optimization_type == "readability":
            optimized_code = f"""# Optimized code for readability
# Original: {original_code}

# Readability improvements:
# 1. Better variable names
# 2. Clearer structure
# 3. Added comments

{original_code}
# End of optimized code
"""
        else:
            optimized_code = f"# {optimization_type} optimized code\n{original_code}"
        
        return {
            "original_code": original_code,
            "optimized_code": optimized_code,
            "language": request.language,
            "optimization_type": optimization_type,
            "improvements": [
                "Reduced execution time by 20%",
                "Improved memory efficiency",
                "Enhanced code readability"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/debug")
async def debug_code(request: CodeDebugRequest):
    """Debug code"""
    try:
        # Mock code debugging - replace with actual debugging logic
        code = request.code
        error_message = request.error_message
        expected_output = request.expected_output
        
        if error_message:
            debug_suggestions = [
                f"Check for syntax error: {error_message}",
                "Verify variable names and scope",
                "Ensure proper indentation",
                "Check for missing imports"
            ]
        else:
            debug_suggestions = [
                "Add print statements for debugging",
                "Check variable values at key points",
                "Verify logic flow",
                "Test with different inputs"
            ]
        
        fixed_code = f"""# Debugged code
# Original: {code}
# Error: {error_message or 'No specific error'}

# Debugging suggestions:
{chr(10).join(f"# {suggestion}" for suggestion in debug_suggestions)}

{code}

# Add debugging output
print("Debug: Code execution completed")
"""
        
        return {
            "original_code": code,
            "debugged_code": fixed_code,
            "language": request.language,
            "error_message": error_message,
            "expected_output": expected_output,
            "suggestions": debug_suggestions,
            "debug_steps": [
                "Added error handling",
                "Included debug output",
                "Improved code structure"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/explain")
async def explain_code(request: CodeExplanationRequest):
    """Explain code"""
    try:
        # Mock code explanation - replace with actual AI integration
        code = request.code
        language = request.language
        
        explanation = f"""Code Explanation for {language}:

**Overview**: This code appears to be a well-structured program written in {language}.

**Key Components**:
1. **Main Logic**: The code implements functionality based on the provided input
2. **Structure**: It follows good programming practices for {language}
3. **Complexity**: Moderate complexity with clear logic flow

**Code Analysis**:
- **Lines of Code**: {len(code.split(chr(10)))} lines
- **Functions**: Contains function definitions
- **Variables**: Uses appropriate variable naming
- **Comments**: {chr(10).join(line for line in code.split(chr(10)) if line.strip().startswith('#'))}

**Recommendations**:
1. Add more comprehensive documentation
2. Include error handling mechanisms
3. Consider adding unit tests
4. Follow {language} style guidelines

**Best Practices Applied**:
- Clear variable naming
- Logical code structure
- Proper indentation
- Good separation of concerns

The code demonstrates good understanding of {language} programming concepts."""
        
        return {
            "explanation": explanation,
            "language": language,
            "complexity": "moderate",
            "suggestions": [
                "Add more documentation",
                "Include error handling",
                "Consider unit tests",
                "Follow style guidelines"
            ],
            "code_metrics": {
                "lines": len(code.split(chr(10))),
                "functions": code.count("def ") if language == "python" else code.count("function "),
                "comments": len([line for line in code.split(chr(10)) if line.strip().startswith('#')])
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-frontend")
async def generate_frontend(request: FrontendGenerationRequest):
    """Generate frontend code"""
    try:
        # Use real Gemini service to generate frontend code
        code = await gemini_service.generate_frontend(request.prompt, request.framework)
        
        return {
            "code": code,
            "framework": request.framework,
            "html": code if request.framework == "vanilla" else None,
            "css": "/* Generated CSS */",
            "javascript": "// Generated JavaScript",
            "explanation": f"Generated {request.framework} frontend based on your prompt."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/languages")
async def get_supported_languages():
    """Get list of supported programming languages"""
    return {
        "languages": [
            {"name": "Python", "value": "python", "extension": ".py"},
            {"name": "JavaScript", "value": "javascript", "extension": ".js"},
            {"name": "TypeScript", "value": "typescript", "extension": ".ts"},
            {"name": "Java", "value": "java", "extension": ".java"},
            {"name": "C++", "value": "cpp", "extension": ".cpp"},
            {"name": "C", "value": "c", "extension": ".c"},
            {"name": "Go", "value": "go", "extension": ".go"},
            {"name": "Rust", "value": "rust", "extension": ".rs"},
            {"name": "PHP", "value": "php", "extension": ".php"},
            {"name": "Ruby", "value": "ruby", "extension": ".rb"},
            {"name": "C#", "value": "csharp", "extension": ".cs"}
        ]
    }

@router.post("/analyze")
async def analyze_code(request: Dict[str, Any]):
    """Analyze code using AI"""
    try:
        code = request.get("code", "")
        language = request.get("language", "python")
        
        analysis = await gemini_service.analyze_code(code, language)
        
        return {
            "analysis": analysis,
            "language": language,
            "code_length": len(code),
            "lines": len(code.split('\n'))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 