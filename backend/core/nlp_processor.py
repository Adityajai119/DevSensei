"""
Enhanced NLP Processor for code analysis and understanding
"""
import os
import spacy
import nltk
from typing import List, Dict, Any, Optional, Set
import re
from collections import defaultdict
import logging
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import tempfile
import shutil

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
    nltk.download('wordnet', quiet=True)
except Exception as e:
    print(f"Warning: Failed to download NLTK data: {str(e)}")

logger = logging.getLogger(__name__)

class NLPProcessor:
    def __init__(self):
        """Initialize NLP processor with optimized settings"""
        # Load spaCy model with error handling
        try:
            self.nlp = spacy.load("en_core_web_sm", disable=['ner', 'parser'])
            self.nlp.max_length = 1000000  # Increase max length for large files
        except Exception as e:
            logger.error(f"Failed to load spaCy model: {str(e)}")
            self.nlp = None
        
        # Initialize TF-IDF vectorizer for semantic similarity
        self.tfidf = TfidfVectorizer(
            max_features=10000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        # Cache for frequently accessed NLP results with size limits
        self.cache = {
            'embeddings': {},
            'similarities': {},
            'keywords': {},
            'complexity': {}
        }
        self.max_cache_size = 1000  # Maximum number of items per cache
        
        # Initialize thread pool for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Regular expressions for code analysis
        self.patterns = {
            'function': re.compile(r'def\s+(\w+)\s*\('),
            'class': re.compile(r'class\s+(\w+)\s*[:\(]'),
            'import': re.compile(r'(?:from|import)\s+(\w+)'),
            'variable': re.compile(r'(\w+)\s*='),
            'comment': re.compile(r'#\s*(.+)$'),
            'docstring': re.compile(r'"""(.*?)"""', re.DOTALL)
        }
    
    def _clean_cache(self, cache_type: str):
        """Clean cache if it exceeds size limit"""
        if len(self.cache[cache_type]) > self.max_cache_size:
            # Remove oldest items
            items_to_remove = len(self.cache[cache_type]) - self.max_cache_size
            for _ in range(items_to_remove):
                self.cache[cache_type].pop(next(iter(self.cache[cache_type])))
    
    def _get_cached_result(self, cache_type: str, key: str) -> Optional[Any]:
        """Get cached NLP result if available"""
        return self.cache[cache_type].get(key)
    
    def _cache_result(self, cache_type: str, key: str, value: Any):
        """Cache NLP result for future use"""
        self.cache[cache_type][key] = value
        self._clean_cache(cache_type)
    
    def analyze_code_structure(self, code: str) -> Dict[str, Any]:
        """Analyze code structure with enhanced NLP"""
        try:
            # Check cache
            cached = self._get_cached_result('complexity', code)
            if cached:
                return cached
            
            # Extract code elements
            structure = {
                'functions': self.patterns['function'].findall(code),
                'classes': self.patterns['class'].findall(code),
                'imports': self.patterns['import'].findall(code),
                'variables': self.patterns['variable'].findall(code),
                'comments': self.patterns['comment'].findall(code),
                'docstrings': self.patterns['docstring'].findall(code)
            }
            
            # Analyze code complexity
            complexity = self._calculate_complexity(code, structure)
            structure['complexity'] = complexity
            
            # Cache result
            self._cache_result('complexity', code, structure)
            
            return structure
            
        except Exception as e:
            logger.error(f"Error in code structure analysis: {str(e)}")
            return {}
    
    def _calculate_complexity(self, code: str, structure: Dict[str, Any]) -> Dict[str, float]:
        """Calculate code complexity metrics"""
        try:
            # Basic metrics
            lines = code.split('\n')
            non_empty_lines = [l for l in lines if l.strip()]
            comment_lines = len(structure['comments'])
            docstring_lines = sum(len(d.split('\n')) for d in structure['docstrings'])
            
            # Advanced metrics
            function_count = len(structure['functions'])
            class_count = len(structure['classes'])
            import_count = len(structure['imports'])
            variable_count = len(structure['variables'])
            
            # Calculate complexity scores
            complexity = {
                'cyclomatic': self._calculate_cyclomatic_complexity(code),
                'cognitive': self._calculate_cognitive_complexity(code),
                'maintainability': self._calculate_maintainability_index(
                    non_empty_lines, comment_lines, docstring_lines
                ),
                'density': self._calculate_code_density(
                    non_empty_lines, comment_lines, docstring_lines
                )
            }
            
            return complexity
            
        except Exception as e:
            logger.error(f"Error calculating complexity: {str(e)}")
            return {}
    
    def _calculate_cyclomatic_complexity(self, code: str) -> float:
        """Calculate cyclomatic complexity"""
        try:
            # Count control structures
            control_structures = sum([
                code.count('if '),
                code.count('for '),
                code.count('while '),
                code.count('except '),
                code.count('case '),
                code.count('&&'),
                code.count('||')
            ])
            
            # Add base complexity
            return control_structures + 1
            
        except Exception as e:
            logger.error(f"Error calculating cyclomatic complexity: {str(e)}")
            return 0.0
    
    def _calculate_cognitive_complexity(self, code: str) -> float:
        """Calculate cognitive complexity"""
        try:
            # Count nested structures
            nested_level = 0
            complexity = 0
            
            for line in code.split('\n'):
                if line.strip().startswith(('if ', 'for ', 'while ', 'try:', 'except ')):
                    nested_level += 1
                    complexity += nested_level
                elif line.strip().startswith(('else:', 'elif ', 'finally:')):
                    complexity += nested_level
                elif line.strip().startswith(('return', 'break', 'continue')):
                    complexity += 1
            
            return complexity
            
        except Exception as e:
            logger.error(f"Error calculating cognitive complexity: {str(e)}")
            return 0.0
    
    def _calculate_maintainability_index(self, code_lines: int, comment_lines: int, docstring_lines: int) -> float:
        """Calculate maintainability index"""
        try:
            # Halstead volume
            volume = code_lines * np.log2(code_lines + 1)
            
            # Comment ratio
            comment_ratio = (comment_lines + docstring_lines) / (code_lines + 1)
            
            # Calculate maintainability index
            mi = 171 - 5.2 * np.log(volume) - 0.23 * np.log(code_lines) - 16.2 * np.log(comment_ratio)
            return max(0, min(100, mi))
            
        except Exception as e:
            logger.error(f"Error calculating maintainability index: {str(e)}")
            return 0.0
    
    def _calculate_code_density(self, code_lines: int, comment_lines: int, docstring_lines: int) -> float:
        """Calculate code density"""
        try:
            total_lines = code_lines + comment_lines + docstring_lines
            return (code_lines / total_lines) * 100 if total_lines > 0 else 0
            
        except Exception as e:
            logger.error(f"Error calculating code density: {str(e)}")
            return 0.0
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """Extract keywords from text with enhanced NLP"""
        try:
            # Check if spaCy is available
            if self.nlp is None:
                logger.warning("spaCy model not available")
                return []
            
            # Check cache
            cached = self._get_cached_result('keywords', text)
            if cached:
                return cached
            
            # Process text with spaCy
            doc = self.nlp(text)
            
            # Extract keywords using multiple methods
            keywords = set()
            
            # Method 1: Noun phrases
            for chunk in doc.noun_chunks:
                keywords.add(chunk.text.lower())
            
            # Method 2: Named entities
            for ent in doc.ents:
                keywords.add(ent.text.lower())
            
            # Method 3: Important words
            for token in doc:
                if token.pos_ in ['NOUN', 'PROPN', 'ADJ'] and not token.is_stop:
                    keywords.add(token.text.lower())
            
            # Convert to list and sort by frequency
            keyword_list = list(keywords)
            keyword_list.sort(key=lambda x: text.lower().count(x), reverse=True)
            
            # Cache result
            self._cache_result('keywords', text, keyword_list[:top_n])
            
            return keyword_list[:top_n]
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {str(e)}")
            return []
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between texts"""
        try:
            # Check cache
            cache_key = f"{text1}:{text2}"
            cached = self._get_cached_result('similarities', cache_key)
            if cached:
                return cached
            
            # Calculate TF-IDF vectors
            tfidf_matrix = self.tfidf.fit_transform([text1, text2])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            # Cache result
            self._cache_result('similarities', cache_key, float(similarity))
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of text"""
        try:
            # Check if spaCy is available
            if self.nlp is None:
                logger.warning("spaCy model not available")
                return {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}
            
            # Process text with spaCy
            doc = self.nlp(text)
            
            # Simple sentiment analysis based on word frequencies
            positive_words = {'good', 'great', 'excellent', 'positive', 'happy', 'success'}
            negative_words = {'bad', 'poor', 'terrible', 'negative', 'sad', 'failure'}
            
            positive_count = sum(1 for token in doc if token.text.lower() in positive_words)
            negative_count = sum(1 for token in doc if token.text.lower() in negative_words)
            total_words = len(doc)
            
            if total_words == 0:
                return {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}
            
            positive_score = positive_count / total_words
            negative_score = negative_count / total_words
            neutral_score = 1 - (positive_score + negative_score)
            
            return {
                'positive': float(positive_score),
                'negative': float(negative_score),
                'neutral': float(neutral_score)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}
    
    def extract_code_patterns(self, code: str) -> Dict[str, List[str]]:
        """Extract common code patterns"""
        try:
            patterns = {
                'design_patterns': [],
                'anti_patterns': [],
                'code_smells': []
            }
            
            # Check for design patterns
            if re.search(r'class\s+\w+\(.*?\):\s+def\s+__init__', code):
                patterns['design_patterns'].append('Class with constructor')
            
            if re.search(r'@property\s+def\s+\w+', code):
                patterns['design_patterns'].append('Property decorator')
            
            if re.search(r'class\s+\w+\(.*?\):\s+def\s+__call__', code):
                patterns['design_patterns'].append('Callable class')
            
            # Check for anti-patterns
            if re.search(r'global\s+\w+', code):
                patterns['anti_patterns'].append('Global variable usage')
            
            if re.search(r'eval\s*\(', code):
                patterns['anti_patterns'].append('Eval usage')
            
            if re.search(r'exec\s*\(', code):
                patterns['anti_patterns'].append('Exec usage')
            
            # Check for code smells
            if len(code.split('\n')) > 100:
                patterns['code_smells'].append('Long function/method')
            
            if re.search(r'if\s+.*?:\s+.*?if\s+.*?:', code):
                patterns['code_smells'].append('Nested if statements')
            
            if re.search(r'for\s+.*?:\s+.*?for\s+.*?:', code):
                patterns['code_smells'].append('Nested loops')
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error extracting code patterns: {str(e)}")
            return {'design_patterns': [], 'anti_patterns': [], 'code_smells': []}
    
    def analyze_code_quality(self, code: str) -> Dict[str, Any]:
        """Analyze code quality"""
        try:
            # Get code structure
            structure = self.analyze_code_structure(code)
            
            # Get code patterns
            patterns = self.extract_code_patterns(code)
            
            # Calculate docstring quality
            docstring_quality = 0.0
            if structure['docstrings']:
                docstring_quality = min(1.0, len(structure['docstrings'][0]) / 100)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                structure['complexity'],
                patterns,
                docstring_quality
            )
            
            return {
                'structure': structure,
                'patterns': patterns,
                'docstring_quality': docstring_quality,
                'recommendations': recommendations
            }
            
        except Exception as e:
            logger.error(f"Error analyzing code quality: {str(e)}")
            return {}
    
    def _generate_recommendations(self, complexity: Dict[str, float], patterns: Dict[str, List[str]], docstring_quality: float) -> List[str]:
        """Generate code improvement recommendations"""
        try:
            recommendations = []
            
            # Complexity-based recommendations
            if complexity.get('cyclomatic', 0) > 10:
                recommendations.append("Consider breaking down complex functions into smaller ones")
            
            if complexity.get('cognitive', 0) > 15:
                recommendations.append("Reduce nesting levels in your code")
            
            if complexity.get('maintainability', 0) < 50:
                recommendations.append("Improve code maintainability by adding more comments and documentation")
            
            # Pattern-based recommendations
            for anti_pattern in patterns['anti_patterns']:
                recommendations.append(f"Avoid using {anti_pattern}")
            
            for code_smell in patterns['code_smells']:
                recommendations.append(f"Consider refactoring to address {code_smell}")
            
            # Documentation recommendations
            if docstring_quality < 0.5:
                recommendations.append("Add more detailed docstrings to your code")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return [] 