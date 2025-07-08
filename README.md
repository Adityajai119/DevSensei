# DevSensei

DevSensei is an advanced AI-powered code understanding and codebase Q&A platform. Unlike traditional LLM-based tools (like ChatGPT, Gemini, or Copilot) that are limited to processing only a handful of files at a time, DevSensei can fetch, index, and provide context from **hundreds or even thousands of files** in a repository. This enables deep, context-aware code analysis, documentation, and code generation at scale.

---

## 🚀 Unique Features

- **Massive Context Window**: Fetches and processes hundreds/thousands of files from a codebase for context-aware answers and code generation.
- **Retrieval-Augmented Generation (RAG)**: Combines LLMs with vector search (ChromaDB + Sentence Transformers) for highly relevant, code-aware responses.
- **GitHub Integration**: Seamlessly fetches repositories, files, and structures directly from GitHub.
- **AI Code Analysis & Generation**: Analyze, explain, and generate code using Google Gemini and custom NLP pipelines.
- **Full-Stack Solution**: Modern React + TypeScript frontend, FastAPI backend, and persistent vector database.
- **Open Source & Extensible**: Easily add new LLMs, code analysis tools, or custom integrations.

---

## 🏗️ Tech Stack

### Backend
- **FastAPI** (Python)
- **Google Gemini API** (LLM)
- **ChromaDB** (Vector DB for RAG)
- **Sentence Transformers** (Embeddings)
- **PyGithub** (GitHub API)
- **ReportLab** (PDF generation)

### Frontend
- **React** + **TypeScript** + **Vite**
- **TailwindCSS** (UI)
- **Monaco Editor** (Code editing)
- **Framer Motion**, **Styled Components**, **Lucide Icons**

---

## ⚡ Why DevSensei?

> **Other LLM tools (ChatGPT, Gemini, Copilot, etc.) are limited to 20-30 files per prompt. DevSensei can fetch and process context from hundreds or thousands of files, enabling true codebase-scale intelligence.**

- **Ideal for large codebases**: Get answers, documentation, and code generation with full-project context.
- **No more context window limits**: RAG + vector DB means you can ask about any part of your repo, no matter the size.
- **Perfect for onboarding, refactoring, and documentation.**

---

## 🛠️ Setup & Usage

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
# Add your API keys to backend/.env (see .env.example)
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Environment Variables
- **backend/.env**: Contains `GITHUB_TOKEN`, `GEMINI_API_KEY` (never commit this file)
- **frontend/.env**: Contains API URLs (safe to share, but don't expose secrets)

---

## 🧩 Features
- **Chat with AI** about your codebase, with full-project context
- **Analyze, explain, and generate code** in any language
- **Fetch and index entire GitHub repositories**
- **RAG-powered answers**: Always relevant, always in context
- **Modern, beautiful UI**

---

## 🤝 Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

- Fork the repo
- Create your feature branch (`git checkout -b feature/your-feature`)
- Commit your changes (`git commit -am 'Add new feature'`)
- Push to the branch (`git push origin feature/your-feature`)
- Open a pull request

---

## 📄 License
MIT

---

## 🙏 Acknowledgements
- [FastAPI](https://fastapi.tiangolo.com/)
- [ChromaDB](https://www.trychroma.com/)
- [Google Gemini](https://ai.google.dev/gemini-api)
- [Sentence Transformers](https://www.sbert.net/)
- [PyGithub](https://pygithub.readthedocs.io/)
- [React](https://react.dev/)
- [Vite](https://vitejs.dev/)
- [TailwindCSS](https://tailwindcss.com/)

---

## 🌟 Star this project if you like it!

---

### [Project Link](https://github.com/Adityajai119/DevSensei) 