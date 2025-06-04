from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from github import Github
from github.GithubException import GithubException
import os
import base64
from datetime import datetime

router = APIRouter()

class GitHubRepoRequest(BaseModel):
    username: str = Field(..., description="GitHub username")
    repositories: List[str] = Field(..., description="List of repository names to scrape")
    github_token: Optional[str] = Field(None, description="GitHub personal access token")

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

@router.post("/scrape", response_model=List[RepoStructure])
async def scrape_github_repos(request: GitHubRepoRequest):
    """Scrape GitHub repositories and analyze code structure"""
    try:
        # Use provided token or fall back to environment variable
        github_token = request.github_token or os.getenv("GITHUB_TOKEN")
        if not github_token:
            raise HTTPException(status_code=401, detail="GitHub token not provided")
        
        g = Github(github_token)
        results = []
        
        for repo_name in request.repositories:
            try:
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
                
                results.append(repo_structure)
                
            except GithubException as e:
                raise HTTPException(status_code=404, detail=f"Repository {repo_name} not found: {str(e)}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error processing {repo_name}: {str(e)}")
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/file-content")
async def get_file_content(
    username: str = Query(..., description="GitHub username"),
    repo: str = Query(..., description="Repository name"),
    file_path: str = Query(..., description="File path in repository"),
    github_token: Optional[str] = Query(None, description="GitHub token")
):
    """Get content of a specific file from GitHub repository"""
    try:
        token = github_token or os.getenv("GITHUB_TOKEN")
        if not token:
            raise HTTPException(status_code=401, detail="GitHub token not provided")
        
        g = Github(token)
        repository = g.get_repo(f"{username}/{repo}")
        
        try:
            file_content = repository.get_contents(file_path)
            if file_content.type == "file":
                content = base64.b64decode(file_content.content).decode('utf-8')
                return {
                    "path": file_path,
                    "content": content,
                    "size": file_content.size,
                    "language": get_file_language(file_path),
                    "encoding": file_content.encoding
                }
            else:
                raise HTTPException(status_code=400, detail="Path is not a file")
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"File not found: {str(e)}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze")
async def analyze_repository(request: GitHubRepoRequest):
    """Analyze repository code statistics"""
    try:
        github_token = request.github_token or os.getenv("GITHUB_TOKEN")
        if not github_token:
            raise HTTPException(status_code=401, detail="GitHub token not provided")
        
        g = Github(github_token)
        analysis_results = []
        
        for repo_name in request.repositories:
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
                        ext = os.path.splitext(content.name)[1]
                        if ext:
                            file_types[ext] = file_types.get(ext, 0) + 1
                        
                        # Count lines (for text files under 1MB)
                        if content.size < 1024 * 1024:  # 1MB limit
                            try:
                                file_content = repo.get_contents(content.path)
                                decoded = base64.b64decode(file_content.content).decode('utf-8')
                                total_lines += len(decoded.splitlines())
                            except:
                                pass
                    
                    elif content.type == "dir":
                        try:
                            sub_contents = repo.get_contents(content.path)
                            analyze_contents(sub_contents)
                        except:
                            pass
            
            analyze_contents(contents)
            
            analysis = CodeAnalysis(
                total_files=total_files,
                languages=languages,
                file_types=file_types,
                total_lines=total_lines,
                repo_info={
                    "name": repo.name,
                    "description": repo.description,
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count,
                    "language": repo.language,
                    "created_at": repo.created_at.isoformat(),
                    "updated_at": repo.updated_at.isoformat()
                }
            )
            
            analysis_results.append(analysis)
        
        return analysis_results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 