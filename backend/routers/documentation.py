from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv
import google.generativeai as genai
from github import Github
import base64
import json
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image, Flowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.rag_engine import RAGEngine
from core.nlp_processor import NLPProcessor
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

load_dotenv()

router = APIRouter()

# Initialize services
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=GEMINI_API_KEY)
github_client = Github(GITHUB_TOKEN) if GITHUB_TOKEN else None
rag_engine = RAGEngine(GEMINI_API_KEY) if GEMINI_API_KEY else None
nlp_processor = NLPProcessor()


class ProjectDocRequest(BaseModel):
    owner: str
    repo: str
    branch: str = "main"
    include_setup: bool = True
    include_architecture: bool = True
    include_api_docs: bool = True
    include_codebase_map: bool = True


class CodebaseMapRequest(BaseModel):
    owner: str
    repo: str
    branch: str = "main"


def generate_codebase_map(repo_name: str, files: List[Dict]) -> Dict:
    """Generate a visual codebase map showing file relationships"""
    # Create a directed graph
    G = nx.DiGraph()
    
    # Group files by directory
    file_structure = {}
    for file in files:
        path_parts = file['path'].split('/')
        current_level = file_structure
        
        for i, part in enumerate(path_parts[:-1]):
            if part not in current_level:
                current_level[part] = {}
            current_level = current_level[part]
        
        # Add file to the structure
        file_name = path_parts[-1]
        current_level[file_name] = {
            'type': 'file',
            'language': file.get('language', 'unknown'),
            'size': file.get('size', 0)
        }
    
    # Add nodes and edges
    def add_nodes(structure, parent=None, prefix=""):
        for name, content in structure.items():
            node_id = f"{prefix}/{name}" if prefix else name
            
            if isinstance(content, dict) and content.get('type') == 'file':
                G.add_node(node_id, type='file', language=content['language'])
                if parent:
                    G.add_edge(parent, node_id)
            else:
                G.add_node(node_id, type='directory')
                if parent:
                    G.add_edge(parent, node_id)
                add_nodes(content, node_id, node_id)
    
    add_nodes(file_structure)
    
    # Analyze imports and dependencies
    import_patterns = {
        'python': [r'import\s+(\w+)', r'from\s+(\w+)'],
        'javascript': [r'import\s+.*\s+from\s+["\'](.+)["\']', r'require\(["\'](.+)["\']\)'],
        'typescript': [r'import\s+.*\s+from\s+["\'](.+)["\']'],
    }
    
    # Create visualization
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, k=2, iterations=50)
    
    # Draw nodes
    file_nodes = [n for n, d in G.nodes(data=True) if d.get('type') == 'file']
    dir_nodes = [n for n, d in G.nodes(data=True) if d.get('type') == 'directory']
    
    nx.draw_networkx_nodes(G, pos, nodelist=file_nodes, node_color='lightblue', 
                          node_size=500, node_shape='o')
    nx.draw_networkx_nodes(G, pos, nodelist=dir_nodes, node_color='lightgreen', 
                          node_size=700, node_shape='s')
    
    # Draw edges and labels
    nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, alpha=0.5)
    nx.draw_networkx_labels(G, pos, font_size=8)
    
    plt.title(f"Codebase Structure: {repo_name}")
    plt.axis('off')
    
    # Save to buffer
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
    img_buffer.seek(0)
    plt.close()
    
    return {
        'graph_data': {
            'nodes': list(G.nodes()),
            'edges': list(G.edges()),
            'file_count': len(file_nodes),
            'directory_count': len(dir_nodes)
        },
        'image': base64.b64encode(img_buffer.getvalue()).decode('utf-8')
    }


