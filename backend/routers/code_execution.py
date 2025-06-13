from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
import google.generativeai as genai
import os
from dotenv import load_dotenv
import sys
import json
import asyncio
import time
from fastapi.security import APIKeyHeader
from fastapi.responses import JSONResponse
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.code_executor import CodeExecutor
from core.nlp_processor import NLPProcessor

load_dotenv()

router = APIRouter()

# Initialize services
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

# Rate limiting
RATE_LIMIT = 100  # requests per minute
rate_limit_store = {}
last_cleanup = time.time()

# API key header
api_key_header = APIKeyHeader(name="X-API-Key")

# Initialize services with error handling
try:
    genai.configure(api_key=GEMINI_API_KEY)
    code_executor = CodeExecutor(timeout=30, max_memory=512)  # 30 seconds timeout, 512MB memory limit
    nlp_processor = NLPProcessor()
except Exception as e:
    print(f"Error initializing services: {str(e)}")
    raise

class CodeExecutionRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=100000)  # 100KB limit
    language: str = Field(..., min_length=1, max_length=50)
    input_data: Optional[str] = Field(None, max_length=10000)  # 10KB limit
    
    @validator('code')
    def validate_code(cls, v):
        if len(v) > 100000:  # 100KB
            raise ValueError("Code exceeds maximum length of 100KB")
        return v
    
    @validator('language')
    def validate_language(cls, v):
        supported_languages = code_executor.get_supported_languages()
        if v.lower() not in supported_languages:
            raise ValueError(f"Unsupported language. Supported languages: {', '.join(supported_languages)}")
        return v.lower()

class CodeGenerationRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=5000)  # 5KB limit
    language: str = Field("python", min_length=1, max_length=50)
    context: Optional[str] = Field(None, max_length=10000)  # 10KB limit
    
    @validator('language')
    def validate_language(cls, v):
        supported_languages = code_executor.get_supported_languages()
        if v.lower() not in supported_languages:
            raise ValueError(f"Unsupported language. Supported languages: {', '.join(supported_languages)}")
        return v.lower()

class CodeOptimizationRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=100000)  # 100KB limit
    language: str = Field(..., min_length=1, max_length=50)
    optimization_type: str = Field("performance", pattern="^(performance|memory|readability)$")
    
    @validator('language')
    def validate_language(cls, v):
        supported_languages = code_executor.get_supported_languages()
        if v.lower() not in supported_languages:
            raise ValueError(f"Unsupported language. Supported languages: {', '.join(supported_languages)}")
        return v.lower()

class CodeDebugRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=100000)  # 100KB limit
    language: str = Field(..., min_length=1, max_length=50)
    error_message: Optional[str] = Field(None, max_length=1000)
    expected_output: Optional[str] = Field(None, max_length=1000)
    
    @validator('language')
    def validate_language(cls, v):
        supported_languages = code_executor.get_supported_languages()
        if v.lower() not in supported_languages:
            raise ValueError(f"Unsupported language. Supported languages: {', '.join(supported_languages)}")
        return v.lower()

class FrontendCodeRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=5000)  # 5KB limit
    framework: str = Field("vanilla", pattern="^(vanilla|react|vue|angular)$")

async def check_rate_limit(api_key: str = Depends(api_key_header)):
    """Check and update rate limit for the API key"""
    global last_cleanup
    
    # Clean up old entries every minute
    current_time = time.time()
    if current_time - last_cleanup > 60:
        rate_limit_store.clear()
        last_cleanup = current_time
    
    # Get or initialize rate limit data
    if api_key not in rate_limit_store:
        rate_limit_store[api_key] = {
            'count': 0,
            'reset_time': current_time + 60
        }
    
    # Check if rate limit is exceeded
    data = rate_limit_store[api_key]
    if current_time > data['reset_time']:
        data['count'] = 0
        data['reset_time'] = current_time + 60
    
    if data['count'] >= RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again in a minute."
        )
    
    data['count'] += 1
    return api_key

