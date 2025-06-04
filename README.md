# DevSensei 🧙‍♂️

An AI-powered code understanding and generation platform that combines the power of Google Gemini AI, RAG (Retrieval Augmented Generation), and NLP to help developers work more efficiently.

![DevSensei](https://img.shields.io/badge/DevSensei-AI%20Code%20Assistant-purple)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![React](https://img.shields.io/badge/React-18.2+-61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-5.2+-3178C6)

## 🚀 Features

### 1. Repository Explorer 📁
- **GitHub Integration**: Input any GitHub username and browse their repositories
- **Smart Documentation**: Generate comprehensive PDF documentation including:
  - Setup instructions
  - Architecture overview
  - Codebase map visualization
  - API documentation
- **Chat with Code**: Ask questions about the codebase using RAG-powered chat
- **Visual Codebase Map**: See the structure and relationships in your code

### 2. Code Playground 💻
- **Multi-Language Support**: Python, JavaScript, TypeScript, Java, C++, Go, Rust, and more
- **Real-time Execution**: Run code directly in the browser
- **AI-Powered Features**:
  - **Generate**: Create code from natural language descriptions
  - **Explain**: Get detailed explanations of code functionality
  - **Debug**: Identify and fix bugs automatically
  - **Optimize**: Improve code performance and readability
- **Syntax Highlighting**: Beautiful code editor with Monaco Editor

### 3. Frontend AI Playground 🎨
- **Framework Support**: Vanilla JS, React, Vue, Angular
- **Live Preview**: See your generated frontend code in action instantly
- **AI Generation**: Describe what you want to build, and AI creates it
- **Example Projects**:
  - Games (Flappy Bird, Memory Cards)
  - Applications (Todo Lists, Calculators)
  - Landing Pages
  - Interactive Dashboards

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **Google Gemini AI**: Advanced language model for code generation and understanding
- **ChromaDB**: Vector database for RAG implementation
- **Langchain**: Framework for building applications with LLMs
- **spaCy & NLTK**: Natural Language Processing
- **Docker**: Optional containerization for code execution
- **NetworkX & Matplotlib**: Codebase visualization

### Frontend
- **React 18**: UI library
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **Framer Motion**: Animation library
- **Monaco Editor**: VS Code's editor in the browser
- **Axios**: HTTP client

## 📋 Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- Git
- Docker (optional, for sandboxed code execution)

## 🔧 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/DevSensei.git
cd DevSensei
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run NLP setup script
python setup_nlp.py
```

### 3. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install
```

### 4. Environment Configuration

Create `.env` files in both backend and frontend directories:

**Backend `.env**:**
```env
# Google Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# GitHub Personal Access Token
GITHUB_TOKEN=your_github_token_here

# Server Configuration
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Vector Database
VECTOR_DB_PATH=./vector_db
EMBEDDING_MODEL=models/embedding-001

# NLP Configuration
ENABLE_NLP=True
NLP_MODEL=en_core_web_sm
```

**Frontend `.env**:**
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=DevSensei
```

## 🚀 Running the Application

### Start Backend Server
```bash
cd backend
uvicorn main:app --reload
```
The API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### Start Frontend Development Server
```bash
cd frontend
npm run dev
```
The frontend will be available at `http://localhost:5173`

## 📖 Usage Guide

### Repository Explorer
1. Navigate to Repository Explorer
2. Enter a GitHub username
3. Select a repository from the list
4. Options:
   - **Generate PDF**: Creates comprehensive documentation
   - **Chat with Repo**: Ask questions about the code
   - **View Codebase Map**: Visualize the repository structure

### Code Playground
1. Navigate to Code Playground
2. Select your programming language
3. Options:
   - **Generate**: Describe what you want to build
   - **Run**: Execute your code with optional input
   - **Explain**: Get detailed code explanation
   - **Debug**: Fix errors automatically
   - **Optimize**: Improve code quality

### Frontend AI Playground
1. Navigate to Frontend AI
2. Describe your frontend project
3. Select framework (Vanilla JS recommended for live preview)
4. Generate code and see live preview

## 🔑 API Keys

### Google Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add to backend `.env` file

### GitHub Personal Access Token
1. Go to [GitHub Settings > Tokens](https://github.com/settings/tokens)
2. Generate new token with `repo` scope
3. Add to backend `.env` file

## 🏗️ Architecture

```
DevSensei/
├── backend/
│   ├── core/
│   │   ├── rag_engine.py      # RAG implementation
│   │   ├── nlp_processor.py   # NLP analysis
│   │   └── code_executor.py   # Code execution engine
│   ├── routers/
│   │   ├── github_scraper.py  # GitHub integration
│   │   ├── ai_chat.py         # AI chat endpoints
│   │   ├── documentation.py   # Doc generation
│   │   └── code_execution.py  # Code execution endpoints
│   └── main.py                # FastAPI application
├── frontend/
│   ├── src/
│   │   ├── pages/             # React pages
│   │   ├── services/          # API services
│   │   └── App.tsx           # Main application
│   └── package.json
└── README.md
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google Gemini AI for powerful language models
- The open-source community for amazing tools and libraries
- All contributors and users of DevSensei

## 📞 Support

For support, please open an issue in the GitHub repository or contact the maintainers.

---

Built with ❤️ by the DevSensei Team 