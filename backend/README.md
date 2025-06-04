# DevSensei Backend

A powerful FastAPI backend for AI-powered code analysis, documentation, and building.

## Features

### 🔍 Code Scraping
- GitHub repository analysis and documentation
- File structure visualization
- Code statistics and language detection
- Repository content exploration

### 💡 Doubt Resolution
- AI-powered code explanations using Google Gemini
- Function and method analysis
- Database query explanations
- Code optimization suggestions
- Automated code reviews

### 🔨 Code Building
- Natural language to code generation
- Multi-language support
- Code debugging and fixing
- Test case generation
- Code refactoring
- Language conversion

### 🎨 UI Building
- Complete UI project generation
- Component library creation
- Design system generation
- Live preview capabilities

## Setup

1. **Clone the repository**
```bash
cd DevSensei/backend
```

2. **Create virtual environment**
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix/MacOS
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**

Create a `.env` file in the backend directory:
```env
# GitHub Configuration
GITHUB_TOKEN=your_github_personal_access_token

# Gemini AI Configuration  
GEMINI_API_KEY=your_gemini_api_key

# Optional Database
DATABASE_URL=sqlite:///./devsensei.db

# Optional Redis
REDIS_URL=redis://localhost:6379

# Application Settings
SECRET_KEY=your_secret_key_here
DEBUG=True
ENVIRONMENT=development
```

5. **Run the server**
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## License

MIT License 