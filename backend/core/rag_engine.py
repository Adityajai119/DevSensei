"""
RAG (Retrieval Augmented Generation) Engine for code understanding
"""
import os
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.utils import embedding_functions
import google.generativeai as genai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import logging

logger = logging.getLogger(__name__)


class RAGEngine:
    def __init__(self, gemini_api_key: str, db_path: str = "./vector_db"):
        """Initialize RAG engine with Gemini embeddings"""
        self.gemini_api_key = gemini_api_key
        self.db_path = db_path
        
        # Configure Gemini
        genai.configure(api_key=gemini_api_key)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Initialize embeddings
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=gemini_api_key
        )
        
        # Text splitter for code
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""],
            length_function=len,
        )
        
        # Collection for storing code embeddings
        self.collection_name = "code_embeddings"
        
    def get_or_create_collection(self, repo_name: str):
        """Get or create a collection for a specific repository"""
        collection_name = f"{self.collection_name}_{repo_name.replace('/', '_')}"
        try:
            collection = self.client.get_collection(collection_name)
        except:
            collection = self.client.create_collection(
                name=collection_name,
                embedding_function=embedding_functions.GoogleGenerativeAiEmbeddingFunction(
                    api_key=self.gemini_api_key,
                    model_name="models/embedding-001"
                )
            )
        return collection
    
    def index_code(self, repo_name: str, files: List[Dict[str, str]]):
        """Index code files into the vector database"""
        collection = self.get_or_create_collection(repo_name)
        
        documents = []
        metadatas = []
        ids = []
        
        for idx, file in enumerate(files):
            # Split code into chunks
            chunks = self.text_splitter.split_text(file['content'])
            
            for chunk_idx, chunk in enumerate(chunks):
                documents.append(chunk)
                metadatas.append({
                    'file_path': file['path'],
                    'file_name': os.path.basename(file['path']),
                    'language': file.get('language', 'unknown'),
                    'chunk_index': chunk_idx,
                    'total_chunks': len(chunks)
                })
                ids.append(f"{file['path']}_{chunk_idx}")
        
        # Add to collection in batches
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i+batch_size]
            batch_metas = metadatas[i:i+batch_size]
            batch_ids = ids[i:i+batch_size]
            
            collection.add(
                documents=batch_docs,
                metadatas=batch_metas,
                ids=batch_ids
            )
        
        logger.info(f"Indexed {len(documents)} chunks for repository {repo_name}")
        return len(documents)
    
    def search_code(self, repo_name: str, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant code snippets using semantic search"""
        collection = self.get_or_create_collection(repo_name)
        
        # Perform semantic search
        results = collection.query(
            query_texts=[query],
            n_results=k
        )
        
        # Format results
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                })
        
        return formatted_results
    
    def generate_with_context(self, query: str, context: List[Dict[str, Any]], 
                            system_prompt: Optional[str] = None) -> str:
        """Generate response using retrieved context"""
        # Prepare context string
        context_str = "\n\n".join([
            f"File: {item['metadata']['file_path']}\n```\n{item['content']}\n```"
            for item in context
        ])
        
        # Default system prompt for code understanding
        if not system_prompt:
            system_prompt = """You are an expert code analyst. 
            Use the provided code context to answer questions accurately.
            If the context doesn't contain enough information, say so.
            Always cite the specific files when referencing code."""
        
        # Create prompt
        prompt = f"""System: {system_prompt}

Context:
{context_str}

Question: {query}

Answer:"""
        
        # Generate response using Gemini
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        
        return response.text
    
    def analyze_code_quality(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Analyze code quality using NLP and static analysis"""
        prompt = f"""Analyze the following {language} code and provide:
1. Code quality score (0-10)
2. Potential issues
3. Best practices violations
4. Suggestions for improvement
5. Security concerns (if any)

Code:
```{language}
{code}
```

Provide the analysis in a structured format."""
        
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        
        return {
            "analysis": response.text,
            "language": language
        }
    
    def clear_collection(self, repo_name: str):
        """Clear all embeddings for a repository"""
        collection_name = f"{self.collection_name}_{repo_name.replace('/', '_')}"
        try:
            self.client.delete_collection(collection_name)
            logger.info(f"Cleared collection for repository {repo_name}")
        except:
            logger.warning(f"Collection {collection_name} not found") 