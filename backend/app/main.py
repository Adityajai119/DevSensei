import os
# Disable ChromaDB telemetry warnings
os.environ["CHROMA_TELEMETRY_ENABLED"] = "FALSE"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api import repo_search, interact_repo, ai_compiler, frontend_playground, ai, github, documentation, code

app = FastAPI(title="DevSensei API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Use absolute path for static directory
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Legacy routes (keeping for backward compatibility)
app.include_router(repo_search.router, prefix="/api/repo-search", tags=["Repo Search"])
app.include_router(interact_repo.router, prefix="/api/interact-repo", tags=["Interact with Repo"])
app.include_router(ai_compiler.router, prefix="/api/ai-compiler", tags=["AI Compiler"])
app.include_router(frontend_playground.router, prefix="/api/frontend-playground", tags=["Frontend Playground"])

# New API routes matching frontend expectations
app.include_router(ai.router, prefix="/api/ai", tags=["AI"])
app.include_router(github.router, prefix="/api/github", tags=["GitHub"])
app.include_router(documentation.router, prefix="/api/documentation", tags=["Documentation"])
app.include_router(code.router, prefix="/api/code", tags=["Code"]) 