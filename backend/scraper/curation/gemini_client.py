import os
import httpx
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
            
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

    async def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": 0.2,
                "responseMimeType": "application/json"
            }
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{self.api_url}?key={self.api_key}",
                json=payload
            )
            resp.raise_for_status()
            data = resp.json()
            
            try:
                text_content = data["candidates"][0]["content"]["parts"][0]["text"]
                return text_content
            except (KeyError, IndexError) as parse_err:
                logger.error(f"Failed to parse Gemini response payload: {data}. Error: {parse_err}")
                raise ValueError(f"Invalid API response structure from Gemini: {parse_err}")

    async def curate_listing(self, listing: dict) -> dict:
        from .prompts import build_curation_prompt
        prompt = build_curation_prompt(listing)
        raw = await self.generate(prompt)
        return json.loads(raw)
