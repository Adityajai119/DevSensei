from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.services.github_service import github_service

router = APIRouter()

class RepoRequest(BaseModel):
    owner: str
    repo: str
    branch: Optional[str] = None
    index_for_rag: Optional[bool] = False

class RepoInfo(BaseModel):
    name: str
    description: str
    stars: int
    forks: int
    language: str
    topics: List[str]
    default_branch: str

class FileContent(BaseModel):
    path: str
    content: str
    size: int
    language: Optional[str] = None

class RepositoryInfo(BaseModel):
    name: str
    full_name: str
    description: Optional[str]
    language: Optional[str]
    stars: int
    forks: int
    url: str
    default_branch: str
    topics: List[str]

class RepositorySearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 10

class RepositorySearchResponse(BaseModel):
    repositories: List[RepositoryInfo]
    total_count: int

class UserRepositoriesRequest(BaseModel):
    username: str

class UserRepositoriesResponse(BaseModel):
    repositories: List[RepositoryInfo]
    username: str

class RepositoryDetailRequest(BaseModel):
    owner: str
    repo_name: str

class RepositoryDetailResponse(BaseModel):
    repository: Dict[str, Any]
    files: List[Dict[str, Any]]
    structure: Dict[str, Any]

@router.post("/repo/info", response_model=RepoInfo)
async def get_repo_info(request: RepoRequest):
    """Get repository information"""
    try:
        # Mock repository info - replace with actual GitHub API integration
        return RepoInfo(
            name=request.repo,
            description=f"Sample repository: {request.repo}",
            stars=150,
            forks=25,
            language="Python",
            topics=["python", "api", "web"],
            default_branch=request.branch or "main"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/repo/files", response_model=List[FileContent])
async def get_repo_files(request: RepoRequest):
    """Get repository files and index for RAG"""
    try:
        files = await github_service.get_repository_files(request.owner, request.repo, request.branch or "main")
        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/repo/structure")
async def get_repo_structure(request: RepoRequest):
    """Get repository structure"""
    try:
        structure = await github_service.get_repository_structure(request.owner, request.repo)
        return structure
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/repo/search-code")
async def search_code_in_repo(request: dict):
    """Search code in indexed repository"""
    try:
        repo_name = request.get("repo_name", "")
        query = request.get("query", "")
        k = request.get("k", 5)
        
        # Mock search results - replace with actual search implementation
        results = [
            {
                "file_path": "src/main.py",
                "line_number": 15,
                "content": f"Found '{query}' in main.py",
                "score": 0.95
            },
            {
                "file_path": "src/utils.py",
                "line_number": 8,
                "content": f"Another occurrence of '{query}' in utils.py",
                "score": 0.87
            }
        ]
        
        return {
            "results": results[:k],
            "total_found": len(results),
            "query": query,
            "repo_name": repo_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/repos")
async def get_user_repos(username: str = Query(...)):
    """Get user repositories"""
    try:
        repos = await github_service.get_user_repositories(username)
        return {
            "username": username,
            "repositories": repos,
            "total_count": len(repos)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search", response_model=RepositorySearchResponse)
async def search_repositories(request: RepositorySearchRequest):
    """Search repositories using GitHub API"""
    try:
        repositories = await github_service.search_repositories(request.query, request.limit)
        
        # Convert to RepositoryInfo models
        repo_infos = []
        for repo in repositories:
            repo_infos.append(RepositoryInfo(
                name=repo["name"],
                full_name=repo["full_name"],
                description=repo.get("description"),
                language=repo.get("language"),
                stars=repo.get("stars", 0),
                forks=repo.get("forks", 0),
                url=repo["url"],
                default_branch=repo.get("default_branch", "main"),
                topics=repo.get("topics", [])
            ))
        
        return RepositorySearchResponse(
            repositories=repo_infos,
            total_count=len(repo_infos)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/user-repos", response_model=UserRepositoriesResponse)
async def get_user_repositories(request: UserRepositoriesRequest):
    """Get repositories for a specific user"""
    try:
        repositories = await github_service.get_user_repositories(request.username)
        
        # Convert to RepositoryInfo models
        repo_infos = []
        for repo in repositories:
            repo_infos.append(RepositoryInfo(
                name=repo["name"],
                full_name=repo["full_name"],
                description=repo.get("description"),
                language=repo.get("language"),
                stars=repo.get("stars", 0),
                forks=repo.get("forks", 0),
                url=repo["url"],
                default_branch=repo.get("default_branch", "main"),
                topics=repo.get("topics", [])
            ))
        
        return UserRepositoriesResponse(
            repositories=repo_infos,
            username=request.username
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/repository-detail", response_model=RepositoryDetailResponse)
async def get_repository_detail(request: RepositoryDetailRequest):
    """Get detailed repository information including files and structure"""
    try:
        # Get repository info
        repo_info = await github_service.get_repository_info(request.owner, request.repo_name)
        
        # Get repository files
        files = await github_service.get_repository_files(request.owner, request.repo_name)
        
        # Get repository structure
        structure = await github_service.get_repository_structure(request.owner, request.repo_name)
        
        return RepositoryDetailResponse(
            repository=repo_info,
            files=files,
            structure=structure
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/repository/{owner}/{repo_name}/files")
async def get_repository_files(owner: str, repo_name: str, path: str = ""):
    """Get files from a specific repository path"""
    try:
        files = await github_service.get_repository_files(owner, repo_name, path)
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/repository/{owner}/{repo_name}/structure")
async def get_repository_structure(owner: str, repo_name: str):
    """Get repository directory structure"""
    try:
        structure = await github_service.get_repository_structure(owner, repo_name)
        return structure
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 