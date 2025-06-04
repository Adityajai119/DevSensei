from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import google.generativeai as genai
import os
import tempfile
import subprocess
import asyncio
import json

router = APIRouter()

class CodeGenerationRequest(BaseModel):
    prompt: str = Field(..., description="Description of what code to generate")
    language: str = Field(..., description="Programming language")
    framework: Optional[str] = Field(None, description="Framework to use (e.g., React, Django, FastAPI)")
    requirements: Optional[List[str]] = Field(None, description="Specific requirements or constraints")
    gemini_api_key: Optional[str] = Field(None, description="Gemini API key")

class CodeDebugRequest(BaseModel):
    code: str = Field(..., description="Code with bugs")
    error_message: Optional[str] = Field(None, description="Error message if available")
    language: str = Field(..., description="Programming language")
    expected_behavior: Optional[str] = Field(None, description="What the code should do")
    gemini_api_key: Optional[str] = Field(None, description="Gemini API key")

class CodeTestRequest(BaseModel):
    code: str = Field(..., description="Code to generate tests for")
    language: str = Field(..., description="Programming language")
    test_framework: Optional[str] = Field(None, description="Testing framework to use")
    coverage_goals: Optional[List[str]] = Field(None, description="What to test")
    gemini_api_key: Optional[str] = Field(None, description="Gemini API key")

class CodeExecutionRequest(BaseModel):
    code: str = Field(..., description="Code to execute")
    language: str = Field(..., description="Programming language")
    input_data: Optional[str] = Field(None, description="Input data for the program")

def configure_gemini(api_key: Optional[str] = None):
    """Configure Gemini AI with API key"""
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise HTTPException(status_code=401, detail="Gemini API key not provided")
    genai.configure(api_key=key)
    return genai.GenerativeModel('gemini-pro')

