import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # GitHub Configuration
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
    
    # Gemini API Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    
    # API Configuration
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
    
    # CORS Configuration
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
        "http://localhost:5177",
        "*"
    ]
    
    # Database Configuration (if needed later)
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./devsensei.db")
    
    # Security Configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
    
    # File Upload Configuration
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR = "uploads"
    
    # RAG Configuration
    VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./vector_db")
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200

config = Config() 