@router.post("/execute")
async def execute_code(
    request: CodeExecutionRequest,
    api_key: str = Depends(check_rate_limit)
):
    """Execute code in the specified language"""
    try:
        # Validate code first
        validation = code_executor.validate_code(request.code, request.language)
        if validation['status'] != 'valid':
            return JSONResponse(
                status_code=400,
                content={
                    'output': '',
                    'error': f"Validation error: {', '.join(validation['errors'])}",
                    'execution_time': 0,
                    'status': 'validation_error'
                }
            )
        
        # Execute the code
        result = code_executor.execute_code(
            request.code,
            request.language,
            request.input_data or ""
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate")
async def generate_code(
    request: CodeGenerationRequest,
    api_key: str = Depends(check_rate_limit)
):
    """Generate code based on prompt"""
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        
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
        
        # Validate generated code
        validation = code_executor.validate_code(code, request.language)
        if validation['status'] != 'valid':
            return JSONResponse(
                status_code=400,
                content={
                    'code': code,
                    'error': f"Generated code validation error: {', '.join(validation['errors'])}",
                    'status': 'validation_error'
                }
            )
        
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
async def optimize_code(
    request: CodeOptimizationRequest,
    api_key: str = Depends(check_rate_limit)
):
    """Optimize code for performance, memory, or readability"""
    try:
        # Validate input code
        validation = code_executor.validate_code(request.code, request.language)
        if validation['status'] != 'valid':
            return JSONResponse(
                status_code=400,
                content={
                    'error': f"Input code validation error: {', '.join(validation['errors'])}",
                    'status': 'validation_error'
                }
            )
        
        model = genai.GenerativeModel('gemini-2.0-flash')
        
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
        
        # Validate optimized code
        validation = code_executor.validate_code(optimized_code, request.language)
        if validation['status'] != 'valid':
            return JSONResponse(
                status_code=400,
                content={
                    'error': f"Optimized code validation error: {', '.join(validation['errors'])}",
                    'status': 'validation_error'
                }
            )
        
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
async def debug_code(
    request: CodeDebugRequest,
    api_key: str = Depends(check_rate_limit)
):
    """Debug code and provide fixes"""
    try:
        # Validate input code
        validation = code_executor.validate_code(request.code, request.language)
        if validation['status'] != 'valid':
            return JSONResponse(
                status_code=400,
                content={
                    'error': f"Input code validation error: {', '.join(validation['errors'])}",
                    'status': 'validation_error'
                }
            )
        
        model = genai.GenerativeModel('gemini-2.0-flash')
        
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
        
        # Validate fixed code
        validation = code_executor.validate_code(fixed_code, request.language)
        if validation['status'] != 'valid':
            return JSONResponse(
                status_code=400,
                content={
                    'error': f"Fixed code validation error: {', '.join(validation['errors'])}",
                    'status': 'validation_error'
                }
            )
        
        return {
            'original_code': request.code,
            'fixed_code': fixed_code,
            'explanation': debug_explanation,
            'error_message': request.error_message,
            'expected_output': request.expected_output
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/ws/execute")
async def websocket_execute(websocket: WebSocket):
    """WebSocket endpoint for real-time code execution"""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            
            # Validate input
            if not isinstance(data, dict) or 'code' not in data or 'language' not in data:
                await websocket.send_json({
                    'error': 'Invalid request format',
                    'status': 'error'
                })
                continue
            
            # Execute code
            try:
                result = code_executor.execute_code(
                    data['code'],
                    data['language'],
                    data.get('input_data', '')
                )
                await websocket.send_json(result)
            except Exception as e:
                await websocket.send_json({
                    'error': str(e),
                    'status': 'error'
                })
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({
            'error': str(e),
            'status': 'error'
        })

@router.get("/supported-languages")
async def get_supported_languages():
    """Get list of supported programming languages"""
    return {
        'languages': code_executor.get_supported_languages()
    } 