#!/usr/bin/env python3
"""
SREGuardAI - Self-hosted AI Gateway for SRE Teams
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
from app.api.router import router
from app.core.ollama_client import OllamaClient
from app.core.logging import setup_logging

# Setup logging
setup_logging()

app = FastAPI(
    title="SREGuardAI",
    description="Self-hosted AI gateway for SRE teams",
    version="1.0.0"
)

# Include router
app.include_router(router)

@app.get("/")
async def root():
    return {"message": "SREGuardAI is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)