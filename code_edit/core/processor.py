"""
Core code processing functionality.
"""
import os
from pathlib import Path
from typing import Optional, Dict

import google.generativeai as genai

class CodeProcessor:
    """Handles code transformations using AI."""

    model_name = 'gemini-2.5-flash-preview-04-17'
    def __init__(self):
        """Initialize the processor with API credentials."""
        self.api_key = os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError(
                "GOOGLE_API_KEY environment variable must be set. "
                "Get your API key from https://makersuite.google.com/app/apikey"
            )
        genai.configure(api_key=self.api_key)
        
        # Configure the model
        self.model = genai.GenerativeModel(self.model_name)

    def get_model_info(self) -> Dict[str, str]:
        """
        Get information about the current model configuration.
        
        Returns:
            Dictionary containing model information
        """
        return {
            "model": self.model_name,
            "provider": "Google",
            "type": "Large Language Model",
            "capabilities": "Code editing, generation, and analysis"
        }

    def process(self, code: str, prompt: str) -> str:
        """
        Process the code according to the prompt.
        
        Args:
            code: The original code to modify
            prompt: Natural language description of desired changes
            
        Returns:
            The modified code
        """
        # Construct the system message and user prompt
        system_prompt = """You are an expert code editor. Your task is to modify the given code according to the user's prompt.
The changes should be minimal and focused on the requested modifications while preserving the code's structure and style.
You should return ONLY the raw modified code, with absolutely no markdown formatting, no code block markers (```), and no additional explanation."""

        user_prompt = f"""Please modify this code according to the following request: {prompt}

Here's the code to modify:

{code}"""

        # Get the AI response
        response = self.model.generate_content(
            [system_prompt, user_prompt],
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                candidate_count=1,
                max_output_tokens=8192,
            )
        )

        # Extract and return the modified code
        return response.text

    def detect_language(self, file_path: Path) -> Optional[str]:
        """
        Detect the programming language based on file extension.
        
        Args:
            file_path: Path to the code file
            
        Returns:
            The detected language or None if unknown
        """
        extension_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
            '.cs': 'csharp',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
        }
        return extension_map.get(file_path.suffix.lower()) 