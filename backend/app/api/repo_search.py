from fastapi import APIRouter, Body
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.services.github_service import github_service
from app.services.gemini_service import gemini_service

router = APIRouter()

class RepoSearchRequest(BaseModel):
    prompt: str
    limit: Optional[int] = 10

@router.post("")
async def repo_search(request: RepoSearchRequest):
    """Search repositories using GitHub API and enhance with AI"""
    try:
        # Search repositories using GitHub API
        repos = await github_service.search_repositories(request.prompt, request.limit)
        
        # Generate AI-enhanced response
        ai_prompt = f"Based on the search query '{request.prompt}', here are some repositories: {repos}. Provide a helpful summary and recommendations."
        ai_response = await gemini_service.chat([{"role": "user", "content": ai_prompt}])
        
        return {
            "response": ai_response,
            "repos": repos,
            "query": request.prompt
        }
    except Exception as e:
        return {
            "response": f"Error searching repositories: {str(e)}",
            "repos": [],
            "query": request.prompt
        } 