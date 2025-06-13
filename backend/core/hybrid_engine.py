"""
Hybrid Code Understanding Engine combining RAG, CodeBERT, and Tree-sitter
"""
import os
from typing import List, Dict, Any, Optional, Set
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import google.generativeai as genai
from transformers import AutoTokenizer, AutoModel
import torch
from tree_sitter import Language, Parser
import json
import logging
from concurrent.futures import ThreadPoolExecutor
import tempfile
import shutil

logger = logging.getLogger(__name__)

class HybridEngine:
    def __init__(self, api_key: str):
        """Initialize hybrid engine with all components"""
        self.api_key = api_key
        
        # Initialize RAG component
        self.rag = RAGEngine(api_key=api_key)
        
        # Initialize CodeBERT with error handling
        try:
            self.codebert_tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
            self.codebert_model = AutoModel.from_pretrained("microsoft/codebert-base")
            self.codebert_model.eval()  # Set to evaluation mode
        except Exception as e:
            logger.error(f"Failed to load CodeBERT model: {str(e)}")
            self.codebert_tokenizer = None
            self.codebert_model = None
        
        # Initialize Tree-sitter
        self.parser = Parser()
        self.languages = {}
        self._initialize_tree_sitter()
        
        # Initialize thread pool for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Cache for frequently accessed results with size limits
        self.cache = {
            'codebert_embeddings': {},
            'ast_analysis': {},
            'combined_results': {}
        }
        self.max_cache_size = 1000  # Maximum number of items per cache
    
    def _initialize_tree_sitter(self):
        """Initialize Tree-sitter with language support"""
        try:
            # Create temporary directory for language files
            temp_dir = tempfile.mkdtemp()
            language_path = os.path.join(temp_dir, 'my-languages.so')
            
            # Download and build language library
            Language.build_library(
                language_path,
                [
                    'https://github.com/tree-sitter/tree-sitter-python',
                    'https://github.com/tree-sitter/tree-sitter-javascript',
                    'https://github.com/tree-sitter/tree-sitter-java',
                    'https://github.com/tree-sitter/tree-sitter-cpp'
                ]
            )
            
            # Load languages
            PY_LANGUAGE = Language(language_path, 'python')
            JS_LANGUAGE = Language(language_path, 'javascript')
            JAVA_LANGUAGE = Language(language_path, 'java')
            CPP_LANGUAGE = Language(language_path, 'cpp')
            
            self.languages = {
                'python': PY_LANGUAGE,
                'javascript': JS_LANGUAGE,
                'java': JAVA_LANGUAGE,
                'cpp': CPP_LANGUAGE
            }
            
            # Clean up temporary directory
            shutil.rmtree(temp_dir)
            
        except Exception as e:
            logger.error(f"Error initializing Tree-sitter: {str(e)}")
            self.languages = {}
    
    def _clean_cache(self, cache_type: str):
        """Clean cache if it exceeds size limit"""
        if len(self.cache[cache_type]) > self.max_cache_size:
            # Remove oldest items
            items_to_remove = len(self.cache[cache_type]) - self.max_cache_size
            for _ in range(items_to_remove):
                self.cache[cache_type].pop(next(iter(self.cache[cache_type])))
    
    def _get_codebert_embedding(self, code: str) -> np.ndarray:
        """Get CodeBERT embedding for code"""
        try:
            # Check if CodeBERT is available
            if self.codebert_model is None or self.codebert_tokenizer is None:
                logger.warning("CodeBERT model not available")
                return np.zeros(768)
            
            # Check cache
            if code in self.cache['codebert_embeddings']:
                return self.cache['codebert_embeddings'][code]
            
            # Tokenize and get embeddings
            inputs = self.codebert_tokenizer(code, return_tensors="pt", padding=True, truncation=True)
            with torch.no_grad():
                outputs = self.codebert_model(**inputs)
            
            # Use [CLS] token embedding as code representation
            embedding = outputs.last_hidden_state[0][0].numpy()
            
            # Cache result
            self.cache['codebert_embeddings'][code] = embedding
            self._clean_cache('codebert_embeddings')
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error getting CodeBERT embedding: {str(e)}")
            return np.zeros(768)  # Return zero vector as fallback
    
    def _analyze_ast(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze code using Tree-sitter"""
        try:
            # Check cache
            cache_key = f"{code}:{language}"
            if cache_key in self.cache['ast_analysis']:
                return self.cache['ast_analysis'][cache_key]
            
            if language not in self.languages:
                logger.warning(f"Language {language} not supported by Tree-sitter")
                return {}
            
            # Parse code
            self.parser.set_language(self.languages[language])
            tree = self.parser.parse(bytes(code, 'utf8'))
            
            # Extract AST information
            ast_info = {
                'functions': [],
                'classes': [],
                'imports': [],
                'variables': [],
                'control_structures': []
            }
            
            # Traverse AST
            def traverse_node(node):
                if node.type == 'function_definition':
                    ast_info['functions'].append({
                        'name': node.child_by_field_name('name').text.decode('utf8'),
                        'start_line': node.start_point[0],
                        'end_line': node.end_point[0]
                    })
                elif node.type == 'class_definition':
                    ast_info['classes'].append({
                        'name': node.child_by_field_name('name').text.decode('utf8'),
                        'start_line': node.start_point[0],
                        'end_line': node.end_point[0]
                    })
                elif node.type in ['if_statement', 'for_statement', 'while_statement']:
                    ast_info['control_structures'].append({
                        'type': node.type,
                        'start_line': node.start_point[0],
                        'end_line': node.end_point[0]
                    })
                
                for child in node.children:
                    traverse_node(child)
            
            traverse_node(tree.root_node)
            
            # Cache result
            self.cache['ast_analysis'][cache_key] = ast_info
            self._clean_cache('ast_analysis')
            
            return ast_info
            
        except Exception as e:
            logger.error(f"Error analyzing AST: {str(e)}")
            return {}
    
    def index_code(self, repo_name: str, files: List[Dict[str, str]]) -> None:
        """Index code using all components"""
        try:
            # Index with RAG
            self.rag.index_code(repo_name, files)
            
            # Process each file with CodeBERT and Tree-sitter
            for file in files:
                # Get CodeBERT embedding
                self._get_codebert_embedding(file['content'])
                
                # Analyze AST
                self._analyze_ast(file['content'], file.get('language', 'python'))
            
            logger.info(f"Indexed {len(files)} files with hybrid engine")
            
        except Exception as e:
            logger.error(f"Error indexing code: {str(e)}")
            raise
    
    def search_code(self, repo_name: str, query: str, k: int = 5) -> List[Dict[str, str]]:
        """Search code using all components"""
        try:
            # Get results from each component
            rag_results = self.rag.search_code(repo_name, query, k)
            
            # Get CodeBERT embedding for query
            query_embedding = self._get_codebert_embedding(query)
            
            # Combine and rank results
            combined_results = []
            for result in rag_results:
                # Get CodeBERT similarity
                code_embedding = self._get_codebert_embedding(result['content'])
                codebert_similarity = cosine_similarity(
                    [query_embedding],
                    [code_embedding]
                )[0][0]
                
                # Get AST analysis
                ast_info = self._analyze_ast(result['content'], result['language'])
                
                # Calculate combined score
                combined_score = (
                    0.4 * result['relevance_score'] +  # RAG score
                    0.4 * codebert_similarity +        # CodeBERT score
                    0.2 * (len(ast_info['functions']) + len(ast_info['classes'])) / 10  # AST complexity
                )
                
                # Add enhanced result
                enhanced_result = {
                    **result,
                    'codebert_similarity': float(codebert_similarity),
                    'ast_info': ast_info,
                    'combined_score': float(combined_score)
                }
                combined_results.append(enhanced_result)
            
            # Sort by combined score
            combined_results.sort(key=lambda x: x['combined_score'], reverse=True)
            
            return combined_results[:k]
            
        except Exception as e:
            logger.error(f"Error searching code: {str(e)}")
            return []
    
    def analyze_code(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze code using all components"""
        try:
            # Get CodeBERT embedding
            codebert_embedding = self._get_codebert_embedding(code)
            
            # Get AST analysis
            ast_info = self._analyze_ast(code, language)
            
            # Get RAG analysis (if code is indexed)
            rag_analysis = self.rag.search_code("temp", code, k=1)
            
            return {
                'codebert_embedding': codebert_embedding.tolist(),
                'ast_info': ast_info,
                'rag_analysis': rag_analysis[0] if rag_analysis else None
            }
            
        except Exception as e:
            logger.error(f"Error analyzing code: {str(e)}")
            return {}

class RAGEngine:
    def __init__(self, api_key: str):
        """Initialize RAG engine"""
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Initialize embeddings cache
        self.embeddings_cache = {}
        self.max_cache_size = 1000
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for text using Gemini"""
        try:
            # Check cache
            if text in self.embeddings_cache:
                return self.embeddings_cache[text]
            
            # Get embedding from Gemini
            response = self.model.embed_content(text)
            embedding = np.array(response.embedding)
            
            # Cache result
            self.embeddings_cache[text] = embedding
            if len(self.embeddings_cache) > self.max_cache_size:
                self.embeddings_cache.pop(next(iter(self.embeddings_cache)))
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error getting embedding: {str(e)}")
            return np.zeros(768)
    
    def index_code(self, repo_name: str, files: List[Dict[str, str]]) -> None:
        """Index code files"""
        try:
            for file in files:
                # Get embedding for file content
                self._get_embedding(file['content'])
            
            logger.info(f"Indexed {len(files)} files with RAG engine")
            
        except Exception as e:
            logger.error(f"Error indexing code: {str(e)}")
            raise
    
    def search_code(self, repo_name: str, query: str, k: int = 5) -> List[Dict[str, str]]:
        """Search code using RAG"""
        try:
            # Get query embedding
            query_embedding = self._get_embedding(query)
            
            # Calculate similarities and return top k results
            results = []
            for file in self.embeddings_cache.items():
                similarity = cosine_similarity(
                    [query_embedding],
                    [file[1]]
                )[0][0]
                
                results.append({
                    'content': file[0],
                    'relevance_score': float(similarity)
                })
            
            # Sort by relevance score
            results.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            return results[:k]
            
        except Exception as e:
            logger.error(f"Error searching code: {str(e)}")
            return []
    
    def generate_explanation(self, code: str, context: Optional[str] = None) -> str:
        """Generate explanation for code"""
        try:
            prompt = f"Explain this code:\n{code}"
            if context:
                prompt += f"\nContext: {context}"
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating explanation: {str(e)}")
            return "Failed to generate explanation" 