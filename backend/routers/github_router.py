from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional
from github import Github
from github.GithubException import GithubException, RateLimitExceededException
import os
import base64
from datetime import datetime, timedelta
import google.generativeai as genai
from core.hybrid_engine import RAGEngine
import time
from fastapi.security import APIKeyHeader
from fastapi.responses import JSONResponse
import asyncio
from functools import lru_cache

router = APIRouter()

# Initialize RAG engine
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

# Rate limiting
RATE_LIMIT = 60  # requests per minute
rate_limit_store = {}
last_cleanup = time.time()

# API key header
api_key_header = APIKeyHeader(name="X-API-Key")

# Cache settings
CACHE_TTL = 3600  # 1 hour
repo_cache = {}
file_cache = {}

# Initialize services with error handling
try:
    genai.configure(api_key=GEMINI_API_KEY)
    rag_engine = RAGEngine(GEMINI_API_KEY)
except Exception as e:
    print(f"Error initializing services: {str(e)}")
    raise

class GitHubRepoRequest(BaseModel):
    username: str
    repositories: List[str]
    github_token: Optional[str] = None
    
    @validator('repositories')
    def validate_repositories(cls, v):
        if len(v) > 10:
            raise ValueError("Maximum 10 repositories allowed per request")
        return v

class FileInfo(BaseModel):
    path: str
    name: str
    size: int
    type: str
    language: Optional[str] = None
    content: Optional[str] = None
    last_modified: Optional[datetime] = None

class RepoStructure(BaseModel):
    name: str
    description: Optional[str]
    stars: int
    language: Optional[str]
    files: List[FileInfo]
    structure: Dict

class CodeAnalysis(BaseModel):
    total_files: int
    languages: Dict[str, int]
    file_types: Dict[str, int]
    total_lines: int
    repo_info: Dict

class ChatRequest(BaseModel):
    username: str
    repo: str
    query: str
    github_token: Optional[str] = None

def get_file_language(filename: str) -> Optional[str]:
    """Determine programming language from file extension"""
    extensions = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.ts': 'TypeScript',
        '.jsx': 'React',
        '.tsx': 'TypeScript React',
        '.java': 'Java',
        '.cpp': 'C++',
        '.c': 'C',
        '.cs': 'C#',
        '.go': 'Go',
        '.rs': 'Rust',
        '.php': 'PHP',
        '.rb': 'Ruby',
        '.swift': 'Swift',
        '.kt': 'Kotlin',
        '.html': 'HTML',
        '.css': 'CSS',
        '.scss': 'SCSS',
        '.sql': 'SQL',
        '.md': 'Markdown',
        '.json': 'JSON',
        '.xml': 'XML',
        '.yaml': 'YAML',
        '.yml': 'YAML'
    }
    
    for ext, lang in extensions.items():
        if filename.lower().endswith(ext):
            return lang
    return None

def build_tree_structure(contents, g, repo, path=""):
    """Recursively build tree structure of repository"""
    structure = {}
    
    for content in contents:
        if content.type == "dir":
            try:
                sub_contents = repo.get_contents(content.path)
                structure[content.name] = {
                    "type": "directory",
                    "children": build_tree_structure(sub_contents, g, repo, content.path)
                }
            except:
                structure[content.name] = {"type": "directory", "children": {}}
        else:
            structure[content.name] = {
                "type": "file",
                "size": content.size,
                "language": get_file_language(content.name)
            }
    
    return structure

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

def get_github_client(token: Optional[str] = None) -> Github:
    """Get GitHub client with proper error handling"""
    try:
        token = token or os.getenv("GITHUB_TOKEN")
        if not token:
            raise HTTPException(status_code=401, detail="GitHub token not provided")
        
        return Github(token)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initializing GitHub client: {str(e)}")

@lru_cache(maxsize=100)
def get_cached_repo(username: str, repo_name: str, token: str) -> Dict:
    """Get cached repository data"""
    cache_key = f"{username}/{repo_name}"
    if cache_key in repo_cache:
        cache_data = repo_cache[cache_key]
        if time.time() - cache_data['timestamp'] < CACHE_TTL:
            return cache_data['data']
    return None

