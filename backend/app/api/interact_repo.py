from fastapi import APIRouter, Body
from pydantic import BaseModel
from typing import Optional
from app.services.github_service import github_service
from app.services.pdf_service import pdf_service
from app.services.gemini_service import gemini_service
from app.services.rag_service import answer_repo_question

router = APIRouter()

class ListReposRequest(BaseModel):
    username: str

class GeneratePDFRequest(BaseModel):
    owner: str
    repo_name: str

class ChatWithRepoRequest(BaseModel):
    owner: str
    repo_name: str
    question: str
    file: Optional[str] = None

@router.post("/list")
async def list_repos(request: ListReposRequest):
    """List repositories for a GitHub user"""
    try:
        repos = await github_service.get_user_repositories(request.username)
        return {"repos": repos, "username": request.username}
    except Exception as e:
        return {"error": str(e), "repos": [], "username": request.username}

@router.post("/pdf")
async def generate_pdf(request: GeneratePDFRequest):
    """Generate PDF documentation for a repository"""
    try:
        # Get repository info and files
        repo_info = await github_service.get_repository_info(request.owner, request.repo_name)
        files = await github_service.get_repository_files(request.owner, request.repo_name)
        structure = await github_service.get_repository_structure(request.owner, request.repo_name)
        
        # Generate PDF
        output_path = f"static/pdfs/{request.owner}_{request.repo_name}_documentation.pdf"
        pdf_path = pdf_service.generate_repository_documentation(
            repo_info=repo_info,
            files=files,
            structure=structure,
            output_path=output_path
        )
        
        return {"pdf_url": f"/static/pdfs/{request.owner}_{request.repo_name}_documentation.pdf"}
    except Exception as e:
        return {"error": str(e)}

@router.post("/chat")
async def chat_with_repo(request: ChatWithRepoRequest):
    """Chat with a repository using RAG or general AI"""
    try:
        # Get repository files for context
        files = await github_service.get_repository_files(request.owner, request.repo_name)
        
        if request.file:
            # Use RAG for specific file questions
            answer = answer_repo_question(
                repo_name=f"{request.owner}/{request.repo_name}",
                files=files,
                question=request.question
            )
        else:
            # Use general AI for repo questions
            repo_info = await github_service.get_repository_info(request.owner, request.repo_name)
            context = f"Repository: {request.owner}/{request.repo_name}\nDescription: {repo_info.get('description', 'No description')}"
            answer = await gemini_service.chat([{"role": "user", "content": f"Context: {context}\nQuestion: {request.question}"}])
        
        return {"answer": answer, "repo": f"{request.owner}/{request.repo_name}"}
    except Exception as e:
        return {"error": str(e), "answer": "Sorry, I couldn't process your question."} 