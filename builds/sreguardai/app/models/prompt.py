from pydantic import BaseModel, Field
from typing import Optional

class PromptRequest(BaseModel):
    """
    Request model for AI generation
    """
    prompt: str = Field(..., min_length=10, max_length=2000,
                       description="SRE-related prompt to generate response for")
    model: Optional[str] = Field("llama3.1", description="Ollama model to use")

class PromptResponse(BaseModel):
    """
    Response model for AI generation
    """
    response: str = Field(..., description="Generated AI response")
    model_used: Optional[str] = "llama3.1"