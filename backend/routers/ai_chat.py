from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
from typing import List, Optional, Dict, Any
import os
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.hybrid_engine import RAGEngine
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
        print(f"Received chat request: {request}")
        print(f"Messages: {request.messages}")
        print(f"Repo name: {request.repo_name}")
        print(f"Use RAG: {request.use_rag}")
        
        # Extract the latest user message
        user_message = request.messages[-1].content if request.messages else ""
        print(f"User message: {user_message}")
        
        sources = None
        response_text = None
        
        if request.use_rag and request.repo_name:
            print(f"Using RAG with repo: {request.repo_name}")
            try:
                # Use RAG to find relevant context
                search_results = rag_engine.search_code(request.repo_name, user_message)
                print(f"Search results: {search_results}")
                
                if search_results:
                    print("Generating response with context")
                    # Generate response with context
                    response_text = rag_engine.generate_with_context(
                        query=user_message,
                        context=search_results
                    )
                    sources = search_results
            except Exception as e:
                print(f"Error in RAG processing: {str(e)}")
                print(f"Error type: {type(e)}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
                print("Falling back to regular Gemini due to RAG error")
        
        if not response_text:
            print("Using regular Gemini without RAG")
            try:
                # Regular Gemini chat without RAG
                model = genai.GenerativeModel('gemini-2.0-flash')
                
                # Convert messages to Gemini format
                prompt = "\n".join([f"{msg.role}: {msg.content}" for msg in request.messages])
                print(f"Generated prompt: {prompt}")
                response = model.generate_content(prompt)
                response_text = response.text
            except Exception as e:
                print(f"Error in Gemini processing: {str(e)}")
                print(f"Error type: {type(e)}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
                raise
        
        print(f"Generated response: {response_text}")
        return ChatResponse(response=response_text, sources=sources)
        
    except Exception as e:
        print(f"Error in chat_with_ai: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
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
        model = genai.GenerativeModel('gemini-2.0-flash')
        
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
        model = genai.GenerativeModel('gemini-2.0-flash')
        
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