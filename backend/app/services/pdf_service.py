import os
import requests
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from app.config import config
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from typing import Dict, List, Any, Optional
from datetime import datetime

def generate_repo_pdf(repo_url: str):
    # Fetch repo details from GitHub
    repo_api_url = repo_url.replace('https://github.com/', 'https://api.github.com/repos/')
    headers = {"Authorization": f"token {config.GITHUB_TOKEN}"}
    resp = requests.get(repo_api_url, headers=headers)
    if resp.status_code != 200:
        return None
    repo = resp.json()
    name = repo.get('full_name', '')
    desc = repo.get('description', '')
    lang = repo.get('language', 'Unknown')
    # Simple run instructions
    instructions = f"To run this project, clone the repo and follow the README. If it's Python, install requirements.txt. If Node, run npm install."
    # Generate PDF
    os.makedirs('backend/static', exist_ok=True)
    pdf_path = f"backend/static/{name.replace('/', '_')}.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(72, 720, name)
    c.setFont("Helvetica", 12)
    c.drawString(72, 700, f"Description: {desc}")
    c.drawString(72, 680, f"Language: {lang}")
    c.drawString(72, 660, f"Repo URL: {repo_url}")
    c.drawString(72, 640, f"Instructions: {instructions}")
    c.save()
    return f"/static/{name.replace('/', '_')}.pdf"

