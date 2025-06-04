from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import google.generativeai as genai
import os
import tempfile
import zipfile
import json
import shutil

router = APIRouter()

class UIGenerationRequest(BaseModel):
    project_name: str = Field(..., description="Name of the UI project")
    description: str = Field(..., description="Description of what UI to build")
    framework: str = Field("react", description="UI framework (react, vue, angular, vanilla)")
    styling: str = Field("tailwind", description="Styling approach (tailwind, css, scss, styled-components)")
    components: Optional[List[str]] = Field(None, description="Specific components needed")
    features: Optional[List[str]] = Field(None, description="Features to include")
    gemini_api_key: Optional[str] = Field(None, description="Gemini API key")

class ComponentRequest(BaseModel):
    component_name: str = Field(..., description="Name of the component")
    description: str = Field(..., description="What the component should do")
    framework: str = Field("react", description="UI framework")
    props: Optional[Dict] = Field(None, description="Component props/properties")
    styling: str = Field("tailwind", description="Styling approach")
    gemini_api_key: Optional[str] = Field(None, description="Gemini API key")

class UIPreviewRequest(BaseModel):
    html: str = Field(..., description="HTML code")
    css: str = Field(..., description="CSS code")
    javascript: Optional[str] = Field(None, description="JavaScript code")

def configure_gemini(api_key: Optional[str] = None):
    """Configure Gemini AI with API key"""
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise HTTPException(status_code=401, detail="Gemini API key not provided")
    genai.configure(api_key=key)
    return genai.GenerativeModel('gemini-pro')

def create_react_project_structure(project_name: str, temp_dir: str):
    """Create a basic React project structure"""
    project_dir = os.path.join(temp_dir, project_name)
    os.makedirs(project_dir)
    
    # Create directories
    dirs = [
        "src",
        "src/components",
        "src/styles",
        "src/utils",
        "src/hooks",
        "src/pages",
        "public"
    ]
    
    for dir_path in dirs:
        os.makedirs(os.path.join(project_dir, dir_path))
    
    return project_dir

