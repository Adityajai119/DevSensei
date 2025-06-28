from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import os
from app.services.pdf_service import pdf_service
from app.services.github_service import github_service

router = APIRouter()

class DocumentationRequest(BaseModel):
    owner: str
    repo: str
    branch: Optional[str] = None
    include_setup: Optional[bool] = True
    include_architecture: Optional[bool] = True
    include_codebase_map: Optional[bool] = True

class CodebaseMapRequest(BaseModel):
    owner: str
    repo: str
    branch: Optional[str] = None

class GeneratePDFRequest(BaseModel):
    owner: str
    repo_name: str
    include_code: Optional[bool] = True
    include_api: Optional[bool] = True
    include_examples: Optional[bool] = True

class GeneratePDFResponse(BaseModel):
    pdf_url: str
    message: str
    file_size: Optional[int] = None

@router.post("/generate-project-docs")
async def generate_project_docs(request: DocumentationRequest):
    """Generate project documentation with PDF"""
    try:
        # Mock documentation generation - replace with actual implementation
        docs_content = f"""# {request.repo} Documentation

## Project Overview
This is a sample documentation for the {request.repo} repository.

## Setup Instructions
{f"### Installation\n```bash\ngit clone https://github.com/{request.owner}/{request.repo}.git\ncd {request.repo}\npip install -r requirements.txt\n```" if request.include_setup else ""}

## Architecture
{f"### System Design\nThis project follows a modular architecture with clear separation of concerns." if request.include_architecture else ""}

## Codebase Map
{f"### File Structure\n- src/: Source code\n- tests/: Test files\n- docs/: Documentation\n- config/: Configuration files" if request.include_codebase_map else ""}

## API Reference
### Endpoints
- GET /api/health - Health check
- POST /api/data - Create data
- GET /api/data/{id} - Get data by ID

## Contributing
Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License
This project is licensed under the MIT License.
"""
        
        return {
            "documentation": docs_content,
            "pdf_url": f"/static/docs/{request.owner}_{request.repo}_docs.pdf",
            "repo_name": request.repo,
            "owner": request.owner,
            "generated_at": "2024-01-01T00:00:00Z",
            "sections_included": {
                "setup": request.include_setup,
                "architecture": request.include_architecture,
                "codebase_map": request.include_codebase_map
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-codebase-map")
async def generate_codebase_map(request: CodebaseMapRequest):
    """Generate codebase map"""
    try:
        # Mock codebase map generation - replace with actual implementation
        codebase_map = {
            "repo_name": request.repo,
            "owner": request.owner,
            "branch": request.branch or "main",
            "structure": {
                "root": {
                    "type": "directory",
                    "path": "/",
                    "children": {
                        "src": {
                            "type": "directory",
                            "path": "/src",
                            "children": {
                                "main.py": {
                                    "type": "file",
                                    "path": "/src/main.py",
                                    "size": 2048,
                                    "language": "python",
                                    "functions": ["main", "setup", "teardown"],
                                    "classes": ["App", "Config"],
                                    "imports": ["fastapi", "uvicorn", "os"]
                                },
                                "utils.py": {
                                    "type": "file",
                                    "path": "/src/utils.py",
                                    "size": 1024,
                                    "language": "python",
                                    "functions": ["helper_function", "validate_input"],
                                    "classes": ["Helper"],
                                    "imports": ["json", "datetime"]
                                }
                            }
                        },
                        "tests": {
                            "type": "directory",
                            "path": "/tests",
                            "children": {
                                "test_main.py": {
                                    "type": "file",
                                    "path": "/tests/test_main.py",
                                    "size": 1536,
                                    "language": "python",
                                    "functions": ["test_main", "test_setup"],
                                    "classes": ["TestApp"],
                                    "imports": ["pytest", "unittest"]
                                }
                            }
                        },
                        "docs": {
                            "type": "directory",
                            "path": "/docs",
                            "children": {
                                "README.md": {
                                    "type": "file",
                                    "path": "/docs/README.md",
                                    "size": 512,
                                    "language": "markdown"
                                }
                            }
                        }
                    }
                }
            },
            "statistics": {
                "total_files": 4,
                "total_lines": 500,
                "languages": {
                    "python": 3,
                    "markdown": 1
                },
                "functions": 5,
                "classes": 3
            },
            "dependencies": {
                "python": ["fastapi", "uvicorn", "pytest", "requests"],
                "dev": ["black", "flake8", "mypy"]
            }
        }
        
        return codebase_map
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat-with-repo")
async def chat_with_repo(request: dict):
    """Chat with repository"""
    try:
        repo_name = request.get("repo_name", "")
        query = request.get("query", "")
        
        # Mock chat response - replace with actual RAG implementation
        response = f"""Based on the {repo_name} repository, here's what I found:

**Query**: {query}

**Response**: The repository contains several key components:

1. **Main Application** (`src/main.py`): Contains the FastAPI application setup and main entry point
2. **Utility Functions** (`src/utils.py`): Helper functions for data processing and validation
3. **Tests** (`tests/test_main.py`): Unit tests for the main functionality
4. **Documentation** (`docs/README.md`): Project documentation and setup instructions

The codebase follows good practices with proper separation of concerns and includes comprehensive testing.

**Relevant Files**:
- `src/main.py` (lines 15-25): Main application logic
- `src/utils.py` (lines 8-12): Helper functions
- `tests/test_main.py` (lines 5-20): Test cases

Would you like me to explain any specific part of the codebase in more detail?"""
        
        return {
            "response": response,
            "repo_name": repo_name,
            "query": query,
            "sources": [
                {
                    "file_path": "src/main.py",
                    "line_numbers": [15, 25],
                    "content": "def main():\n    app = FastAPI()\n    return app"
                },
                {
                    "file_path": "src/utils.py",
                    "line_numbers": [8, 12],
                    "content": "def helper_function():\n    return 'helper'"
                }
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-pdf", response_model=GeneratePDFResponse)
async def generate_repository_pdf(request: GeneratePDFRequest):
    """Generate comprehensive PDF documentation for a repository"""
    try:
        # Get repository information
        repo_info = await github_service.get_repository_info(request.owner, request.repo_name)
        
        # Get repository files
        files = await github_service.get_repository_files(request.owner, request.repo_name)
        
        # Get repository structure
        structure = await github_service.get_repository_structure(request.owner, request.repo_name)
        
        # Create output directory if it doesn't exist
        output_dir = "static/pdfs"
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate PDF filename
        pdf_filename = f"{request.owner}_{request.repo_name}_documentation.pdf"
        output_path = os.path.join(output_dir, pdf_filename)
        
        # Generate PDF
        pdf_path = pdf_service.generate_repository_documentation(
            repo_info=repo_info,
            files=files if request.include_code else [],
            structure=structure,
            output_path=output_path
        )
        
        # Get file size
        file_size = os.path.getsize(pdf_path) if os.path.exists(pdf_path) else None
        
        # Return PDF URL
        pdf_url = f"/static/pdfs/{pdf_filename}"
        
        return GeneratePDFResponse(
            pdf_url=pdf_url,
            message=f"PDF documentation generated successfully for {request.owner}/{request.repo_name}",
            file_size=file_size
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

@router.get("/pdf/{owner}/{repo_name}")
async def get_repository_pdf(owner: str, repo_name: str):
    """Get existing PDF documentation for a repository"""
    try:
        pdf_filename = f"{owner}_{repo_name}_documentation.pdf"
        pdf_path = f"static/pdfs/{pdf_filename}"
        
        if not os.path.exists(pdf_path):
            raise HTTPException(status_code=404, detail="PDF documentation not found")
        
        return {"pdf_url": f"/static/pdfs/{pdf_filename}"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 