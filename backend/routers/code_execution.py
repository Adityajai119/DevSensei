from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import google.generativeai as genai
import os
from dotenv import load_dotenv
import sys
import json
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.code_executor import CodeExecutor
from core.nlp_processor import NLPProcessor

load_dotenv()

router = APIRouter()

# Initialize services
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=GEMINI_API_KEY)
code_executor = CodeExecutor(use_docker=False)  # Set to True if Docker is available
nlp_processor = NLPProcessor()


class CodeExecutionRequest(BaseModel):
    code: str
    language: str
    input_data: Optional[str] = ""


class CodeGenerationRequest(BaseModel):
    prompt: str
    language: str = "python"
    context: Optional[str] = None


class CodeOptimizationRequest(BaseModel):
    code: str
    language: str
    optimization_type: str = "performance"  # performance, memory, readability


class CodeDebugRequest(BaseModel):
    code: str
    language: str
    error_message: Optional[str] = None
    expected_output: Optional[str] = None


class FrontendCodeRequest(BaseModel):
    prompt: str
    framework: str = "vanilla"  # vanilla, react, vue, angular


@router.post("/execute")
async def execute_code(request: CodeExecutionRequest):
    """Execute code in the specified language"""
    try:
        # Validate code first
        validation = code_executor.validate_code(request.code, request.language)
        if not validation['valid']:
            return {
                'output': '',
                'error': f"Syntax error: {validation['error']}",
                'execution_time': 0,
                'status': 'syntax_error'
            }
        
        # Execute the code
        result = code_executor.execute_code(
            request.code,
            request.language,
            request.input_data
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate")
async def generate_code(request: CodeGenerationRequest):
    """Generate code based on prompt"""
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        # Create prompt
        prompt = f"""Generate {request.language} code for the following requirement:

{request.prompt}

{f'Context: {request.context}' if request.context else ''}

Requirements:
1. Write clean, well-commented code
2. Follow best practices for {request.language}
3. Include error handling
4. Make it production-ready
5. Add example usage if applicable

Code:
```{request.language}"""
        
        response = model.generate_content(prompt)
        
        # Extract code from response
        code = response.text
        if "```" in code:
            parts = code.split("```")
            for i, part in enumerate(parts):
                if i % 2 == 1:  # Code blocks are at odd indices
                    # Remove language identifier
                    lines = part.strip().split('\n')
                    if lines and lines[0].lower() in ['python', 'javascript', 'java', 'cpp', 'c', 'go', 'rust']:
                        code = '\n'.join(lines[1:])
                    else:
                        code = part.strip()
                    break
        
        # Analyze the generated code
        analysis = nlp_processor.extract_code_entities(code, request.language)
        
        return {
            'code': code,
            'language': request.language,
            'analysis': analysis,
            'description': f"Generated {request.language} code for: {request.prompt}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize")
async def optimize_code(request: CodeOptimizationRequest):
    """Optimize code for performance, memory, or readability"""
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        # Analyze current code
        current_analysis = nlp_processor.analyze_code_complexity(request.code, request.language)
        
        optimization_prompts = {
            'performance': 'Optimize this code for better performance and execution speed',
            'memory': 'Optimize this code for lower memory usage',
            'readability': 'Refactor this code for better readability and maintainability'
        }
        
        prompt = f"""Please {optimization_prompts.get(request.optimization_type, optimization_prompts['performance'])}:

```{request.language}
{request.code}
```

Provide:
1. Optimized version of the code
2. Explanation of changes made
3. Performance/memory improvements expected
4. Any trade-offs

Optimized code:
```{request.language}"""
        
        response = model.generate_content(prompt)
        
        # Extract optimized code
        response_text = response.text
        optimized_code = request.code  # Default to original
        explanation = ""
        
        if "```" in response_text:
            parts = response_text.split("```")
            for i, part in enumerate(parts):
                if i % 2 == 1:  # Code blocks
                    lines = part.strip().split('\n')
                    if lines and lines[0].lower() == request.language.lower():
                        optimized_code = '\n'.join(lines[1:])
                    else:
                        optimized_code = part.strip()
                    break
            
            # Extract explanation
            explanation_start = response_text.find("```", response_text.find("```") + 3) + 3
            if explanation_start > 3:
                explanation = response_text[explanation_start:].strip()
        
        # Analyze optimized code
        optimized_analysis = nlp_processor.analyze_code_complexity(optimized_code, request.language)
        
        return {
            'original_code': request.code,
            'optimized_code': optimized_code,
            'explanation': explanation,
            'original_metrics': current_analysis,
            'optimized_metrics': optimized_analysis,
            'optimization_type': request.optimization_type
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/debug")
async def debug_code(request: CodeDebugRequest):
    """Debug code and provide fixes"""
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""Debug the following {request.language} code:

```{request.language}
{request.code}
```

{f'Error message: {request.error_message}' if request.error_message else ''}
{f'Expected output: {request.expected_output}' if request.expected_output else ''}

Please:
1. Identify all bugs and issues
2. Explain what's causing the problems
3. Provide the corrected code
4. Add comments explaining the fixes
5. Suggest best practices to avoid these issues

Fixed code:
```{request.language}"""
        
        response = model.generate_content(prompt)
        response_text = response.text
        
        # Extract fixed code
        fixed_code = request.code  # Default
        debug_explanation = ""
        
        if "```" in response_text:
            parts = response_text.split("```")
            for i, part in enumerate(parts):
                if i % 2 == 1:  # Code blocks
                    lines = part.strip().split('\n')
                    if lines and lines[0].lower() == request.language.lower():
                        fixed_code = '\n'.join(lines[1:])
                    else:
                        fixed_code = part.strip()
                    break
            
            # Extract explanation
            explanation_start = response_text.find("```", response_text.find("```") + 3) + 3
            if explanation_start > 3:
                debug_explanation = response_text[explanation_start:].strip()
        
        # Test the fixed code
        test_result = code_executor.execute_code(fixed_code, request.language)
        
        return {
            'original_code': request.code,
            'fixed_code': fixed_code,
            'explanation': debug_explanation,
            'test_result': test_result,
            'bugs_found': True if fixed_code != request.code else False
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/explain")
async def explain_code(code: str, language: str):
    """Explain code in detail"""
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        # Get NLP analysis
        entities = nlp_processor.extract_code_entities(code, language)
        complexity = nlp_processor.analyze_code_complexity(code, language)
        
        prompt = f"""Explain this {language} code in detail:

```{language}
{code}
```

Please provide:
1. Overall purpose and functionality
2. Step-by-step explanation
3. Key concepts used
4. Time and space complexity
5. Potential use cases
6. Possible improvements"""
        
        response = model.generate_content(prompt)
        
        return {
            'explanation': response.text,
            'entities': entities,
            'complexity': complexity,
            'language': language
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-frontend")
async def generate_frontend_code(request: FrontendCodeRequest):
    """Generate frontend code (HTML/CSS/JS) based on prompt"""
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        framework_templates = {
            'vanilla': 'vanilla HTML, CSS, and JavaScript',
            'react': 'React with hooks and modern JavaScript',
            'vue': 'Vue.js 3 with Composition API',
            'angular': 'Angular with TypeScript'
        }
        
        prompt = f"""Create a complete, working {framework_templates.get(request.framework, framework_templates['vanilla'])} application for:

{request.prompt}

Requirements:
1. Create a fully functional implementation
2. Use modern, clean code
3. Make it visually appealing with proper CSS
4. Ensure it's responsive
5. Add smooth animations/transitions where appropriate
6. Include all necessary HTML, CSS, and JavaScript in a single file (for vanilla) or component

For vanilla JS, provide a complete HTML file with embedded CSS and JavaScript.
For frameworks, provide the main component code.

Code:"""
        
        response = model.generate_content(prompt)
        code = response.text
        
        # Parse the response to extract HTML, CSS, and JS
        html_code = ""
        css_code = ""
        js_code = ""
        
        if request.framework == 'vanilla':
            # Extract complete HTML file
            if "```html" in code:
                start = code.find("```html") + 7
                end = code.find("```", start)
                html_code = code[start:end].strip()
            elif "<html" in code or "<!DOCTYPE" in code:
                # Try to extract HTML directly
                html_code = code
        else:
            # For frameworks, return the component code
            if "```" in code:
                parts = code.split("```")
                for i, part in enumerate(parts):
                    if i % 2 == 1:  # Code blocks
                        html_code = part.strip()
                        break
        
        return {
            'framework': request.framework,
            'code': html_code,
            'description': f"Generated {request.framework} code for: {request.prompt}",
            'preview_available': request.framework == 'vanilla'
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws/execute")
async def websocket_execute(websocket: WebSocket):
    """WebSocket endpoint for real-time code execution"""
    await websocket.accept()
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            
            if data.get('type') == 'execute':
                # Execute code
                result = code_executor.execute_code(
                    data.get('code', ''),
                    data.get('language', 'python'),
                    data.get('input', '')
                )
                
                # Send result back
                await websocket.send_json({
                    'type': 'execution_result',
                    'result': result
                })
            
            elif data.get('type') == 'validate':
                # Validate code
                validation = code_executor.validate_code(
                    data.get('code', ''),
                    data.get('language', 'python')
                )
                
                await websocket.send_json({
                    'type': 'validation_result',
                    'result': validation
                })
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({
            'type': 'error',
            'message': str(e)
        })


@router.get("/supported-languages")
async def get_supported_languages():
    """Get list of supported programming languages"""
    return {
        'languages': code_executor.get_supported_languages(),
        'frontend_frameworks': ['vanilla', 'react', 'vue', 'angular']
    } 