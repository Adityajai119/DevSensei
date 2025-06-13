from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
from routers import (
    documentation,
    github_router,
    code_execution
)
from typing import Dict, Any
import time

# Simple in-memory cache implementation
class SimpleCache:
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._ttl: Dict[str, float] = {}

    def set(self, key: str, value: Any, ttl: int = 300):
        self._cache[key] = value
        self._ttl[key] = time.time() + ttl

    def get(self, key: str) -> Any:
        if key in self._cache:
            if time.time() < self._ttl[key]:
                return self._cache[key]
            else:
                del self._cache[key]
                del self._ttl[key]
        return None

# Initialize cache
cache = SimpleCache()

# Load environment variables
load_dotenv()

app = FastAPI(
    title="DevSensei API",
    description="AI-powered code analysis and documentation API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

# Include routers
app.include_router(github_router.router, prefix="/api/github", tags=["GitHub"])
app.include_router(documentation.router, prefix="/api/documentation", tags=["Documentation"])
app.include_router(code_execution.router, prefix="/api/code", tags=["Code Execution"])

@app.get("/")
async def root():
    return {"message": "Welcome to DevSensei API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 