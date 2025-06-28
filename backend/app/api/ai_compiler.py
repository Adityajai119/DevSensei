from fastapi import APIRouter, Body
from pydantic import BaseModel
from app.services.gemini_service import gemini_service
from app.services.compiler_service import run_code

router = APIRouter()

class GenerateCodeRequest(BaseModel):
    language: str
    prompt: str

class RunCodeRequest(BaseModel):
    language: str
    code: str

@router.post("/generate")
async def generate_code_endpoint(request: GenerateCodeRequest):
    """Generate code using AI"""
    try:
        code = await gemini_service.generate_code(request.prompt, request.language)
        return {"code": code, "language": request.language}
    except Exception as e:
        return {"error": str(e), "code": "", "language": request.language}

@router.post("/run")
async def run_code_endpoint(request: RunCodeRequest):
    """Run generated code"""
    try:
        output = run_code(request.language, request.code)
        return {"output": output, "language": request.language}
    except Exception as e:
        return {"error": str(e), "output": "", "language": request.language} 