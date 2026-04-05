import logging
import sys
import json
from pathlib import Path
from config import load_config
import requests

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sreguardai.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SREGuardAI:
    def __init__(self, config_path='config.yaml'):
        self.config = load_config(config_path)
        self.ollama_url = self.config.get('ollama_url', 'http://localhost:11434')
        self.model = self.config.get('model', 'mistral')
        logger.info(f'SREGuardAI initialized with model: {self.model}')
    
    def proxy_prompt(self, prompt, context='incident'):
        """Send SRE prompt to local Ollama instance."""
        try:
            if not self._validate_prompt(prompt, context):
                logger.warning(f'Prompt validation failed for context: {context}')
                return None
            
            payload = {
                'model': self.model,
                'prompt': prompt,
                'stream': False
            }
            
            response = requests.post(
                f'{self.ollama_url}/api/generate',
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json().get('response', '')
            self._log_audit(prompt, result, context)
            return result
        
        except requests.exceptions.RequestException as e:
            logger.error(f'Ollama connection failed: {e}')
            return None
    
    def _validate_prompt(self, prompt, context):
        """Basic safety filter for SRE contexts."""
        blocked_patterns = self.config.get('blocked_patterns', [])
        return not any(pattern.lower() in prompt.lower() for pattern in blocked_patterns)
    
    def _log_audit(self, prompt, response, context):
        """Log all interactions for compliance."""
        audit_entry = {
            'timestamp': __import__('datetime').datetime.utcnow().isoformat(),
            'context': context,
            'prompt_hash': __import__('hashlib').sha256(prompt.encode()).hexdigest(),
            'response_length': len(response)
        }
        with open(self.config.get('audit_log', 'audit.log'), 'a') as f:
            f.write(json.dumps(audit_entry) + '\n')
        logger.info(f'Audit logged: {context}')

def main():
    if len(sys.argv) < 2:
        print('Usage: python main.py <prompt> [--context incident|runbook|debug]')
        sys.exit(1)
    
    prompt = sys.argv[1]
    context = 'incident'
    if '--context' in sys.argv:
        idx = sys.argv.index('--context')
        context = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else 'incident'
    
    sre_guard = SREGuardAI()
    result = sre_guard.proxy_prompt(prompt, context)
    
    if result:
        print(result)
    else:
        print('Error: Failed to generate response', file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()