@router.post("/generate-ui")
async def generate_ui_project(request: UIGenerationRequest):
    """Generate a complete UI project based on description"""
    try:
        model = configure_gemini(request.gemini_api_key)
        
        # Build comprehensive prompt
        components_info = f"\nComponents needed: {', '.join(request.components)}" if request.components else ""
        features_info = f"\nFeatures: {', '.join(request.features)}" if request.features else ""
        
        # Generate project structure first
        structure_prompt = f"""
        Design a {request.framework} project structure for: {request.description}
        
        Project Name: {request.project_name}
        Styling: {request.styling}
        {components_info}
        {features_info}
        
        Provide a complete file structure with descriptions of what each file should contain.
        Include all necessary configuration files.
        """
        
        structure_response = model.generate_content(structure_prompt)
        
        # Generate main application code
        app_prompt = f"""
        Generate the main application code for a {request.framework} project:
        
        Description: {request.description}
        Styling: {request.styling}
        
        Create a beautiful, modern UI with:
        1. Responsive design
        2. Smooth animations
        3. Good UX practices
        4. Accessibility features
        5. Clean component structure
        
        Include the main App component and routing setup.
        """
        
        app_response = model.generate_content(app_prompt)
        
        # Generate individual components
        components = request.components or ["Header", "Hero", "Features", "Footer"]
        component_codes = {}
        
        for component in components:
            comp_prompt = f"""
            Create a {request.framework} component called {component} using {request.styling}:
            
            Make it modern, animated, and beautiful.
            Follow best practices for {request.framework}.
            Include proper TypeScript types if applicable.
            """
            
            comp_response = model.generate_content(comp_prompt)
            component_codes[component] = comp_response.text
        
        # Generate package.json
        package_prompt = f"""
        Create a package.json file for a {request.framework} project with:
        - Project name: {request.project_name}
        - All necessary dependencies for {request.framework} and {request.styling}
        - Useful scripts (dev, build, test, lint)
        - Modern tooling setup
        """
        
        package_response = model.generate_content(package_prompt)
        
        # Create project files in temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = create_react_project_structure(request.project_name, temp_dir)
            
            # Write package.json
            package_json = extract_json_from_response(package_response.text)
            with open(os.path.join(project_dir, "package.json"), "w") as f:
                json.dump(package_json, f, indent=2)
            
            # Write main app file
            app_code = extract_code_from_response(app_response.text, request.framework)
            app_file = "App.tsx" if request.framework == "react" else "App.vue"
            with open(os.path.join(project_dir, "src", app_file), "w") as f:
                f.write(app_code)
            
            # Write components
            for comp_name, comp_code in component_codes.items():
                code = extract_code_from_response(comp_code, request.framework)
                ext = ".tsx" if request.framework == "react" else ".vue"
                with open(os.path.join(project_dir, "src", "components", f"{comp_name}{ext}"), "w") as f:
                    f.write(code)
            
            # Create README
            readme_content = f"""# {request.project_name}

{request.description}

## Setup

\`\`\`bash
npm install
npm run dev
\`\`\`

## Features

{chr(10).join(f"- {feature}" for feature in (request.features or ["Modern UI", "Responsive Design", "Animations"]))}

## Technologies

- Framework: {request.framework}
- Styling: {request.styling}

## Project Structure

{structure_response.text}
"""
            
            with open(os.path.join(project_dir, "README.md"), "w") as f:
                f.write(readme_content)
            
            # Create zip file
            zip_path = os.path.join(temp_dir, f"{request.project_name}.zip")
            shutil.make_archive(
                os.path.join(temp_dir, request.project_name),
                'zip',
                temp_dir,
                request.project_name
            )
            
            # Read zip file
            with open(zip_path, "rb") as f:
                zip_content = f.read()
        
        return {
            "project_name": request.project_name,
            "framework": request.framework,
            "styling": request.styling,
            "structure": structure_response.text,
            "components": list(component_codes.keys()),
            "download_url": f"/api/ui/download/{request.project_name}",
            "setup_instructions": [
                f"1. Extract {request.project_name}.zip",
                f"2. cd {request.project_name}",
                "3. npm install",
                "4. npm run dev"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-component")
async def generate_component(request: ComponentRequest):
    """Generate a single UI component"""
    try:
        model = configure_gemini(request.gemini_api_key)
        
        props_info = ""
        if request.props:
            props_info = f"\nProps: {json.dumps(request.props, indent=2)}"
        
        prompt = f"""
        Create a {request.framework} component called {request.component_name}:
        
        Description: {request.description}
        Styling: {request.styling}
        {props_info}
        
        Requirements:
        1. Modern, beautiful design
        2. Smooth animations and transitions
        3. Responsive layout
        4. Accessibility features
        5. Clean, reusable code
        6. Proper TypeScript types (if React)
        7. Follow {request.framework} best practices
        
        Make it production-ready with error handling and loading states if applicable.
        """
        
        response = model.generate_content(prompt)
        
        # Extract code
        code = extract_code_from_response(response.text, request.framework)
        
        # Generate usage example
        usage_prompt = f"""
        Show how to use the {request.component_name} component in a parent component.
        Include all necessary imports and props.
        """
        
        usage_response = model.generate_content(usage_prompt)
        
        return {
            "component_name": request.component_name,
            "code": code,
            "framework": request.framework,
            "styling": request.styling,
            "usage_example": extract_code_from_response(usage_response.text, request.framework),
            "explanation": response.text
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/preview")
async def preview_ui(request: UIPreviewRequest):
    """Generate a preview HTML file for UI code"""
    try:
        # Create complete HTML file
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UI Preview</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        {request.css}
    </style>
</head>
<body>
    {request.html}
    {f'<script>{request.javascript}</script>' if request.javascript else ''}
</body>
</html>"""
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(html_content)
            temp_path = f.name
        
        return {
            "preview_url": f"/api/ui/preview-file?path={temp_path}",
            "html_size": len(html_content),
            "preview_available": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/preview-file")
async def serve_preview_file(path: str):
    """Serve the preview HTML file"""
    if os.path.exists(path) and path.endswith('.html'):
        return FileResponse(path, media_type="text/html")
    else:
        raise HTTPException(status_code=404, detail="Preview file not found")

@router.post("/generate-design-system")
async def generate_design_system(
    brand_name: str,
    primary_color: str,
    style: str = "modern",  # modern, minimal, playful, corporate
    gemini_api_key: Optional[str] = None
):
    """Generate a complete design system"""
    try:
        model = configure_gemini(gemini_api_key)
        
        prompt = f"""
        Create a complete design system for {brand_name} with:
        
        Primary Color: {primary_color}
        Style: {style}
        
        Include:
        1. Color palette (primary, secondary, neutral, semantic colors)
        2. Typography scale (headings, body, captions)
        3. Spacing system (margins, paddings)
        4. Border radius values
        5. Shadow system
        6. Animation timings
        7. Breakpoints for responsive design
        
        Provide as CSS variables and utility classes.
        Make it consistent and beautiful.
        """
        
        response = model.generate_content(prompt)
        
        # Extract CSS
        css_code = extract_code_from_response(response.text, "css")
        
        # Generate component examples
        examples_prompt = f"""
        Create example components using the design system for {brand_name}:
        1. Button variations
        2. Card component
        3. Form inputs
        4. Navigation bar
        
        Use the CSS variables from the design system.
        """
        
        examples_response = model.generate_content(examples_prompt)
        
        return {
            "brand_name": brand_name,
            "primary_color": primary_color,
            "style": style,
            "design_system_css": css_code,
            "component_examples": examples_response.text,
            "tokens": {
                "colors": "Defined in CSS variables",
                "typography": "Defined in CSS variables",
                "spacing": "Defined in CSS variables"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def extract_code_from_response(response_text: str, language: str) -> str:
    """Extract code block from AI response"""
    import re
    
    # Try to find code blocks
    code_blocks = re.findall(r'```(?:\w+)?\n(.*?)```', response_text, re.DOTALL)
    if code_blocks:
        return code_blocks[0].strip()
    
    # If no code blocks, try to extract based on common patterns
    if language == "react":
        # Look for React component pattern
        match = re.search(r'(import.*?export default.*?})', response_text, re.DOTALL)
        if match:
            return match.group(1)
    
    return response_text.strip()

def extract_json_from_response(response_text: str) -> dict:
    """Extract JSON from AI response"""
    import re
    
    # Try to find JSON block
    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except:
            pass
    
    # Return default package.json if extraction fails
    return {
        "name": "generated-project",
        "version": "1.0.0",
        "scripts": {
            "dev": "vite",
            "build": "vite build",
            "preview": "vite preview"
        },
        "dependencies": {
            "react": "^18.2.0",
            "react-dom": "^18.2.0"
        },
        "devDependencies": {
            "vite": "^5.0.0",
            "@vitejs/plugin-react": "^4.2.0"
        }
    } 