@router.post("/generate")
async def generate_code(request: CodeGenerationRequest):
    """Generate code based on natural language prompt"""
    try:
        model = configure_gemini(request.gemini_api_key)
        
        # Build comprehensive prompt
        framework_info = f"using {request.framework}" if request.framework else ""
        requirements_info = ""
        if request.requirements:
            requirements_info = f"\n\nSpecific requirements:\n" + "\n".join(f"- {req}" for req in request.requirements)
        
        prompt = f"""
        Generate production-ready {request.language} code {framework_info} for the following task:
        
        {request.prompt}
        {requirements_info}
        
        Please provide:
        1. Complete, working code with all necessary imports
        2. Clear comments explaining key parts
        3. Error handling where appropriate
        4. Following best practices for {request.language} {framework_info}
        5. Any necessary configuration or setup instructions
        
        Format the code properly and ensure it's ready to run.
        """
        
        response = model.generate_content(prompt)
        
        # Extract code from response
        import re
        code_blocks = re.findall(r'```(?:\w+)?\n(.*?)```', response.text, re.DOTALL)
        generated_code = code_blocks[0] if code_blocks else response.text
        
        # Analyze the generated code
        analysis_prompt = f"""
        Analyze this {request.language} code and provide:
        1. Main components/functions
        2. Dependencies required
        3. Complexity estimate
        4. Potential improvements
        
        Code:
        ```
        {generated_code}
        ```
        """
        
        analysis_response = model.generate_content(analysis_prompt)
        
        return {
            "generated_code": generated_code,
            "language": request.language,
            "framework": request.framework,
            "explanation": response.text,
            "code_analysis": analysis_response.text,
            "metadata": {
                "lines_of_code": len(generated_code.splitlines()),
                "characters": len(generated_code)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/debug")
async def debug_code(request: CodeDebugRequest):
    """Debug code and provide fixes"""
    try:
        model = configure_gemini(request.gemini_api_key)
        
        error_context = f"\nError message: {request.error_message}" if request.error_message else ""
        behavior_context = f"\nExpected behavior: {request.expected_behavior}" if request.expected_behavior else ""
        
        prompt = f"""
        Debug the following {request.language} code and fix any issues:
        
        ```
        {request.code}
        ```
        {error_context}
        {behavior_context}
        
        Please:
        1. Identify all bugs and issues
        2. Explain what's wrong and why
        3. Provide the corrected code
        4. Explain what was changed and why
        5. Suggest any additional improvements
        6. Add debugging tips for similar issues
        """
        
        response = model.generate_content(prompt)
        
        # Extract fixed code
        import re
        code_blocks = re.findall(r'```(?:\w+)?\n(.*?)```', response.text, re.DOTALL)
        fixed_code = code_blocks[0] if code_blocks else request.code
        
        # Generate diff-like comparison
        original_lines = request.code.splitlines()
        fixed_lines = fixed_code.splitlines()
        
        changes = []
        for i, (orig, fixed) in enumerate(zip(original_lines, fixed_lines)):
            if orig != fixed:
                changes.append({
                    "line": i + 1,
                    "original": orig,
                    "fixed": fixed
                })
        
        return {
            "original_code": request.code,
            "fixed_code": fixed_code,
            "debugging_report": response.text,
            "changes": changes,
            "issue_count": len(changes)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-tests")
async def generate_tests(request: CodeTestRequest):
    """Generate test cases for code"""
    try:
        model = configure_gemini(request.gemini_api_key)
        
        framework = request.test_framework or {
            "python": "pytest",
            "javascript": "jest",
            "typescript": "jest",
            "java": "junit",
            "csharp": "xunit",
            "go": "testing"
        }.get(request.language.lower(), "default")
        
        coverage_info = ""
        if request.coverage_goals:
            coverage_info = f"\nFocus on testing: " + ", ".join(request.coverage_goals)
        
        prompt = f"""
        Generate comprehensive test cases for the following {request.language} code using {framework}:
        
        ```
        {request.code}
        ```
        {coverage_info}
        
        Please provide:
        1. Unit tests for all functions/methods
        2. Edge case tests
        3. Error handling tests
        4. Integration tests (if applicable)
        5. Test setup and teardown
        6. Mock objects (if needed)
        7. Clear test descriptions
        
        Ensure high code coverage and follow {framework} best practices.
        """
        
        response = model.generate_content(prompt)
        
        # Extract test code
        import re
        code_blocks = re.findall(r'```(?:\w+)?\n(.*?)```', response.text, re.DOTALL)
        test_code = code_blocks[0] if code_blocks else response.text
        
        # Analyze test coverage
        coverage_prompt = f"""
        Analyze the test coverage for these tests and estimate:
        1. Approximate code coverage percentage
        2. What's covered well
        3. What might be missing
        4. Suggested additional tests
        """
        
        coverage_response = model.generate_content(coverage_prompt)
        
        return {
            "test_code": test_code,
            "test_framework": framework,
            "test_explanation": response.text,
            "coverage_analysis": coverage_response.text,
            "test_count": len(re.findall(r'test_|it\(|@Test|def test', test_code))
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute")
async def execute_code(request: CodeExecutionRequest):
    """Execute code in a sandboxed environment (limited languages)"""
    try:
        # Only allow safe languages for execution
        allowed_languages = ["python", "javascript", "ruby"]
        if request.language.lower() not in allowed_languages:
            raise HTTPException(
                status_code=400, 
                detail=f"Code execution not supported for {request.language}. Supported: {', '.join(allowed_languages)}"
            )
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{request.language}', delete=False) as f:
            f.write(request.code)
            temp_file = f.name
        
        try:
            # Prepare command based on language
            if request.language.lower() == "python":
                cmd = ["python", temp_file]
            elif request.language.lower() == "javascript":
                cmd = ["node", temp_file]
            elif request.language.lower() == "ruby":
                cmd = ["ruby", temp_file]
            
            # Execute with timeout
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Send input if provided
            input_bytes = request.input_data.encode() if request.input_data else None
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(input=input_bytes),
                    timeout=10.0  # 10 second timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                raise HTTPException(status_code=408, detail="Code execution timed out (10s limit)")
            
            return {
                "output": stdout.decode(),
                "errors": stderr.decode(),
                "exit_code": process.returncode,
                "language": request.language,
                "execution_time": "< 10s"
            }
            
        finally:
            # Clean up temp file
            os.unlink(temp_file)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/refactor")
async def refactor_code(request: CodeGenerationRequest):
    """Refactor existing code following best practices"""
    try:
        model = configure_gemini(request.gemini_api_key)
        
        requirements_info = ""
        if request.requirements:
            requirements_info = "\nRefactoring goals:\n" + "\n".join(f"- {req}" for req in request.requirements)
        
        prompt = f"""
        Refactor the following {request.language} code to improve quality:
        
        ```
        {request.prompt}  # This contains the code to refactor
        ```
        {requirements_info}
        
        Apply these refactoring principles:
        1. SOLID principles
        2. DRY (Don't Repeat Yourself)
        3. Clean Code practices
        4. Design patterns where appropriate
        5. Better naming conventions
        6. Improved error handling
        7. Performance optimizations
        8. Better code organization
        
        Provide the refactored code with explanations for major changes.
        """
        
        response = model.generate_content(prompt)
        
        # Extract refactored code
        import re
        code_blocks = re.findall(r'```(?:\w+)?\n(.*?)```', response.text, re.DOTALL)
        refactored_code = code_blocks[0] if code_blocks else request.prompt
        
        return {
            "original_code": request.prompt,
            "refactored_code": refactored_code,
            "refactoring_explanation": response.text,
            "improvements": request.requirements or ["General code quality improvements"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/convert")
async def convert_code(
    source_code: str,
    source_language: str,
    target_language: str,
    gemini_api_key: Optional[str] = None
):
    """Convert code from one language to another"""
    try:
        model = configure_gemini(gemini_api_key)
        
        prompt = f"""
        Convert the following {source_language} code to {target_language}:
        
        ```
        {source_code}
        ```
        
        Requirements:
        1. Maintain the same functionality
        2. Use idiomatic {target_language} patterns
        3. Include necessary imports/dependencies
        4. Add appropriate comments
        5. Handle language-specific differences
        6. Ensure the code is ready to run
        
        Explain any significant changes required due to language differences.
        """
        
        response = model.generate_content(prompt)
        
        # Extract converted code
        import re
        code_blocks = re.findall(r'```(?:\w+)?\n(.*?)```', response.text, re.DOTALL)
        converted_code = code_blocks[0] if code_blocks else ""
        
        return {
            "source_language": source_language,
            "target_language": target_language,
            "source_code": source_code,
            "converted_code": converted_code,
            "conversion_notes": response.text,
            "success": bool(converted_code)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 