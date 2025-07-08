import google.generativeai as genai
from app.config import config
import json
from typing import List, Dict, Any, Optional

class GeminiService:
    def __init__(self):
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

    async def chat(self, messages: List[Dict[str, str]], repo_context: Optional[str] = None) -> str:
        try:
            formatted_messages = []
            for msg in messages:
                if msg['role'] == 'user':
                    formatted_messages.append(f"User: {msg['content']}")
                elif msg['role'] == 'assistant':
                    formatted_messages.append(f"Assistant: {msg['content']}")
            if repo_context:
                formatted_messages.insert(0, f"Repository Context:\n{repo_context}\n")
            prompt = "\n".join(formatted_messages)
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error in Gemini chat: {e}")
            return "[Gemini API error]"

    async def generate_code(self, prompt: str, language: str, context: Optional[str] = None) -> str:
        try:
            full_prompt = f"""
            Generate concise, idiomatic, and practical {language} code for the following prompt:
            
            Prompt: {prompt}
            
            {f"Context: {context}" if context else ""}
            
            Requirements:
            1. Write clean, idiomatic, and efficient code as used in real-world projects.
            2. Avoid unnecessary comments, verbose explanations, and excessive error handling.
            3. For simple operations, do not add error handling or checks unless specifically requested.
            4. Do NOT include example usage or test code unless specifically requested in the prompt.
            5. Do NOT use input() or any interactive input.
            6. Assume all inputs are provided as function arguments or variables.
            7. The code should run in a web-based execution environment without user interaction.
            8. Only include minimal error handling as appropriate for production code, and only if the prompt asks for it.
            9. Write code as you would in a real-world project, not for teaching or demonstration.
            
            Please provide only the code without any markdown formatting.
            """
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            print(f"Error in Gemini code generation: {e}")
            return "[Gemini API error]"

    async def analyze_code(self, code: str, language: str) -> Dict[str, Any]:
        try:
            prompt = f"""
            Analyze the following {language} code and provide a detailed analysis:
            
            Code:
            {code}
            
            Please provide analysis in the following JSON format:
            {{
                "summary": "Brief summary of what the code does",
                "complexity": "Low/Medium/High",
                "functions": ["list of function names"],
                "classes": ["list of class names"],
                "variables": ["list of important variables"],
                "suggestions": ["list of improvement suggestions"],
                "quality_score": 85
            }}
            """
            response = self.model.generate_content(prompt)
            try:
                return json.loads(response.text)
            except json.JSONDecodeError:
                return {}
        except Exception as e:
            print(f"Error in Gemini code analysis: {e}")
            return {}

    async def explain_code(self, code: str, language: str) -> str:
        try:
            prompt = f"""
            Explain the following {language} code in detail:
            
            {code}
            
            Please provide:
            1. What the code does
            2. How it works step by step
            3. Key concepts used
            4. Any important patterns or techniques
            """
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error in Gemini code explanation: {e}")
            return "[Gemini API error]"

    async def generate_frontend(self, prompt: str, framework: str) -> str:
        try:
            # If the framework is React, instruct to generate only App.jsx (or App.js) as a single file
            if framework.lower() == "react":
                full_prompt = f"""
                Generate only the code for a React frontend app in a single file (App.jsx), using functional components and hooks, based on the following prompt:
                
                Prompt: {prompt}
                
                Requirements:
                1. Output only the code for App.jsx. Do NOT include CSS, HTML, or any other files.
                2. Do NOT include any explanations, comments, or extra text.
                3. The code should be ready to copy and run as a real React component file.
                4. Do NOT use markdown formatting or language tags.
                """
            else:
                full_prompt = f"""
                Generate a complete, production-ready {framework} frontend codebase based on the following prompt:
                
                Prompt: {prompt}
                
                Requirements:
                1. Output only the full code (HTML, CSS, JS, etc.) needed to run the app.
                2. Do NOT include any placeholder text, explanations, or comments unless specifically requested.
                3. Do NOT include any mock HTML or 'Your content will appear here.'
                4. The code should be ready to copy and run as a real project.
                
                Please provide only the code without any markdown formatting or extra text.
                """
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            print(f"Error in Gemini frontend generation: {e}")
            return "[Gemini API error]"

gemini_service = GeminiService() 