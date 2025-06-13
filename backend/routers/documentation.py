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
from core.hybrid_engine import RAGEngine
from core.nlp_processor import NLPProcessor
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import re
from collections import defaultdict
from datetime import datetime

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

# Configure base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALLOWED_PATHS = [
    os.path.join(BASE_DIR, "frontend", "src"),
    os.path.join(BASE_DIR, "frontend", "public"),
    os.path.join(BASE_DIR, "backend"),
]

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
    """Generate a visual codebase map showing file relationships with multiple layout models and enhanced visuals"""
    # Create a directed graph
    G = nx.DiGraph()
    
    # Group files by directory with enhanced metadata
    file_structure = {}
    for file in files:
        path_parts = file['path'].split('/')
        current_level = file_structure
        
        for i, part in enumerate(path_parts[:-1]):
            if part not in current_level:
                current_level[part] = {}
            current_level = current_level[part]
        
        # Add file to the structure with enhanced metadata
        file_name = path_parts[-1]
        current_level[file_name] = {
            'type': 'file',
            'language': file.get('language', 'unknown'),
            'size': file.get('size', 0),
            'complexity': file.get('complexity', 0),
            'last_modified': file.get('last_modified', ''),
            'dependencies': file.get('dependencies', [])
        }
    
    # Add nodes and edges with enhanced attributes
    def add_nodes(structure, parent=None, prefix=""):
        for name, content in structure.items():
            node_id = f"{prefix}/{name}" if prefix else name
            
            if isinstance(content, dict) and content.get('type') == 'file':
                G.add_node(node_id, 
                    type='file',
                    language=content['language'],
                    size=content['size'],
                    complexity=content['complexity'],
                    last_modified=content['last_modified'],
                    dependencies=content['dependencies']
                )
                if parent:
                    G.add_edge(parent, node_id, type='contains')
            else:
                G.add_node(node_id, type='directory')
                if parent:
                    G.add_edge(parent, node_id, type='contains')
                add_nodes(content, node_id, node_id)
    
    add_nodes(file_structure)
    
    # Create three different visualizations with enhanced layouts
    layouts = {
        'spring': nx.spring_layout(G, k=2, iterations=50, seed=42),
        'circular': nx.circular_layout(G, scale=2),
        'kamada_kawai': nx.kamada_kawai_layout(G, scale=2)
    }
    
    # Create figure with subplots and enhanced styling
    plt.style.use('seaborn')
    fig = plt.figure(figsize=(24, 18))
    
    # Define enhanced color schemes with gradients
    color_schemes = {
        'primary': {
            'file': ['#3b82f6', '#60a5fa', '#93c5fd'],      # Blue gradient
            'directory': ['#10b981', '#34d399', '#6ee7b7'],  # Green gradient
            'edge': ['#94a3b8', '#cbd5e1', '#e2e8f0'],      # Gray gradient
            'background': '#f8fafc'                          # Light gray
        },
        'secondary': {
            'file': ['#8b5cf6', '#a78bfa', '#c4b5fd'],      # Purple gradient
            'directory': ['#f59e0b', '#fbbf24', '#fcd34d'],  # Amber gradient
            'edge': ['#64748b', '#94a3b8', '#cbd5e1'],      # Slate gradient
            'background': '#f1f5f9'                          # Slate light
        },
        'tertiary': {
            'file': ['#ec4899', '#f472b6', '#f9a8d4'],      # Pink gradient
            'directory': ['#14b8a6', '#2dd4bf', '#5eead4'],  # Teal gradient
            'edge': ['#475569', '#64748b', '#94a3b8'],      # Slate dark gradient
            'background': '#f8fafc'                          # Light gray
        }
    }
    
    # Create three subplots with enhanced layouts
    for idx, (layout_name, layout) in enumerate(layouts.items(), 1):
        ax = fig.add_subplot(1, 3, idx)
        
        # Get color scheme
        colors = color_schemes[list(color_schemes.keys())[idx-1]]
        
        # Draw nodes with enhanced styling
        file_nodes = [n for n, d in G.nodes(data=True) if d.get('type') == 'file']
        dir_nodes = [n for n, d in G.nodes(data=True) if d.get('type') == 'directory']
        
        # Draw file nodes with size based on complexity
        file_sizes = [G.nodes[n].get('complexity', 1) * 200 for n in file_nodes]
        nx.draw_networkx_nodes(
            G, layout, 
            nodelist=file_nodes,
            node_color=colors['file'][0],
            node_size=file_sizes,
            node_shape='o',
            alpha=0.8,
            ax=ax,
            edgecolors=colors['file'][1],
            linewidths=2
        )
        
        # Draw directory nodes with size based on number of children
        dir_sizes = [len(list(G.successors(n))) * 100 for n in dir_nodes]
        nx.draw_networkx_nodes(
            G, layout,
            nodelist=dir_nodes,
            node_color=colors['directory'][0],
            node_size=dir_sizes,
            node_shape='s',
            alpha=0.8,
            ax=ax,
            edgecolors=colors['directory'][1],
            linewidths=2
        )
        
        # Draw edges with enhanced styling
        edge_colors = [colors['edge'][0] if G[u][v].get('type') == 'contains' else colors['edge'][1] 
                      for u, v in G.edges()]
        nx.draw_networkx_edges(
            G, layout,
            edge_color=edge_colors,
            arrows=True,
            arrowsize=20,
            width=2,
            alpha=0.6,
            connectionstyle='arc3,rad=0.2',
            ax=ax,
            edge_cmap=plt.cm.Blues
        )
        
        # Draw labels with enhanced styling
        labels = {node: node.split('/')[-1] for node in G.nodes()}
        nx.draw_networkx_labels(
            G, layout,
            labels=labels,
            font_size=10,
            font_family='sans-serif',
            font_weight='bold',
            ax=ax,
            bbox=dict(facecolor='white', edgecolor='none', alpha=0.7, pad=3)
        )
        
        # Set background color and style
        ax.set_facecolor(colors['background'])
        ax.grid(True, linestyle='--', alpha=0.3)
        
        # Add title with enhanced styling
        ax.set_title(
            f"{layout_name.title()} Layout",
            fontsize=14,
            pad=20,
            fontweight='bold',
            color=colors['file'][0]
        )
        
        # Remove axis
        ax.axis('off')
    
    # Adjust layout with more padding
    plt.tight_layout(pad=4.0)
    
    # Save to buffer with enhanced quality
    img_buffer = io.BytesIO()
    plt.savefig(
        img_buffer,
        format='png',
        dpi=300,
        bbox_inches='tight',
        facecolor='white',
        edgecolor='none',
        transparent=False
    )
    img_buffer.seek(0)
    plt.close()
    
    # Calculate enhanced graph metrics
    metrics = {
        'density': nx.density(G),
        'average_clustering': nx.average_clustering(G),
        'average_shortest_path': nx.average_shortest_path_length(G) if nx.is_connected(G) else float('inf'),
        'diameter': nx.diameter(G) if nx.is_connected(G) else float('inf'),
        'average_degree': sum(dict(G.degree()).values()) / G.number_of_nodes(),
        'centrality': nx.degree_centrality(G),
        'clustering': nx.clustering(G),
        'pagerank': nx.pagerank(G)
    }
    
    return {
        'graph_data': {
            'nodes': list(G.nodes()),
            'edges': list(G.edges()),
            'file_count': len(file_nodes),
            'directory_count': len(dir_nodes),
            'metrics': metrics,
            'node_attributes': {node: G.nodes[node] for node in G.nodes()}
        },
        'image': base64.b64encode(img_buffer.getvalue()).decode('utf-8')
    }


