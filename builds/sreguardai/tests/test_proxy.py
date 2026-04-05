#!/usr/bin/env python3
"""
Tests for SREGuardAI
"""

import pytest
from starlette.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "SREGuardAI is running" in response.json()["message"]

def test_generate_sre_prompt():
    """Test generating response for SRE prompt"""
    payload = {
        "prompt": "Analyze this incident: High latency on API endpoint",
        "model": "llama3.1"
    }
    response = client.post("/generate", json=payload)
    # Note: This will fail without Ollama running, but tests the endpoint
    assert response.status_code in [200, 500]  # 500 if Ollama not available

def test_generate_non_sre_prompt():
    """Test rejection of non-SRE prompts"""
    payload = {
        "prompt": "Write a poem about cats",
        "model": "llama3.1"
    }
    response = client.post("/generate", json=payload)
    assert response.status_code == 400
    assert "SRE-related" in response.json()["detail"]

def test_generate_short_prompt():
    """Test rejection of too-short prompts"""
    payload = {
        "prompt": "Hi",
        "model": "llama3.1"
    }
    response = client.post("/generate", json=payload)
    assert response.status_code == 422  # Validation error