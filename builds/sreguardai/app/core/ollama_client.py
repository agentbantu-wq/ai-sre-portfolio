import requests
import json
import logging
from typing import Optional

class OllamaClient:
    """
    Client for interacting with local Ollama instance
    """

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model = "llama3.1"  # Default model

    def generate(self, prompt: str) -> Optional[str]:
        """
        Generate response from Ollama
        """
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }

            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                logging.error(f"Ollama API error: {response.status_code}")
                return None

        except Exception as e:
            logging.error(f"Error calling Ollama: {e}")
            return None

    def list_models(self) -> list:
        """
        List available models
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                return response.json().get("models", [])
            return []
        except Exception as e:
            logging.error(f"Error listing models: {e}")
            return []