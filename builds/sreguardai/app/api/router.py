from fastapi import APIRouter, HTTPException
from app.models.prompt import PromptRequest, PromptResponse
from app.core.ollama_client import OllamaClient
from app.core.logging import log_interaction
import logging

router = APIRouter()
ollama_client = OllamaClient()

@router.post("/generate", response_model=PromptResponse)
async def generate_response(request: PromptRequest):
    """
    Generate AI response for SRE prompt
    """
    try:
        # Validate SRE context
        if not any(keyword in request.prompt.lower() for keyword in
                  ['incident', 'alert', 'runbook', 'sre', 'reliability', 'monitoring']):
            raise HTTPException(status_code=400, detail="Prompt must be SRE-related")

        # Generate response
        response_text = ollama_client.generate(request.prompt)

        # Log interaction
        log_interaction(request.prompt, response_text)

        return PromptResponse(response=response_text)

    except Exception as e:
        logging.error(f"Error generating response: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate response")