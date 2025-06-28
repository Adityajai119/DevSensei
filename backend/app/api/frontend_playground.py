from fastapi import APIRouter, Body
from pydantic import BaseModel
from app.services.gemini_service import gemini_service

router = APIRouter()

class GenerateFrontendRequest(BaseModel):
    stack: str
    prompt: str

class RunFrontendRequest(BaseModel):
    stack: str
    code: str

@router.post("/generate")
async def generate_frontend_code(request: GenerateFrontendRequest):
    """Generate frontend code using AI"""
    try:
        code = await gemini_service.generate_frontend(request.prompt, request.stack)
        return {"code": code, "stack": request.stack}
    except Exception as e:
        return {"error": str(e), "code": "", "stack": request.stack}

@router.post("/run")
async def run_frontend_code(request: RunFrontendRequest):
    """Run frontend code (returns the code for now)"""
    # For now, just return the code. In production, run in a secure sandbox/iframe.
    return {"output": request.code, "stack": request.stack} 