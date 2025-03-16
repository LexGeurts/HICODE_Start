import os
import yaml
import requests
import json
from typing import Dict, List, Any, Optional, Text

class OpenAIClient:
    """
    A utility class for interacting with OpenAI APIs for CALM rephrasing
    """
    
    def __init__(self, config_path: str = "../config/openai.yml"):
        """Initialize the OpenAI client with configuration"""
        self.config = self._load_config(config_path)
        self.api_key = os.environ.get(self.config['api']['api_key_env'])
        if not self.api_key:
            raise ValueError(f"OpenAI API key not found in environment variable {self.config['api']['api_key_env']}")
        
        # Set base URL and headers
        self.base_url = self.config['api']['endpoint']
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Add organization header if available
        org_id_env = self.config['api'].get('organization_env')
        if org_id_env and os.environ.get(org_id_env):
            self.headers["OpenAI-Organization"] = os.environ.get(org_id_env)
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load OpenAI configuration from YAML file"""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except Exception as e:
            print(f"Error loading OpenAI config: {e}")
            # Provide minimal default configuration
            return {
                "api": {"endpoint": "https://api.openai.com/v1", "api_key_env": "OPENAI_API_KEY"},
                "models": {"default": "gpt-3.5-turbo"},
                "parameters": {"rephraser": {"temperature": 0.3, "max_tokens": 50}}
            }
    
    def rephrase(self, text: Text, active_flow: Text = "main_flow") -> Text:
        """
        Rephrase user input using OpenAI
        
        Args:
            text: The original user text to rephrase
            active_flow: The current conversation flow context
            
        Returns:
            The rephrased text
        """
        # Get the appropriate system prompt for the flow
        system_prompt = self.config['prompts'].get(
            active_flow, 
            self.config['prompts']['main_flow']
        )
        
        # Get model and parameters
        model = self.config['models'].get('rephraser', self.config['models']['default'])
        params = self.config['parameters'].get('rephraser', {})
        
        # Prepare the API request
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Rephrase this user input to match an intent: '{text}'"}
            ],
            **params
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                rephrased = result['choices'][0]['message']['content'].strip()
                return rephrased
            else:
                return text  # Return original if rephrasing failed
        except Exception as e:
            print(f"Error in OpenAI rephrasing: {e}")
            return text  # Return original if rephrasing failed
