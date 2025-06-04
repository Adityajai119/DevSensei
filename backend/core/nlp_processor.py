"""
NLP Processor for advanced code analysis and understanding
"""
import spacy
import nltk
from typing import List, Dict, Any, Tuple
import re
from collections import Counter
import ast
from radon.complexity import cc_visit
from radon.metrics import mi_visit, h_visit
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
import logging

logger = logging.getLogger(__name__)


class NLPProcessor:
    def __init__(self):
        """Initialize NLP processor with spaCy and NLTK"""
        # Download required NLTK data
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('wordnet', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
        except:
            logger.warning("Some NLTK data couldn't be downloaded")
        
        # Load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            logger.warning("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    def extract_code_entities(self, code: str, language: str = "python") -> Dict[str, List[str]]:
        """Extract entities from code (functions, classes, variables)"""
        entities = {
            "functions": [],
            "classes": [],
            "variables": [],
            "imports": [],
            "comments": []
        }
        
        if language.lower() == "python":
            try:
                tree = ast.parse(code)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        entities["functions"].append(node.name)
                    elif isinstance(node, ast.ClassDef):
                        entities["classes"].append(node.name)
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            entities["imports"].append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        module = node.module or ""
                        for alias in node.names:
                            entities["imports"].append(f"{module}.{alias.name}")
                    elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                        entities["variables"].append(node.id)
                
                # Extract comments
                comment_pattern = r'#.*$|"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\''
                entities["comments"] = re.findall(comment_pattern, code, re.MULTILINE)
                
            except SyntaxError:
                logger.error("Failed to parse Python code")
        
        return entities
    
    def analyze_code_complexity(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Analyze code complexity metrics"""
        metrics = {
            "cyclomatic_complexity": [],
            "maintainability_index": None,
            "halstead_metrics": {},
            "lines_of_code": {
                "total": len(code.splitlines()),
                "code": 0,
                "comments": 0,
                "blank": 0
            }
        }
        
        if language.lower() == "python":
            try:
                # Cyclomatic Complexity
                cc_results = cc_visit(code)
                for result in cc_results:
                    metrics["cyclomatic_complexity"].append({
                        "name": result.name,
                        "complexity": result.complexity,
                        "rank": self._get_complexity_rank(result.complexity)
                    })
                
                # Maintainability Index
                mi_result = mi_visit(code, multi=True)
                metrics["maintainability_index"] = mi_result
                
                # Halstead Metrics
                h_results = h_visit(code)
                if h_results:
                    metrics["halstead_metrics"] = {
                        "volume": h_results[0].volume,
                        "difficulty": h_results[0].difficulty,
                        "effort": h_results[0].effort,
                        "bugs": h_results[0].bugs
                    }
                
                # Count lines
                for line in code.splitlines():
                    stripped = line.strip()
                    if not stripped:
                        metrics["lines_of_code"]["blank"] += 1
                    elif stripped.startswith("#") or stripped.startswith('"""') or stripped.startswith("'''"):
                        metrics["lines_of_code"]["comments"] += 1
                    else:
                        metrics["lines_of_code"]["code"] += 1
                        
            except Exception as e:
                logger.error(f"Failed to analyze code complexity: {str(e)}")
        
        return metrics
    
    def _get_complexity_rank(self, complexity: int) -> str:
        """Get complexity rank based on cyclomatic complexity"""
        if complexity <= 5:
            return "A (Simple)"
        elif complexity <= 10:
            return "B (Moderate)"
        elif complexity <= 20:
            return "C (Complex)"
        elif complexity <= 50:
            return "D (Very Complex)"
        else:
            return "F (Unmaintainable)"
    
    def extract_code_patterns(self, code: str) -> Dict[str, Any]:
        """Extract common code patterns and anti-patterns"""
        patterns = {
            "design_patterns": [],
            "anti_patterns": [],
            "code_smells": []
        }
        
        # Check for common patterns
        if "class" in code and "def __init__" in code:
            patterns["design_patterns"].append("Object-Oriented Programming")
        
        if re.search(r'@\w+\s*\n\s*def', code):
            patterns["design_patterns"].append("Decorator Pattern")
        
        if "yield" in code:
            patterns["design_patterns"].append("Generator Pattern")
        
        if re.search(r'async\s+def', code):
            patterns["design_patterns"].append("Async/Await Pattern")
        
        # Check for anti-patterns
        if re.search(r'except:\s*pass', code):
            patterns["anti_patterns"].append("Silent Exception Handling")
        
        if re.search(r'global\s+\w+', code):
            patterns["anti_patterns"].append("Global Variable Usage")
        
        # Check for code smells
        lines = code.splitlines()
        for i, line in enumerate(lines):
            if len(line) > 120:
                patterns["code_smells"].append(f"Long line at {i+1}: {len(line)} characters")
        
        # Check for deeply nested code
        max_indent = 0
        for line in lines:
            indent = len(line) - len(line.lstrip())
            max_indent = max(max_indent, indent)
        
        if max_indent > 20:  # More than 5 levels of indentation
            patterns["code_smells"].append("Deeply nested code")
        
        return patterns
    
    def generate_code_summary(self, code: str, entities: Dict[str, List[str]]) -> str:
        """Generate a natural language summary of the code"""
        summary_parts = []
        
        if entities["classes"]:
            summary_parts.append(f"This code defines {len(entities['classes'])} class(es): {', '.join(entities['classes'][:3])}")
        
        if entities["functions"]:
            summary_parts.append(f"It contains {len(entities['functions'])} function(s): {', '.join(entities['functions'][:3])}")
        
        if entities["imports"]:
            summary_parts.append(f"It imports {len(entities['imports'])} module(s)")
        
        return ". ".join(summary_parts) if summary_parts else "This code snippet is minimal or empty."
    
    def tokenize_code(self, code: str) -> List[str]:
        """Tokenize code for further analysis"""
        # Remove comments and strings
        code_without_comments = re.sub(r'#.*$|"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'', '', code, flags=re.MULTILINE)
        code_without_strings = re.sub(r'"[^"]*"|\'[^\']*\'', '', code_without_comments)
        
        # Tokenize
        tokens = re.findall(r'\b\w+\b|[^\w\s]', code_without_strings)
        return tokens
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[Tuple[str, int]]:
        """Extract keywords from text using NLP"""
        if not self.nlp:
            # Fallback to simple frequency analysis
            tokens = self.tokenize_code(text)
            counter = Counter(tokens)
            return counter.most_common(top_n)
        
        # Use spaCy for more advanced keyword extraction
        doc = self.nlp(text)
        
        # Extract non-stop words and important parts of speech
        keywords = []
        for token in doc:
            if not token.is_stop and not token.is_punct and token.pos_ in ['NOUN', 'VERB', 'ADJ']:
                keywords.append(token.lemma_.lower())
        
        counter = Counter(keywords)
        return counter.most_common(top_n)
    
    def syntax_highlight(self, code: str, language: str = "python") -> str:
        """Syntax highlight code for better readability"""
        try:
            lexer = get_lexer_by_name(language, stripall=True)
            formatter = HtmlFormatter(style='monokai', linenos=True)
            return highlight(code, lexer, formatter)
        except:
            # Fallback to plain text
            return f"<pre>{code}</pre>" 