def cache_repo(username: str, repo_name: str, data: Dict):
    """Cache repository data"""
    cache_key = f"{username}/{repo_name}"
    repo_cache[cache_key] = {
        'data': data,
        'timestamp': time.time()
    }

@router.post("/scrape", response_model=List[RepoStructure])
async def scrape_github_repos(request: GitHubRepoRequest):
    """Scrape GitHub repositories and analyze code structure"""
    try:
        github_token = request.github_token or os.getenv("GITHUB_TOKEN")
        g = get_github_client(github_token)
        results = []
        
        for repo_name in request.repositories:
            try:
                # Check cache first
                cached_data = get_cached_repo(request.username, repo_name, request.github_token or "")
                if cached_data:
                    results.append(cached_data)
                    continue
                
                # Get repository
                repo = g.get_repo(f"{request.username}/{repo_name}")
                
                # Get repository contents
                contents = repo.get_contents("")
                files = []
                
                # Build tree structure
                tree_structure = build_tree_structure(contents, g, repo)
                
                # Collect file information
                def collect_files(contents, path=""):
                    for content in contents:
                        if content.type == "file":
                            file_info = FileInfo(
                                path=content.path,
                                name=content.name,
                                size=content.size,
                                type=content.type,
                                language=get_file_language(content.name)
                            )
                            files.append(file_info)
                        elif content.type == "dir":
                            try:
                                sub_contents = repo.get_contents(content.path)
                                collect_files(sub_contents, content.path)
                            except:
                                pass
                
                collect_files(contents)
                
                # Create repository structure
                repo_structure = RepoStructure(
                    name=repo.name,
                    description=repo.description,
                    stars=repo.stargazers_count,
                    language=repo.language,
                    files=files,
                    structure=tree_structure
                )
                
                # Cache the result
                cache_repo(request.username, repo_name, repo_structure.dict())
                
                results.append(repo_structure)
                
            except RateLimitExceededException:
                raise HTTPException(
                    status_code=429,
                    detail="GitHub API rate limit exceeded. Please try again later."
                )
            except GithubException as e:
                raise HTTPException(status_code=404, detail=f"Repository {repo_name} not found: {str(e)}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error processing {repo_name}: {str(e)}")
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/file-content")
async def get_file_content(
    username: str = Query(...),
    repo: str = Query(...),
    file_path: str = Query(...),
    github_token: Optional[str] = Query(None),
    api_key: str = Depends(check_rate_limit)
):
    """Get content of a specific file from GitHub repository"""
    try:
        token = github_token or os.getenv("GITHUB_TOKEN")
        g = get_github_client(token)
        
        # Check cache first
        cache_key = f"{username}/{repo}/{file_path}"
        if cache_key in file_cache:
            cache_data = file_cache[cache_key]
            if time.time() - cache_data['timestamp'] < CACHE_TTL:
                return cache_data['data']
        
        repository = g.get_repo(f"{username}/{repo}")
        
        try:
            file_content = repository.get_contents(file_path)
            if file_content.type == "file":
                content = base64.b64decode(file_content.content).decode('utf-8')
                result = {
                    "path": file_path,
                    "content": content,
                    "size": file_content.size,
                    "language": get_file_language(file_path),
                    "encoding": file_content.encoding
                }
                
                # Cache the result
                file_cache[cache_key] = {
                    'data': result,
                    'timestamp': time.time()
                }
                
                return result
            else:
                raise HTTPException(status_code=400, detail="Path is not a file")
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"File not found: {str(e)}")
            
    except RateLimitExceededException:
        raise HTTPException(
            status_code=429,
            detail="GitHub API rate limit exceeded. Please try again later."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze")
async def analyze_repository(request: GitHubRepoRequest):
    """Analyze repository code statistics"""
    try:
        github_token = request.github_token or os.getenv("GITHUB_TOKEN")
        g = get_github_client(github_token)
        analysis_results = []
        
        for repo_name in request.repositories:
            try:
                # Get repository
                repo = g.get_repo(f"{request.username}/{repo_name}")
                
                # Initialize counters
                languages = {}
                file_types = {}
                total_files = 0
                total_lines = 0
                
                # Analyze repository
                contents = repo.get_contents("")
                
                def analyze_contents(contents):
                    nonlocal total_files, total_lines
                    
                    for content in contents:
                        if content.type == "file":
                            total_files += 1
                            
                            # Count by language
                            lang = get_file_language(content.name)
                            if lang:
                                languages[lang] = languages.get(lang, 0) + 1
                            
                            # Count by file type
                            ext = os.path.splitext(content.name)[1].lower()
                            if ext:
                                file_types[ext] = file_types.get(ext, 0) + 1
                            
                            # Count lines
                            try:
                                content_str = base64.b64decode(content.content).decode('utf-8')
                                total_lines += len(content_str.splitlines())
                            except:
                                pass
                                
                        elif content.type == "dir":
                            try:
                                sub_contents = repo.get_contents(content.path)
                                analyze_contents(sub_contents)
                            except:
                                pass
                
                analyze_contents(contents)
                
                # Create analysis result
                analysis = CodeAnalysis(
                    total_files=total_files,
                    languages=languages,
                    file_types=file_types,
                    total_lines=total_lines,
                    repo_info={
                        'name': repo.name,
                        'description': repo.description,
                        'stars': repo.stargazers_count,
                        'language': repo.language,
                        'size': repo.size,
                        'created_at': repo.created_at.isoformat(),
                        'updated_at': repo.updated_at.isoformat()
                    }
                )
                
                analysis_results.append(analysis)
                
            except RateLimitExceededException:
                raise HTTPException(
                    status_code=429,
                    detail="GitHub API rate limit exceeded. Please try again later."
                )
            except GithubException as e:
                raise HTTPException(status_code=404, detail=f"Repository {repo_name} not found: {str(e)}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error processing {repo_name}: {str(e)}")
        
        return analysis_results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat-with-repo")
async def chat_with_repository(request: ChatRequest):
    """Chat with repository using RAG"""
    try:
        token = request.github_token or os.getenv("GITHUB_TOKEN")
        g = get_github_client(token)
        
        # Get repository
        repo = g.get_repo(f"{request.username}/{request.repo}")
        
        # Collect repository content
        contents = repo.get_contents("")
        
        def collect_content(contents, path=""):
            content_list = []
            for content in contents:
                if content.type == "file":
                    try:
                        content_str = base64.b64decode(content.content).decode('utf-8')
                        content_list.append({
                            'path': content.path,
                            'content': content_str,
                            'language': get_file_language(content.name)
                        })
                    except:
                        pass
                elif content.type == "dir":
                    try:
                        sub_contents = repo.get_contents(content.path)
                        content_list.extend(collect_content(sub_contents, content.path))
                    except:
                        pass
            return content_list
        
        # Get all content
        all_content = collect_content(contents)
        
        # Use RAG to answer the query
        response = rag_engine.query(request.query, all_content)
        
        return {
            'query': request.query,
            'response': response,
            'repo': request.repo,
            'username': request.username
        }
        
    except RateLimitExceededException:
        raise HTTPException(
            status_code=429,
            detail="GitHub API rate limit exceeded. Please try again later."
        )
    except GithubException as e:
        raise HTTPException(status_code=404, detail=f"Repository {request.repo} not found: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/repos")
async def get_user_repos(
    username: str = Query(...),
    github_token: Optional[str] = Query(None),
    api_key: str = Depends(check_rate_limit)
):
    """Fetch repositories for a given GitHub username"""
    g = get_github_client(github_token)
    try:
        user = g.get_user(username)
        repos = user.get_repos()
        return [{"name": repo.name, "description": repo.description, "stars": repo.stargazers_count, "language": repo.language} for repo in repos]
    except GithubException as e:
        raise HTTPException(status_code=e.status, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching repositories: {str(e)}") 