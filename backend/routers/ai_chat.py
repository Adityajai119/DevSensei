from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
from typing import List, Optional, Dict, Any
import os
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.rag_engine import RAGEngine
from core.nlp_processor import NLPProcessor

load_dotenv()

router = APIRouter()

# Initialize Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=GEMINI_API_KEY)

# Initialize RAG engine and NLP processor
rag_engine = RAGEngine(GEMINI_API_KEY)
nlp_processor = NLPProcessor()


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    repo_name: Optional[str] = None
    use_rag: bool = True


class ChatResponse(BaseModel):
    response: str
    sources: Optional[List[Dict[str, Any]]] = None


class CodeAnalysisRequest(BaseModel):
    code: str
    language: str = "python"
    analysis_type: str = "full"  # full, entities, complexity, patterns


class CodeAnalysisResponse(BaseModel):
    entities: Optional[Dict[str, List[str]]] = None
    complexity: Optional[Dict[str, Any]] = None
    patterns: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None
    keywords: Optional[List[tuple]] = None
    quality_analysis: Optional[Dict[str, Any]] = None


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """
    Chat with AI using Google Gemini with optional RAG support
    """
    try:
        # Extract the latest user message
        user_message = request.messages[-1].content if request.messages else ""
        
        sources = None
        
        if request.use_rag and request.repo_name:
            # Use RAG to find relevant context
            search_results = rag_engine.search_code(request.repo_name, user_message)
            
            if search_results:
                # Generate response with context
                response_text = rag_engine.generate_with_context(
                    query=user_message,
                    context=search_results
                )
                sources = search_results
            else:
                # Fallback to regular Gemini
                model = genai.GenerativeModel('gemini-pro')
                
                # Convert messages to Gemini format
                prompt = "\n".join([f"{msg.role}: {msg.content}" for msg in request.messages])
                response = model.generate_content(prompt)
                response_text = response.text
        else:
            # Regular Gemini chat without RAG
            model = genai.GenerativeModel('gemini-pro')
            
            # Convert messages to Gemini format
            prompt = "\n".join([f"{msg.role}: {msg.content}" for msg in request.messages])
            response = model.generate_content(prompt)
            response_text = response.text
        
        return ChatResponse(response=response_text, sources=sources)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-code", response_model=CodeAnalysisResponse)
async def analyze_code(request: CodeAnalysisRequest):
    """
    Analyze code using NLP and static analysis
    """
    try:
        response = CodeAnalysisResponse()
        
        if request.analysis_type in ["full", "entities"]:
            response.entities = nlp_processor.extract_code_entities(
                request.code, request.language
            )
            
        if request.analysis_type in ["full", "complexity"]:
            response.complexity = nlp_processor.analyze_code_complexity(
                request.code, request.language
            )
            
        if request.analysis_type in ["full", "patterns"]:
            response.patterns = nlp_processor.extract_code_patterns(request.code)
            
        if response.entities:
            response.summary = nlp_processor.generate_code_summary(
                request.code, response.entities
            )
            
        # Extract keywords
        response.keywords = nlp_processor.extract_keywords(request.code)
        
        # Get AI-powered quality analysis
        response.quality_analysis = rag_engine.analyze_code_quality(
            request.code, request.language
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/index-repository")
async def index_repository(repo_name: str, files: List[Dict[str, str]]):
    """
    Index a repository's code files for RAG
    """
    try:
        num_chunks = rag_engine.index_code(repo_name, files)
        return {"message": f"Successfully indexed {num_chunks} code chunks", "chunks": num_chunks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-code")
async def generate_code(prompt: str, language: str = "python", context: Optional[str] = None):
    """
    Generate code based on prompt using Gemini
    """
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        # Create a specialized prompt for code generation
        full_prompt = f"""Generate {language} code for the following request:

Request: {prompt}

{f'Context: {context}' if context else ''}

Requirements:
1. Write clean, well-commented code
2. Follow best practices for {language}
3. Include error handling where appropriate
4. Make the code production-ready

Code:
```{language}"""
        
        response = model.generate_content(full_prompt)
        
        # Extract code from response
        code = response.text
        if "```" in code:
            # Extract code block
            code_parts = code.split("```")
            if len(code_parts) >= 2:
                code = code_parts[1]
                # Remove language identifier if present
                if code.startswith(language):
                    code = code[len(language):].strip()
        
        return {
            "code": code,
            "language": language,
            "explanation": f"Generated {language} code for: {prompt}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/explain-code")
async def explain_code(code: str, language: str = "python"):
    """
    Explain code using Gemini and NLP analysis
    """
    try:
        # Get NLP analysis
        entities = nlp_processor.extract_code_entities(code, language)
        complexity = nlp_processor.analyze_code_complexity(code, language)
        patterns = nlp_processor.extract_code_patterns(code)
        
        # Get AI explanation
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""Explain the following {language} code in detail:

```{language}
{code}
```

Please provide:
1. Overall purpose of the code
2. How it works step by step
3. Key functions and their roles
4. Any important patterns or techniques used
5. Potential improvements or considerations"""
        
        response = model.generate_content(prompt)
        
        return {
            "explanation": response.text,
            "entities": entities,
            "complexity": complexity,
            "patterns": patterns,
            "summary": nlp_processor.generate_code_summary(code, entities)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 