class PDFService:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.darkblue
        )
        
        self.subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=8,
            spaceBefore=12,
            textColor=colors.darkgreen
        )
        
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            leading=14
        )
        
        self.code_style = ParagraphStyle(
            'CustomCode',
            parent=self.styles['Code'],
            fontSize=9,
            spaceAfter=6,
            fontName='Courier',
            leftIndent=20,
            rightIndent=20,
            backColor=colors.lightgrey
        )

    def generate_repository_documentation(self, repo_info: Dict[str, Any], files: List[Dict[str, Any]], 
                                        structure: Dict[str, Any], output_path: str) -> str:
        """Generate comprehensive PDF documentation for a repository"""
        try:
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            story = []
            
            # Title page
            story.extend(self._create_title_page(repo_info))
            story.append(PageBreak())
            
            # Table of contents
            story.extend(self._create_table_of_contents())
            story.append(PageBreak())
            
            # Repository overview
            story.extend(self._create_repository_overview(repo_info))
            story.append(PageBreak())
            
            # Project structure
            story.extend(self._create_project_structure(structure))
            story.append(PageBreak())
            
            # Installation instructions
            story.extend(self._create_installation_instructions(repo_info))
            story.append(PageBreak())
            
            # Code documentation
            story.extend(self._create_code_documentation(files))
            story.append(PageBreak())
            
            # API documentation (if applicable)
            story.extend(self._create_api_documentation(files))
            story.append(PageBreak())
            
            # Usage examples
            story.extend(self._create_usage_examples(repo_info))
            
            # Build PDF
            doc.build(story)
            return output_path
            
        except Exception as e:
            print(f"Error generating PDF: {e}")
            raise

    def _create_title_page(self, repo_info: Dict[str, Any]) -> List:
        """Create the title page"""
        elements = []
        
        # Title
        title = Paragraph(f"<b>{repo_info.get('name', 'Repository')}</b>", self.title_style)
        elements.append(title)
        elements.append(Spacer(1, 30))
        
        # Subtitle
        subtitle = Paragraph("Technical Documentation", self.heading_style)
        elements.append(subtitle)
        elements.append(Spacer(1, 50))
        
        # Repository details
        details_data = [
            ["Repository Name", repo_info.get('name', 'N/A')],
            ["Full Name", repo_info.get('full_name', 'N/A')],
            ["Description", repo_info.get('description', 'No description available')],
            ["Language", repo_info.get('language', 'N/A')],
            ["Stars", str(repo_info.get('stars', 0))],
            ["Forks", str(repo_info.get('forks', 0))],
            ["Created", repo_info.get('created_at', 'N/A')],
            ["Last Updated", repo_info.get('updated_at', 'N/A')],
            ["License", repo_info.get('license', 'N/A')],
        ]
        
        details_table = Table(details_data, colWidths=[2*inch, 4*inch])
        details_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(details_table)
        elements.append(Spacer(1, 30))
        
        # Generated date
        generated_date = Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", self.body_style)
        elements.append(generated_date)
        
        return elements

    def _create_table_of_contents(self) -> List:
        """Create table of contents"""
        elements = []
        
        toc_title = Paragraph("Table of Contents", self.heading_style)
        elements.append(toc_title)
        elements.append(Spacer(1, 20))
        
        toc_items = [
            "1. Repository Overview",
            "2. Project Structure",
            "3. Installation Instructions",
            "4. Code Documentation",
            "5. API Documentation",
            "6. Usage Examples"
        ]
        
        for item in toc_items:
            toc_item = Paragraph(item, self.body_style)
            elements.append(toc_item)
            elements.append(Spacer(1, 8))
        
        return elements

    def _create_repository_overview(self, repo_info: Dict[str, Any]) -> List:
        """Create repository overview section"""
        elements = []
        
        # Section title
        title = Paragraph("1. Repository Overview", self.heading_style)
        elements.append(title)
        elements.append(Spacer(1, 20))
        
        # Description
        description = repo_info.get('description', 'No description available')
        desc_para = Paragraph(f"<b>Description:</b> {description}", self.body_style)
        elements.append(desc_para)
        elements.append(Spacer(1, 15))
        
        # Key features
        features_title = Paragraph("Key Features:", self.subheading_style)
        elements.append(features_title)
        
        features = [
            f"• Primary Language: {repo_info.get('language', 'N/A')}",
            f"• Stars: {repo_info.get('stars', 0)}",
            f"• Forks: {repo_info.get('forks', 0)}",
            f"• Open Issues: {repo_info.get('open_issues', 0)}",
            f"• License: {repo_info.get('license', 'N/A')}",
            f"• Default Branch: {repo_info.get('default_branch', 'main')}"
        ]
        
        for feature in features:
            feature_para = Paragraph(feature, self.body_style)
            elements.append(feature_para)
            elements.append(Spacer(1, 5))
        
        # Topics/Tags
        topics = repo_info.get('topics', [])
        if topics:
            elements.append(Spacer(1, 10))
            topics_title = Paragraph("Topics:", self.subheading_style)
            elements.append(topics_title)
            
            topics_text = ", ".join(topics)
            topics_para = Paragraph(topics_text, self.body_style)
            elements.append(topics_para)
        
        return elements

    def _create_project_structure(self, structure: Dict[str, Any]) -> List:
        """Create project structure section"""
        elements = []
        
        # Section title
        title = Paragraph("2. Project Structure", self.heading_style)
        elements.append(title)
        elements.append(Spacer(1, 20))
        
        # Structure description
        desc = Paragraph("The project follows a standard directory structure:", self.body_style)
        elements.append(desc)
        elements.append(Spacer(1, 15))
        
        # Create structure tree
        structure_text = self._format_structure_tree(structure.get('structure', {}))
        structure_para = Paragraph(f"<pre>{structure_text}</pre>", self.code_style)
        elements.append(structure_para)
        
        return elements

    def _create_installation_instructions(self, repo_info: Dict[str, Any]) -> List:
        """Create installation instructions section"""
        elements = []
        
        # Section title
        title = Paragraph("3. Installation Instructions", self.heading_style)
        elements.append(title)
        elements.append(Spacer(1, 20))
        
        # Prerequisites
        prereq_title = Paragraph("Prerequisites:", self.subheading_style)
        elements.append(prereq_title)
        
        language = repo_info.get('language', 'Unknown')
        prereqs = self._get_prerequisites(language)
        
        for prereq in prereqs:
            prereq_para = Paragraph(f"• {prereq}", self.body_style)
            elements.append(prereq_para)
            elements.append(Spacer(1, 5))
        
        elements.append(Spacer(1, 15))
        
        # Installation steps
        install_title = Paragraph("Installation Steps:", self.subheading_style)
        elements.append(install_title)
        
        install_steps = [
            "1. Clone the repository:",
            f"   git clone https://github.com/{repo_info.get('full_name', 'user/repo')}.git",
            "",
            "2. Navigate to the project directory:",
            f"   cd {repo_info.get('name', 'repo')}",
            "",
            "3. Install dependencies:",
            self._get_install_command(language),
            "",
            "4. Run the application:",
            self._get_run_command(language)
        ]
        
        for step in install_steps:
            step_para = Paragraph(step, self.code_style if step.startswith('   ') or step.startswith('   ') else self.body_style)
            elements.append(step_para)
            elements.append(Spacer(1, 3))
        
        return elements

    def _create_code_documentation(self, files: List[Dict[str, Any]]) -> List:
        """Create code documentation section"""
        elements = []
        
        # Section title
        title = Paragraph("4. Code Documentation", self.heading_style)
        elements.append(title)
        elements.append(Spacer(1, 20))
        
        # Document each file
        for file_info in files:
            if file_info.get('type') == 'file' and file_info.get('content'):
                # File header
                file_title = Paragraph(f"File: {file_info['name']}", self.subheading_style)
                elements.append(file_title)
                
                # File content (truncated if too long)
                content = file_info['content']
                if len(content) > 1000:
                    content = content[:1000] + "\n... (content truncated)"
                
                content_para = Paragraph(f"<pre>{content}</pre>", self.code_style)
                elements.append(content_para)
                elements.append(Spacer(1, 15))
        
        return elements

    def _create_api_documentation(self, files: List[Dict[str, Any]]) -> List:
        """Create API documentation section"""
        elements = []
        
        # Section title
        title = Paragraph("5. API Documentation", self.heading_style)
        elements.append(title)
        elements.append(Spacer(1, 20))
        
        # Check if there are API-related files
        api_files = [f for f in files if any(keyword in f.get('name', '').lower() 
                                            for keyword in ['api', 'route', 'endpoint', 'controller'])]
        
        if api_files:
            for file_info in api_files:
                file_title = Paragraph(f"API File: {file_info['name']}", self.subheading_style)
                elements.append(file_title)
                
                if file_info.get('content'):
                    content = file_info['content'][:500] + "..." if len(file_info['content']) > 500 else file_info['content']
                    content_para = Paragraph(f"<pre>{content}</pre>", self.code_style)
                    elements.append(content_para)
                    elements.append(Spacer(1, 15))
        else:
            no_api = Paragraph("No specific API documentation found in this repository.", self.body_style)
            elements.append(no_api)
        
        return elements

    def _create_usage_examples(self, repo_info: Dict[str, Any]) -> List:
        """Create usage examples section"""
        elements = []
        
        # Section title
        title = Paragraph("6. Usage Examples", self.heading_style)
        elements.append(title)
        elements.append(Spacer(1, 20))
        
        # Basic usage
        basic_title = Paragraph("Basic Usage:", self.subheading_style)
        elements.append(basic_title)
        
        language = repo_info.get('language', 'python')
        example_code = self._get_example_code(language)
        example_para = Paragraph(f"<pre>{example_code}</pre>", self.code_style)
        elements.append(example_para)
        
        return elements

    def _format_structure_tree(self, structure: Dict[str, Any], indent: str = "") -> str:
        """Format directory structure as a tree"""
        result = ""
        for name, info in structure.items():
            if info.get('type') == 'directory':
                result += f"{indent}📁 {name}/\n"
                if 'children' in info:
                    result += self._format_structure_tree(info['children'], indent + "  ")
            else:
                result += f"{indent}📄 {name}\n"
        return result

    def _get_prerequisites(self, language: str) -> List[str]:
        """Get prerequisites based on programming language"""
        prereqs = {
            'python': ['Python 3.7+', 'pip (Python package manager)'],
            'javascript': ['Node.js 14+', 'npm or yarn'],
            'typescript': ['Node.js 14+', 'npm or yarn', 'TypeScript compiler'],
            'java': ['Java 8+', 'Maven or Gradle'],
            'cpp': ['C++ compiler (gcc, clang, or MSVC)', 'Make or CMake'],
            'go': ['Go 1.16+'],
            'rust': ['Rust and Cargo'],
            'php': ['PHP 7.4+', 'Composer'],
            'ruby': ['Ruby 2.7+', 'Bundler'],
            'csharp': ['.NET 5+', 'Visual Studio or VS Code']
        }
        return prereqs.get(language.lower(), ['Appropriate runtime environment'])

    def _get_install_command(self, language: str) -> str:
        """Get installation command based on programming language"""
        commands = {
            'python': 'pip install -r requirements.txt',
            'javascript': 'npm install',
            'typescript': 'npm install',
            'java': 'mvn install',
            'cpp': 'make install',
            'go': 'go mod download',
            'rust': 'cargo build',
            'php': 'composer install',
            'ruby': 'bundle install',
            'csharp': 'dotnet restore'
        }
        return commands.get(language.lower(), 'Follow language-specific installation steps')

    def _get_run_command(self, language: str) -> str:
        """Get run command based on programming language"""
        commands = {
            'python': 'python main.py',
            'javascript': 'npm start',
            'typescript': 'npm start',
            'java': 'java -jar target/app.jar',
            'cpp': './app',
            'go': 'go run main.go',
            'rust': 'cargo run',
            'php': 'php -S localhost:8000',
            'ruby': 'ruby app.rb',
            'csharp': 'dotnet run'
        }
        return commands.get(language.lower(), 'Follow language-specific run instructions')

    def _get_example_code(self, language: str) -> str:
        """Get example code based on programming language"""
        examples = {
            'python': '''# Example usage
import requests

# Make a request
response = requests.get('https://api.example.com/data')
print(response.json())''',
            'javascript': '''// Example usage
const axios = require('axios');

// Make a request
axios.get('https://api.example.com/data')
  .then(response => console.log(response.data));''',
            'java': '''// Example usage
import java.net.http.HttpClient;

// Make a request
HttpClient client = HttpClient.newHttpClient();
// ... implementation details''',
            'cpp': '''// Example usage
#include <iostream>

int main() {
    std::cout << "Hello, World!" << std::endl;
    return 0;
}'''
        }
        return examples.get(language.lower(), f'# {language} example code\n# Add your usage examples here')

pdf_service = PDFService() 