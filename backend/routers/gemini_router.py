from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import google.generativeai as genai
import os
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
import json

router = APIRouter()

class CodeExplanationRequest(BaseModel):
    code: str = Field(..., description="Code snippet to explain")
    language: Optional[str] = Field(None, description="Programming language")
    context: Optional[str] = Field(None, description="Additional context about the code")
    gemini_api_key: Optional[str] = Field(None, description="Gemini API key")

class FunctionAnalysisRequest(BaseModel):
    code: str = Field(..., description="Code containing functions to analyze")
    language: str = Field(..., description="Programming language")
    gemini_api_key: Optional[str] = Field(None, description="Gemini API key")

class DatabaseQueryRequest(BaseModel):
    query: str = Field(..., description="Database query to explain")
    db_type: str = Field("sql", description="Database type (sql, mongodb, etc)")
    schema_context: Optional[Dict] = Field(None, description="Database schema context")
    gemini_api_key: Optional[str] = Field(None, description="Gemini API key")

class CodeOptimizationRequest(BaseModel):
    code: str = Field(..., description="Code to optimize")
    language: str = Field(..., description="Programming language")
    optimization_goals: Optional[List[str]] = Field(None, description="Specific optimization goals")
    gemini_api_key: Optional[str] = Field(None, description="Gemini API key")

def configure_gemini(api_key: Optional[str] = None):
    """Configure Gemini AI with API key"""
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise HTTPException(status_code=401, detail="Gemini API key not provided")
    genai.configure(api_key=key)
    return genai.GenerativeModel('gemini-2.0-flash')

def syntax_highlight_code(code: str, language: str = None) -> str:
    """Apply syntax highlighting to code"""
    try:
        if language:
            lexer = get_lexer_by_name(language, stripall=True)
        else:
            lexer = guess_lexer(code)
        
        formatter = HtmlFormatter(style='monokai', linenos=True)
        highlighted = highlight(code, lexer, formatter)
        css = formatter.get_style_defs('.highlight')
        
        return {
            "html": highlighted,
            "css": css,
            "language": lexer.name
        }
    except:
        return {
            "html": f"<pre>{code}</pre>",
            "css": "",
            "language": "text"
        }

@router.post("/explain-code")
async def explain_code(request: CodeExplanationRequest):
    """Get detailed explanation of code snippet"""
    try:
        model = configure_gemini(request.gemini_api_key)
        
        # Create prompt for code explanation
        prompt = f"""
        Please provide a comprehensive explanation of the following code:

        Language: {request.language or 'Auto-detect'}
        Code:
        ```
        {request.code}
        ```
        
        {f'Additional Context: {request.context}' if request.context else ''}
        
        Please explain:
        1. What this code does (overall functionality)
        2. How it works (step-by-step breakdown)
        3. Key concepts or patterns used
        4. Potential use cases
        5. Any important considerations or potential issues
        
        Format the response in a clear, educational manner suitable for developers.
        """
        
        response = model.generate_content(prompt)
        
        # Syntax highlight the code
        highlighted = syntax_highlight_code(request.code, request.language)
        
        return {
            "explanation": response.text,
            "highlighted_code": highlighted,
            "analysis": {
                "lines_of_code": len(request.code.splitlines()),
                "detected_language": highlighted["language"]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-functions")
async def analyze_functions(request: FunctionAnalysisRequest):
    """Analyze functions in the provided code"""
    try:
        model = configure_gemini(request.gemini_api_key)
        
        prompt = f"""
        Analyze all functions/methods in the following {request.language} code:

        ```
        {request.code}
        ```
        
        For each function, provide:
        1. Function name and signature
        2. Purpose and functionality
        3. Parameters (name, type, purpose)
        4. Return value (type and meaning)
        5. Key logic and algorithms used
        6. Complexity analysis (time and space)
        7. Potential edge cases or error conditions
        
        Format the response as structured JSON that can be parsed.
        """
        
        response = model.generate_content(prompt)
        
        # Parse and structure the response
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                analysis_data = json.loads(json_match.group())
            else:
                analysis_data = {"raw_analysis": response.text}
        except:
            analysis_data = {"raw_analysis": response.text}
        
        return {
            "function_analysis": analysis_data,
            "highlighted_code": syntax_highlight_code(request.code, request.language)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/explain-database-query")
async def explain_database_query(request: DatabaseQueryRequest):
    """Explain database queries and connections"""
    try:
        model = configure_gemini(request.gemini_api_key)
        
        schema_info = ""
        if request.schema_context:
            schema_info = f"Database Schema Context:\n{json.dumps(request.schema_context, indent=2)}\n"
        
        prompt = f"""
        Explain the following {request.db_type} database query:

        ```sql
        {request.query}
        ```
        
        {schema_info}
        
        Please provide:
        1. What this query does in plain English
        2. Step-by-step breakdown of the query execution
        3. Tables/collections involved
        4. Filtering conditions and joins explained
        5. Expected output format
        6. Performance considerations
        7. Potential optimizations
        8. Common pitfalls or issues
        
        Make the explanation accessible to developers who may not be database experts.
        """
        
        response = model.generate_content(prompt)
        
        return {
            "explanation": response.text,
            "query_type": request.db_type,
            "highlighted_query": syntax_highlight_code(request.query, "sql" if request.db_type == "sql" else "javascript")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimize-code")
async def optimize_code(request: CodeOptimizationRequest):
    """Get code optimization suggestions"""
    try:
        model = configure_gemini(request.gemini_api_key)
        
        goals = request.optimization_goals or ["performance", "readability", "maintainability"]
        goals_str = ", ".join(goals)
        
        prompt = f"""
        Optimize the following {request.language} code focusing on: {goals_str}

        Original Code:
        ```
        {request.code}
        ```
        
        Please provide:
        1. Optimized version of the code
        2. Explanation of each optimization made
        3. Performance improvements expected
        4. Trade-offs (if any)
        5. Best practices applied
        6. Alternative approaches (if applicable)
        
        Format the optimized code clearly and explain the reasoning.
        """
        
        response = model.generate_content(prompt)
        
        # Extract optimized code from response
        import re
        code_blocks = re.findall(r'```(?:\w+)?\n(.*?)```', response.text, re.DOTALL)
        optimized_code = code_blocks[0] if code_blocks else request.code
        
        return {
            "original_code": syntax_highlight_code(request.code, request.language),
            "optimized_code": syntax_highlight_code(optimized_code, request.language),
            "explanation": response.text,
            "optimization_goals": goals
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/code-review")
async def review_code(request: CodeExplanationRequest):
    """Perform AI-powered code review"""
    try:
        model = configure_gemini(request.gemini_api_key)
        
        prompt = f"""
        Perform a thorough code review of the following {request.language or 'code'}:

        ```
        {request.code}
        ```
        
        {f'Context: {request.context}' if request.context else ''}
        
        Please analyze and provide feedback on:
        1. Code Quality and Style
        2. Potential bugs or errors
        3. Security vulnerabilities
        4. Performance issues
        5. Best practices violations
        6. Suggestions for improvement
        7. Testing recommendations
        8. Documentation needs
        
        Rate the code on a scale of 1-10 and provide actionable feedback.
        """
        
        response = model.generate_content(prompt)
        
        return {
            "review": response.text,
            "highlighted_code": syntax_highlight_code(request.code, request.language),
            "timestamp": os.popen('date').read().strip()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 