@router.post("/generate-project-docs")
async def generate_project_documentation(request: ProjectDocRequest):
    """Generate comprehensive project documentation with codebase map"""
    try:
        repo = github_client.get_repo(f"{request.owner}/{request.repo}")
        
        # Get repository files with enhanced context
        contents = repo.get_contents("", ref=request.branch)
        all_files = []
        file_context = {
            'total_files': 0,
            'languages': defaultdict(int),
            'file_types': defaultdict(int),
            'dependencies': set(),
            'endpoints': [],
            'models': [],
            'complexity_scores': defaultdict(float)
        }
        
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path, ref=request.branch))
            else:
                try:
                    content = base64.b64decode(file_content.content).decode('utf-8')
                    file_info = {
                        'path': file_content.path,
                        'name': file_content.name,
                        'size': file_content.size,
                        'content': content,
                        'language': file_content.name.split('.')[-1] if '.' in file_content.name else 'unknown'
                    }
                    
                    # Update context information
                    file_context['total_files'] += 1
                    file_context['languages'][file_info['language']] += 1
                    file_context['file_types'][file_info['name'].split('.')[-1]] += 1
                    
                    # Analyze file content for context
                    if file_info['language'] == 'py':
                        # Extract dependencies
                        imports = re.findall(r'(?:from|import)\s+(\w+)', content)
                        file_context['dependencies'].update(imports)
                        
                        # Extract endpoints
                        if '@router' in content or '@app' in content:
                            endpoints = re.findall(r'@(?:router|app)\.(?:get|post|put|delete)\s*\([\'"]([^\'"]+)[\'"]', content)
                            file_context['endpoints'].extend(endpoints)
                        
                        # Extract models
                        if 'class' in content and ('BaseModel' in content or 'SQLModel' in content):
                            models = re.findall(r'class\s+(\w+)\s*\(.*?BaseModel', content)
                            file_context['models'].extend(models)
                    
                    # Calculate complexity
                    complexity = nlp_processor.analyze_code_structure(content)
                    if complexity and 'complexity' in complexity:
                        file_context['complexity_scores'][file_info['path']] = complexity['complexity'].get('cyclomatic', 0)
                    
                    all_files.append(file_info)
                except Exception as e:
                    print(f"Error reading file {file_content.path}: {str(e)}")
        
        # Initialize RAG engine with enhanced context
        rag_engine = RAGEngine(api_key=os.getenv("GEMINI_API_KEY"))
        
        # Index code with enhanced analysis and context
        rag_engine.index_code(f"{request.owner}/{request.repo}", all_files)
        
        # Generate documentation using enhanced RAG with context
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Analyze README if exists
        readme_content = ""
        try:
            readme = repo.get_readme()
            readme_content = base64.b64decode(readme.content).decode('utf-8')
        except:
            pass
        
        # Generate setup instructions with enhanced context
        setup_prompt = f"""Based on this repository structure and README, generate detailed setup instructions:

Repository: {request.owner}/{request.repo}
Main Language: {repo.language}
Description: {repo.description}

Repository Context:
- Total Files: {file_context['total_files']}
- Languages: {dict(file_context['languages'])}
- File Types: {dict(file_context['file_types'])}
- Dependencies: {list(file_context['dependencies'])}
- Endpoints: {file_context['endpoints']}
- Models: {file_context['models']}
- Average Complexity: {sum(file_context['complexity_scores'].values()) / len(file_context['complexity_scores']) if file_context['complexity_scores'] else 0}

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
6. Development environment setup
7. Testing instructions
8. Deployment guidelines
"""
        
        setup_response = model.generate_content(setup_prompt)
        setup_instructions = setup_response.text
        
        # Generate architecture documentation with enhanced context
        arch_prompt = f"""Analyze this repository and provide comprehensive architecture documentation:

Repository: {request.owner}/{request.repo}
Repository Context:
- Total Files: {file_context['total_files']}
- Languages: {dict(file_context['languages'])}
- File Types: {dict(file_context['file_types'])}
- Dependencies: {list(file_context['dependencies'])}
- Endpoints: {file_context['endpoints']}
- Models: {file_context['models']}
- Average Complexity: {sum(file_context['complexity_scores'].values()) / len(file_context['complexity_scores']) if file_context['complexity_scores'] else 0}

Files: {json.dumps([f['path'] for f in all_files[:100]], indent=2)}

Please provide:
1. High-level architecture overview
2. Key components and their responsibilities
3. Data flow and interactions
4. Technology stack
5. Design patterns used
6. Security considerations
7. Performance considerations
8. Scalability aspects
9. Integration points
10. Future improvement suggestions
"""
        
        arch_response = model.generate_content(arch_prompt)
        architecture_docs = arch_response.text
        
        # Generate codebase map with enhanced context
        codebase_map = None
        if request.include_codebase_map:
            codebase_map = generate_codebase_map(f"{request.owner}/{request.repo}", all_files)
            # Add context information to codebase map
            if codebase_map:
                codebase_map['context'] = {
                    'languages': dict(file_context['languages']),
                    'dependencies': list(file_context['dependencies']),
                    'endpoints': file_context['endpoints'],
                    'models': file_context['models'],
                    'complexity': {
                        'average': sum(file_context['complexity_scores'].values()) / len(file_context['complexity_scores']) if file_context['complexity_scores'] else 0,
                        'highest': max(file_context['complexity_scores'].items(), key=lambda x: x[1]) if file_context['complexity_scores'] else None
                    }
                }
        
        # Create PDF with enhanced content and context
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        styles = getSampleStyleSheet()
        
        # Define modern color scheme
        colors_dict = {
            'primary': colors.HexColor('#2563eb'),      # Modern blue
            'secondary': colors.HexColor('#64748b'),    # Slate gray
            'accent': colors.HexColor('#0ea5e9'),       # Sky blue
            'text': colors.HexColor('#1e293b'),         # Dark slate
            'light': colors.HexColor('#f8fafc'),        # Light background
            'success': colors.HexColor('#22c55e'),      # Green
            'warning': colors.HexColor('#f59e0b'),      # Amber
            'error': colors.HexColor('#ef4444'),        # Red
        }
        
        # Define custom styles for better formatting
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=32,
            textColor=colors_dict['primary'],
            spaceAfter=30,
            alignment=1,  # Center
            fontName='Helvetica-Bold',
            leading=40
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors_dict['secondary'],
            spaceAfter=20,
            alignment=1,  # Center
            fontName='Helvetica',
            leading=24
        )
        
        heading2_style = ParagraphStyle(
            'CustomHeading2',
            parent=styles['Heading2'],
            fontSize=20,
            textColor=colors_dict['primary'],
            spaceBefore=25,
            spaceAfter=15,
            fontName='Helvetica-Bold',
            leading=28,
            borderWidth=1,
            borderColor=colors_dict['accent'],
            borderPadding=5,
            borderRadius=5
        )
        
        bullet_style = ParagraphStyle(
            'CustomBullet',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors_dict['text'],
            leftIndent=20,
            spaceBefore=5,
            spaceAfter=5,
            fontName='Helvetica',
            leading=16
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors_dict['text'],
            spaceBefore=5,
            spaceAfter=5,
            fontName='Helvetica',
            leading=16
        )
        
        code_style = ParagraphStyle(
            'CustomCode',
            parent=styles['Code'],
            fontSize=10,
            textColor=colors_dict['text'],
            backColor=colors_dict['light'],
            fontName='Courier',
            leading=14,
            leftIndent=20,
            rightIndent=20,
            borderWidth=1,
            borderColor=colors_dict['secondary'],
            borderPadding=5,
            borderRadius=3
        )
        
        story = []
        
        # Add a decorative header
        def create_header():
            header = Table([
                [Paragraph(f"{repo.name} Documentation", title_style)],
                [Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}", subtitle_style)]
            ], colWidths=[doc.width])
            header.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('BACKGROUND', (0, 0), (-1, 0), colors_dict['primary']),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('BACKGROUND', (0, 1), (-1, 1), colors_dict['light']),
                ('TEXTCOLOR', (0, 1), (-1, 1), colors_dict['secondary']),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, 0), 32),
                ('FONTSIZE', (0, 1), (-1, 1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 20),
                ('TOPPADDING', (0, 1), (-1, 1), 10),
                ('BOTTOMPADDING', (0, 1), (-1, 1), 10),
            ]))
            return header
        
        story.append(create_header())
        story.append(Spacer(1, 30))
        
        # Repository Overview with enhanced styling
        story.append(Paragraph("Repository Overview", heading2_style))
        overview_data = [
            ["Repository", f"{request.owner}/{request.repo}"],
            ["Language", repo.language or 'Not specified'],
            ["Stars", str(repo.stargazers_count)],
            ["Description", repo.description or 'No description'],
            ["Last Updated", repo.updated_at.strftime('%Y-%m-%d')],
            ["License", repo.license.name if repo.license else 'Not specified']
        ]
        
        overview_table = Table(overview_data, colWidths=[doc.width/3, doc.width*2/3])
        overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors_dict['light']),
            ('TEXTCOLOR', (0, 0), (0, -1), colors_dict['primary']),
            ('TEXTCOLOR', (1, 0), (1, -1), colors_dict['text']),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors_dict['secondary']),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ]))
        story.append(overview_table)
        story.append(Spacer(1, 20))
        
        # Codebase Statistics with enhanced styling
        story.append(Paragraph("Codebase Statistics", heading2_style))
        stats_data = [
            ["Total Files", str(file_context['total_files'])],
            ["Languages", ', '.join(f"{k}: {v}" for k, v in file_context['languages'].items())],
            ["Dependencies", ', '.join(file_context['dependencies'])],
            ["Endpoints", ', '.join(file_context['endpoints'])],
            ["Models", ', '.join(file_context['models'])],
            ["Average Complexity", f"{sum(file_context['complexity_scores'].values()) / len(file_context['complexity_scores']) if file_context['complexity_scores'] else 0:.2f}"]
        ]
        
        stats_table = Table(stats_data, colWidths=[doc.width/3, doc.width*2/3])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors_dict['light']),
            ('TEXTCOLOR', (0, 0), (0, -1), colors_dict['primary']),
            ('TEXTCOLOR', (1, 0), (1, -1), colors_dict['text']),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors_dict['secondary']),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ]))
        story.append(stats_table)
        story.append(Spacer(1, 20))
        
        # Setup Instructions with enhanced styling
        if request.include_setup:
            story.append(Paragraph("Setup Instructions", heading2_style))
            setup_sections = setup_instructions.split('\n\n')
            for section in setup_sections:
                if section.strip():
                    if '\n' in section:
                        lines = section.split('\n')
                        for line in lines:
                            if line.strip():
                                story.append(Paragraph(f"• {line.strip()}", bullet_style))
                    else:
                        story.append(Paragraph(section.strip(), normal_style))
            story.append(PageBreak())
        
        # Architecture with enhanced styling
        if request.include_architecture:
            story.append(Paragraph("Architecture Overview", heading2_style))
            arch_sections = architecture_docs.split('\n\n')
            for section in arch_sections:
                if section.strip():
                    if '\n' in section:
                        lines = section.split('\n')
                        for line in lines:
                            if line.strip():
                                story.append(Paragraph(f"• {line.strip()}", bullet_style))
                    else:
                        story.append(Paragraph(section.strip(), normal_style))
            story.append(PageBreak())
        
        # Codebase Map with enhanced styling
        if request.include_codebase_map and codebase_map:
            story.append(Paragraph("Codebase Map", heading2_style))
            story.append(Spacer(1, 10))
            
            # Add the image with a border
            img_data = base64.b64decode(codebase_map['image'])
            img = Image(io.BytesIO(img_data), width=6*inch, height=4*inch)
            img_table = Table([[img]], colWidths=[doc.width])
            img_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 1, colors_dict['secondary']),
                ('BACKGROUND', (0, 0), (-1, -1), colors_dict['light']),
                ('PADDING', (0, 0), (-1, -1), 10),
            ]))
            story.append(img_table)
            
            # Add statistics with enhanced styling
            story.append(Paragraph("Codebase Statistics", heading2_style))
            codebase_stats_data = [
                ["Total Files", str(codebase_map['graph_data']['file_count'])],
                ["Total Directories", str(codebase_map['graph_data']['directory_count'])],
                ["Main Language", repo.language or 'Not specified'],
                ["File Types", ', '.join(f"{k}: {v}" for k, v in codebase_map['graph_data'].get('file_types', {}).items())],
                ["Dependencies", ', '.join(file_context['dependencies'])],
                ["Endpoints", ', '.join(file_context['endpoints'])],
                ["Models", ', '.join(file_context['models'])],
                ["Average Complexity", f"{sum(file_context['complexity_scores'].values()) / len(file_context['complexity_scores']) if file_context['complexity_scores'] else 0:.2f}"]
            ]
            
            codebase_stats_table = Table(codebase_stats_data, colWidths=[doc.width/3, doc.width*2/3])
            codebase_stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors_dict['light']),
                ('TEXTCOLOR', (0, 0), (0, -1), colors_dict['primary']),
                ('TEXTCOLOR', (1, 0), (1, -1), colors_dict['text']),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors_dict['secondary']),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ]))
            story.append(codebase_stats_table)
        
        # Add footer with page numbers
        def add_page_number(canvas, doc):
            canvas.saveState()
            canvas.setFont('Helvetica', 9)
            canvas.setFillColor(colors_dict['secondary'])
            page_number_text = f"Page {doc.page}"
            canvas.drawRightString(doc.pagesize[0] - 72, 50, page_number_text)
            canvas.restoreState()
        
        # Build PDF with page numbers
        doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
        pdf_buffer.seek(0)
        
        # Convert PDF to base64
        pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')
        
        return {
            "pdf": pdf_base64,
            "setup_instructions": setup_instructions,
            "architecture_docs": architecture_docs,
            "codebase_map": codebase_map,
            "repository_info": {
                "name": repo.name,
                "owner": request.owner,
                "language": repo.language,
                "stars": repo.stargazers_count,
                "description": repo.description,
                "last_updated": repo.updated_at.strftime('%Y-%m-%d'),
                "license": repo.license.name if repo.license else None,
                "context": {
                    "total_files": file_context['total_files'],
                    "languages": dict(file_context['languages']),
                    "dependencies": list(file_context['dependencies']),
                    "endpoints": file_context['endpoints'],
                    "models": file_context['models'],
                    "complexity": {
                        "average": sum(file_context['complexity_scores'].values()) / len(file_context['complexity_scores']) if file_context['complexity_scores'] else 0,
                        "highest": max(file_context['complexity_scores'].items(), key=lambda x: x[1]) if file_context['complexity_scores'] else None
                    }
                }
            }
        }
        
    except Exception as e:
        print(f"Error generating documentation: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
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
    """Chat with a repository using RAG with enhanced context"""
    try:
        # Get repository context
        owner, repo = repo_name.split('/')
        repo_obj = github_client.get_repo(repo_name)
        
        # Get repository files for context
        contents = repo_obj.get_contents("")
        file_context = {
            'total_files': 0,
            'languages': defaultdict(int),
            'dependencies': set(),
            'endpoints': [],
            'models': [],
            'complexity_scores': defaultdict(float)
        }
        
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repo_obj.get_contents(file_content.path))
            else:
                try:
                    content = base64.b64decode(file_content.content).decode('utf-8')
                    file_context['total_files'] += 1
                    file_context['languages'][file_content.name.split('.')[-1]] += 1
                    
                    # Extract context from Python files
                    if file_content.name.endswith('.py'):
                        imports = re.findall(r'(?:from|import)\s+(\w+)', content)
                        file_context['dependencies'].update(imports)
                        
                        if '@router' in content or '@app' in content:
                            endpoints = re.findall(r'@(?:router|app)\.(?:get|post|put|delete)\s*\([\'"]([^\'"]+)[\'"]', content)
                            file_context['endpoints'].extend(endpoints)
                        
                        if 'class' in content and ('BaseModel' in content or 'SQLModel' in content):
                            models = re.findall(r'class\s+(\w+)\s*\(.*?BaseModel', content)
                            file_context['models'].extend(models)
                        
                        # Calculate complexity
                        complexity = nlp_processor.analyze_code_structure(content)
                        if complexity and 'complexity' in complexity:
                            file_context['complexity_scores'][file_content.path] = complexity['complexity'].get('cyclomatic', 0)
                except Exception as e:
                    print(f"Error reading file {file_content.path}: {str(e)}")
        
        # Search for relevant code with context
        search_results = rag_engine.search_code(repo_name, query, k=5)
        
        if search_results:
            # Generate response with enhanced context
            response = rag_engine.generate_with_context(
                query=query,
                context=search_results,
                system_prompt=f"""You are a helpful assistant that answers questions about code repositories. 
                Use the provided code context to give accurate, specific answers. 
                Always reference the specific files and line numbers when possible.
                
                Repository Context:
                - Total Files: {file_context['total_files']}
                - Languages: {dict(file_context['languages'])}
                - Dependencies: {list(file_context['dependencies'])}
                - Endpoints: {file_context['endpoints']}
                - Models: {file_context['models']}
                - Average Complexity: {sum(file_context['complexity_scores'].values()) / len(file_context['complexity_scores']) if file_context['complexity_scores'] else 0}
                """
            )
            
            return {
                "response": response,
                "sources": search_results,
                "context": {
                    "total_files": file_context['total_files'],
                    "languages": dict(file_context['languages']),
                    "dependencies": list(file_context['dependencies']),
                    "endpoints": file_context['endpoints'],
                    "models": file_context['models'],
                    "complexity": {
                        "average": sum(file_context['complexity_scores'].values()) / len(file_context['complexity_scores']) if file_context['complexity_scores'] else 0,
                        "highest": max(file_context['complexity_scores'].items(), key=lambda x: x[1]) if file_context['complexity_scores'] else None
                    }
                }
            }
        else:
            # Fallback to general knowledge with context
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content(
                f"""Answer this question about the repository {repo_name}:
                {query}
                
                Repository Context:
                - Total Files: {file_context['total_files']}
                - Languages: {dict(file_context['languages'])}
                - Dependencies: {list(file_context['dependencies'])}
                - Endpoints: {file_context['endpoints']}
                - Models: {file_context['models']}
                - Average Complexity: {sum(file_context['complexity_scores'].values()) / len(file_context['complexity_scores']) if file_context['complexity_scores'] else 0}
                """
            )
            
            return {
                "response": response.text,
                "sources": [],
                "context": {
                    "total_files": file_context['total_files'],
                    "languages": dict(file_context['languages']),
                    "dependencies": list(file_context['dependencies']),
                    "endpoints": file_context['endpoints'],
                    "models": file_context['models'],
                    "complexity": {
                        "average": sum(file_context['complexity_scores'].values()) / len(file_context['complexity_scores']) if file_context['complexity_scores'] else 0,
                        "highest": max(file_context['complexity_scores'].items(), key=lambda x: x[1]) if file_context['complexity_scores'] else None
                    }
                }
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Add file content endpoint
@router.get("/file-content")
async def get_file_content(path: str):
    try:
        # Normalize path to prevent directory traversal
        normalized_path = os.path.normpath(path)
        if normalized_path.startswith('..') or normalized_path.startswith('/'):
            raise HTTPException(status_code=400, detail="Invalid file path")
        
        # Check if path is within allowed directories
        full_path = os.path.join(BASE_DIR, normalized_path)
        is_allowed = any(full_path.startswith(allowed_path) for allowed_path in ALLOWED_PATHS)
        if not is_allowed:
            raise HTTPException(status_code=403, detail="Access to this file path is not allowed")
        
        # Check if file exists
        if not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail=f"File not found: {normalized_path}")
        
        # Check if it's a file
        if not os.path.isfile(full_path):
            raise HTTPException(status_code=400, detail=f"Path is not a file: {normalized_path}")
        
        # Get file extension
        _, ext = os.path.splitext(full_path)
        
        # Read file content based on file type
        try:
            if ext.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
                # For binary files, return base64 encoded content
                with open(full_path, 'rb') as f:
                    content = base64.b64encode(f.read()).decode('utf-8')
                content_type = 'binary'
            else:
                # For text files, try different encodings
                encodings = ['utf-8', 'latin-1', 'cp1252']
                content = None
                for encoding in encodings:
                    try:
                        with open(full_path, 'r', encoding=encoding) as f:
                            content = f.read()
                        break
                    except UnicodeDecodeError:
                        continue
                
                if content is None:
                    raise HTTPException(status_code=400, detail=f"Could not decode file content: {normalized_path}")
                content_type = 'text'
            
            return {
                "path": normalized_path,
                "content": content,
                "size": os.path.getsize(full_path),
                "type": content_type,
                "extension": ext.lower(),
                "last_modified": datetime.fromtimestamp(os.path.getmtime(full_path)).isoformat()
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}") 