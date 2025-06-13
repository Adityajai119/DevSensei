from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from github import Github
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv
import base64
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.hybrid_engine import RAGEngine
from fastapi_cache.decorator import cache
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import asyncio
import time

load_dotenv()

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

# Initialize GitHub client
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN not found in environment variables")

github_client = Github(GITHUB_TOKEN)
rag_engine = RAGEngine(GEMINI_API_KEY) if GEMINI_API_KEY else None


class RepoRequest(BaseModel):
    owner: str
    repo: str
    branch: str = "main"
    index_for_rag: bool = True


class FileContent(BaseModel):
    path: str
    content: str
    size: int
    language: Optional[str] = None


class RepoInfo(BaseModel):
    name: str
    description: str
    stars: int
    forks: int
    language: str
    topics: List[str]
    default_branch: str


def get_file_language(filename: str) -> str:
    """Determine programming language from file extension"""
    ext_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.cs': 'csharp',
        '.rb': 'ruby',
        '.go': 'go',
        '.rs': 'rust',
        '.php': 'php',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.scala': 'scala',
        '.r': 'r',
        '.jsx': 'javascript',
        '.tsx': 'typescript',
        '.vue': 'vue',
        '.dart': 'dart'
    }
    
    _, ext = os.path.splitext(filename.lower())
    return ext_map.get(ext, 'text')


@router.post("/repo/info")
@cache(expire=300)  # 5 minutes cache
@limiter.limit("30/minute")  # 30 requests per minute
async def get_repo_info(request: Request, repo_request: RepoRequest):
    """Get basic information about a GitHub repository"""
    try:
        repo = github_client.get_repo(f"{repo_request.owner}/{repo_request.repo}")
        
        return RepoInfo(
            name=repo.name,
            description=repo.description or "",
            stars=repo.stargazers_count,
            forks=repo.forks_count,
            language=repo.language or "Unknown",
            topics=repo.get_topics(),
            default_branch=repo.default_branch
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/batch/repos-info")
@cache(expire=300)
@limiter.limit("10/minute")
async def batch_get_repos_info(request: Request, requests: List[RepoRequest]):
    """Get information for multiple repositories in parallel"""
    async def get_single_repo_info(repo_request: RepoRequest):
        try:
            repo = github_client.get_repo(f"{repo_request.owner}/{repo_request.repo}")
            return RepoInfo(
                name=repo.name,
                description=repo.description or "",
                stars=repo.stargazers_count,
                forks=repo.forks_count,
                language=repo.language or "Unknown",
                topics=repo.get_topics(),
                default_branch=repo.default_branch
            )
        except Exception as e:
            return {"error": str(e), "owner": repo_request.owner, "repo": repo_request.repo}

    # Process requests in parallel with a semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(5)  # Limit to 5 concurrent requests
    async def bounded_get_repo(repo_request):
        async with semaphore:
            return await get_single_repo_info(repo_request)

    tasks = [bounded_get_repo(repo_request) for repo_request in requests]
    results = await asyncio.gather(*tasks)
    return results


@router.post("/repo/files", response_model=List[FileContent])
async def get_repo_files(request: RepoRequest):
    """Get all code files from a repository and optionally index them for RAG"""
    try:
        print(f"Fetching files for repository: {request.owner}/{request.repo}")
        print(f"Branch: {request.branch}")
        print(f"Index for RAG: {request.index_for_rag}")
        
        repo = github_client.get_repo(f"{request.owner}/{request.repo}")
        print(f"Repository found: {repo.full_name}")
        
        contents = repo.get_contents("", ref=request.branch)
        print(f"Found {len(contents)} items in root directory")
        
        files = []
        files_for_rag = []
        
        # Process files recursively
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                print(f"Processing directory: {file_content.path}")
                contents.extend(repo.get_contents(file_content.path, ref=request.branch))
            else:
                # Filter for code files
                if file_content.path.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.c', 
                                             '.cs', '.rb', '.go', '.rs', '.php', '.swift',
                                             '.kt', '.scala', '.r', '.jsx', '.tsx', '.vue',
                                             '.dart', '.md', '.yml', '.yaml', '.json')):
                    try:
                        # Decode file content
                        content = base64.b64decode(file_content.content).decode('utf-8')
                        language = get_file_language(file_content.path)
                        
                        file_data = FileContent(
                            path=file_content.path,
                            content=content,
                            size=file_content.size,
                            language=language
                        )
                        files.append(file_data)
                        
                        # Prepare for RAG indexing
                        files_for_rag.append({
                            'path': file_content.path,
                            'content': content,
                            'language': language
                        })
                        
                        print(f"Processed file: {file_content.path}")
                        
                    except Exception as e:
                        print(f"Error processing file {file_content.path}: {e}")
        
        print(f"Total files processed: {len(files)}")
        
        # Index files in RAG if requested
        if request.index_for_rag and rag_engine and files_for_rag:
            try:
                print(f"Indexing {len(files_for_rag)} files for RAG")
                rag_engine.index_code(f"{request.owner}/{request.repo}", files_for_rag)
                print("RAG indexing completed")
            except Exception as e:
                print(f"Error indexing files for RAG: {e}")
        
        return files
        
    except Exception as e:
        print(f"Error in get_repo_files: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/repo/structure")
async def get_repo_structure(request: RepoRequest):
    """Get the directory structure of a repository"""
    try:
        repo = github_client.get_repo(f"{request.owner}/{request.repo}")
        
        def build_tree(contents, level=0):
            tree = []
            for content in sorted(contents, key=lambda x: (x.type != "dir", x.name)):
                indent = "  " * level
                if content.type == "dir":
                    tree.append(f"{indent}📁 {content.name}/")
                    # Get subdirectory contents
                    sub_contents = repo.get_contents(content.path, ref=request.branch)
                    tree.extend(build_tree(sub_contents, level + 1))
                else:
                    # Determine file icon based on extension
                    icon = "📄"
                    if content.name.endswith(('.py', '.pyw')):
                        icon = "🐍"
                    elif content.name.endswith(('.js', '.jsx', '.ts', '.tsx')):
                        icon = "📜"
                    elif content.name.endswith(('.md', '.markdown')):
                        icon = "📝"
                    elif content.name.endswith(('.json', '.yml', '.yaml')):
                        icon = "⚙️"
                    
                    tree.append(f"{indent}{icon} {content.name}")
            return tree
        
        contents = repo.get_contents("", ref=request.branch)
        tree_structure = build_tree(contents)
        
        return {
            "repository": f"{request.owner}/{request.repo}",
            "branch": request.branch,
            "structure": tree_structure
        }
        
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/user/repos")
async def get_user_repos(username: str):
    """Get all repositories for a GitHub user"""
    try:
        user = github_client.get_user(username)
        repos = []
        
        for repo in user.get_repos():
            repos.append({
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description,
                "language": repo.language,
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "private": repo.private,
                "default_branch": repo.default_branch,
                "url": repo.html_url
            })
        
        return {
            "username": username,
            "total_repos": len(repos),
            "repositories": repos
        }
        
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/repo/search-code")
async def search_code_in_repo(repo_name: str, query: str, k: int = 5):
    """Search for code in an indexed repository using RAG"""
    if not rag_engine:
        raise HTTPException(status_code=500, detail="RAG engine not initialized")
    
    try:
        results = rag_engine.search_code(repo_name, query, k)
        return {
            "query": query,
            "repository": repo_name,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 