@router.post("/generate-project-docs")
async def generate_project_documentation(request: ProjectDocRequest):
    """Generate comprehensive project documentation with codebase map"""
    try:
        repo = github_client.get_repo(f"{request.owner}/{request.repo}")
        
        # Get repository files
        contents = repo.get_contents("", ref=request.branch)
        all_files = []
        
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path, ref=request.branch))
            else:
                all_files.append({
                    'path': file_content.path,
                    'name': file_content.name,
                    'size': file_content.size
                })
        
        # Generate documentation using Gemini
        model = genai.GenerativeModel('gemini-pro')
        
        # Analyze README if exists
        readme_content = ""
        try:
            readme = repo.get_readme()
            readme_content = base64.b64decode(readme.content).decode('utf-8')
        except:
            pass
        
        # Generate setup instructions
        setup_prompt = f"""Based on this repository structure and README, generate detailed setup instructions:

Repository: {request.owner}/{request.repo}
Main Language: {repo.language}
Description: {repo.description}

README Content:
{readme_content[:2000] if readme_content else "No README found"}

File Structure:
{json.dumps([f['path'] for f in all_files[:50]], indent=2)}

Please provide:
1. Prerequisites and system requirements
2. Step-by-step installation guide
3. Configuration instructions
4. How to run the project
5. Common troubleshooting tips
"""
        
        setup_response = model.generate_content(setup_prompt)
        setup_instructions = setup_response.text
        
        # Generate architecture documentation
        arch_prompt = f"""Analyze this repository and provide architecture documentation:

Repository: {request.owner}/{request.repo}
Files: {json.dumps([f['path'] for f in all_files[:100]], indent=2)}

Please provide:
1. High-level architecture overview
2. Key components and their responsibilities
3. Data flow and interactions
4. Technology stack
5. Design patterns used
"""
        
        arch_response = model.generate_content(arch_prompt)
        architecture_docs = arch_response.text
        
        # Generate codebase map
        codebase_map = None
        if request.include_codebase_map:
            codebase_map = generate_codebase_map(f"{request.owner}/{request.repo}", all_files)
        
        # Create PDF
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=1  # Center
        )
        
        story.append(Paragraph(f"{repo.name} Documentation", title_style))
        story.append(Spacer(1, 20))
        
        # Repository info
        info_text = f"""
        <b>Repository:</b> {request.owner}/{request.repo}<br/>
        <b>Language:</b> {repo.language or 'Not specified'}<br/>
        <b>Stars:</b> {repo.stargazers_count}<br/>
        <b>Description:</b> {repo.description or 'No description'}<br/>
        """
        story.append(Paragraph(info_text, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Setup Instructions
        if request.include_setup:
            story.append(Paragraph("Setup Instructions", styles['Heading2']))
            story.append(Spacer(1, 10))
            for paragraph in setup_instructions.split('\n\n'):
                if paragraph.strip():
                    story.append(Paragraph(paragraph, styles['Normal']))
                    story.append(Spacer(1, 10))
            story.append(PageBreak())
        
        # Architecture
        if request.include_architecture:
            story.append(Paragraph("Architecture Overview", styles['Heading2']))
            story.append(Spacer(1, 10))
            for paragraph in architecture_docs.split('\n\n'):
                if paragraph.strip():
                    story.append(Paragraph(paragraph, styles['Normal']))
                    story.append(Spacer(1, 10))
            story.append(PageBreak())
        
        # Codebase Map
        if request.include_codebase_map and codebase_map:
            story.append(Paragraph("Codebase Map", styles['Heading2']))
            story.append(Spacer(1, 10))
            
            # Add the image
            img_data = base64.b64decode(codebase_map['image'])
            img = Image(io.BytesIO(img_data), width=6*inch, height=4*inch)
            story.append(img)
            
            # Add statistics
            stats_text = f"""
            <b>Total Files:</b> {codebase_map['graph_data']['file_count']}<br/>
            <b>Total Directories:</b> {codebase_map['graph_data']['directory_count']}<br/>
            """
            story.append(Paragraph(stats_text, styles['Normal']))
        
        # Build PDF
        doc.build(story)
        pdf_buffer.seek(0)
        
        return {
            "pdf": base64.b64encode(pdf_buffer.getvalue()).decode('utf-8'),
            "setup_instructions": setup_instructions,
            "architecture_docs": architecture_docs,
            "codebase_map": codebase_map,
            "repository_info": {
                "name": repo.name,
                "owner": request.owner,
                "language": repo.language,
                "stars": repo.stargazers_count,
                "description": repo.description
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-codebase-map")
async def generate_codebase_map_endpoint(request: CodebaseMapRequest):
    """Generate just the codebase map visualization"""
    try:
        repo = github_client.get_repo(f"{request.owner}/{request.repo}")
        
        # Get all files
        contents = repo.get_contents("", ref=request.branch)
        all_files = []
        
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path, ref=request.branch))
            else:
                all_files.append({
                    'path': file_content.path,
                    'name': file_content.name,
                    'size': file_content.size,
                    'language': file_content.path.split('.')[-1] if '.' in file_content.path else 'unknown'
                })
        
        codebase_map = generate_codebase_map(f"{request.owner}/{request.repo}", all_files)
        
        return codebase_map
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat-with-repo")
async def chat_with_repository(repo_name: str, query: str):
    """Chat with a repository using RAG"""
    try:
        # Search for relevant code
        search_results = rag_engine.search_code(repo_name, query, k=5)
        
        if search_results:
            # Generate response with context
            response = rag_engine.generate_with_context(
                query=query,
                context=search_results,
                system_prompt="""You are a helpful assistant that answers questions about code repositories. 
                Use the provided code context to give accurate, specific answers. 
                Always reference the specific files and line numbers when possible."""
            )
            
            return {
                "response": response,
                "sources": search_results
            }
        else:
            # Fallback to general knowledge
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(f"Answer this question about the repository {repo_name}: {query}")
            
            return {
                "response": response.text,
                "sources": []
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 