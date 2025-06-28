from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
from app.services.gemini_service import gemini_service
from app.services.rag_service import answer_repo_question
from app.services.github_service import github_service

router = APIRouter()

class ChatMessage(BaseModel):
    role: str  # 'user' | 'assistant' | 'system'
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    repo_name: Optional[str] = None
    use_rag: Optional[bool] = False
    repo_owner: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    sources: Optional[List[Dict[str, Any]]] = None

class CodeAnalysisRequest(BaseModel):
    code: str
    language: Optional[str] = "python"
    analysis_type: Optional[str] = "full"  # 'full' | 'entities' | 'complexity' | 'patterns'

class CodeAnalysisResponse(BaseModel):
    entities: Optional[Dict[str, List[str]]] = None
    complexity: Optional[Dict[str, Any]] = None
    patterns: Optional[Dict[str, List[str]]] = None
    summary: Optional[str] = None
    keywords: Optional[List[List[str]]] = None
    quality_analysis: Optional[Dict[str, str]] = None

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """Chat with AI using Gemini and optional RAG"""
    try:
        # Convert Pydantic models to dict for Gemini service
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Get repository context if RAG is enabled
        repo_context = None
        sources = None
        
        if request.use_rag and request.repo_name and request.repo_owner:
            try:
                # Get repository files for RAG
                files = await github_service.get_repository_files(request.repo_owner, request.repo_name)
                
                # Get the last user message for RAG query
                last_user_message = None
                for msg in reversed(request.messages):
                    if msg.role == 'user':
                        last_user_message = msg.content
                        break
                
                if last_user_message:
                    # Use RAG to get relevant context
                    repo_context = answer_repo_question(
                        repo_name=f"{request.repo_owner}/{request.repo_name}",
                        files=files,
                        question=last_user_message
                    )
                    
                    # Create sources info for the response
                    sources = [{
                        "type": "repository_context",
                        "repo": f"{request.repo_owner}/{request.repo_name}",
                        "context_length": len(repo_context) if repo_context else 0
                    }]
                    
            except Exception as e:
                print(f"RAG error: {e}")
                repo_context = f"Repository context for {request.repo_owner}/{request.repo_name} (RAG failed: {str(e)})"
        
        response = await gemini_service.chat(messages, repo_context)
        
        return ChatResponse(
            response=response,
            sources=sources
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-code", response_model=CodeAnalysisResponse)
async def analyze_code(request: CodeAnalysisRequest):
    """Analyze code with NLP"""
    try:
        analysis = await gemini_service.analyze_code(request.code, request.language)
        
        return CodeAnalysisResponse(
            entities=analysis.get("entities", {}),
            complexity=analysis.get("complexity", {}),
            patterns=analysis.get("patterns", {}),
            summary=analysis.get("summary", ""),
            keywords=analysis.get("keywords", []),
            quality_analysis=analysis.get("quality_analysis", {})
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-code")
async def generate_code(request: dict):
    """Generate code using AI"""
    try:
        prompt = request.get("prompt", "")
        language = request.get("language", "python")
        context = request.get("context", "")
        
        generated_code = await gemini_service.generate_code(prompt, language, context)
        
        return {
            "code": generated_code,
            "language": language,
            "explanation": f"Generated {language} code based on your prompt."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/explain-code")
async def explain_code(request: dict):
    """Explain code using AI and NLP"""
    try:
        code = request.get("code", "")
        language = request.get("language", "python")
        
        explanation = await gemini_service.explain_code(code, language)
        
        return {
            "explanation": explanation,
            "language": language,
            "complexity": "moderate",
            "suggestions": ["Add more documentation", "Include error handling", "Consider unit tests"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 