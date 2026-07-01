"""Google Gemini translation service."""

import asyncio
import json
import os
import re
import time
from typing import Any

import google.generativeai as genai

from app.config import get_settings
from app.models.localization import ConfidenceScore

SYSTEM_PROMPT = (
    "You are an expert educational content translator. "
    "Translate the following course content accurately preserving technical "
    "terminology, code snippets, and learning objectives."
)

MODEL = "gemini-1.5-flash"
MAX_WORDS_PER_BLOCK = 500
MAX_RETRIES = 3
RETRY_BASE_DELAY = 2.0

_response_times: list[float] = []
_active_requests = 0


class ClaudeService:
    """Handles AI-powered block translation via Gemini."""

    def __init__(self) -> None:
        # Pulling directly from Railway variables to prevent config schema crashes
        gemini_key = os.environ.get("GEMINI_API_KEY")
        genai.configure(api_key=gemini_key)
        
        self.model = genai.GenerativeModel(
            model_name=MODEL,
            system_instruction=SYSTEM_PROMPT
        )

    @staticmethod
    def split_into_blocks(text: str, max_words: int = MAX_WORDS_PER_BLOCK) -> list[str]:
        """Split text into blocks of at most max_words words."""
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        blocks: list[str] = []
        current: list[str] = []
        current_words = 0

        for paragraph in paragraphs:
            word_count = len(paragraph.split())
            if current_words + word_count > max_words and current:
                blocks.append("\n\n".join(current))
                current = [paragraph]
                current_words = word_count
            else:
                current.append(paragraph)
                current_words += word_count

        if current:
            blocks.append("\n\n".join(current))

        if not blocks and text.strip():
            words = text.split()
            for i in range(0, len(words), max_words):
                blocks.append(" ".join(words[i : i + max_words]))

        return blocks

    async def translate_block(
        self,
        text: str,
        source_language: str,
        target_language: str,
        context: str = "",
    ) -> dict[str, Any]:
        """Translate a single content block and return text with confidence."""
        global _active_requests

        user_prompt = (
            f"Source language: {source_language}\n"
            f"Target language: {target_language}\n"
        )
        if context:
            user_prompt += f"Context from previous block: {context[:300]}\n\n"
        user_prompt += (
            f"Translate the following content block:\n\n{text}\n\n"
            "Respond in JSON format only:\n"
            '{"translated_text": "...", "confidence": "high|medium|low"}'
        )

        _active_requests += 1
        start = time.perf_counter()

        try:
            for attempt in range(MAX_RETRIES):
                try:
                    # Force strict JSON output from Gemini
                    response = await self.model.generate_content_async(
                        user_prompt,
                        generation_config=genai.GenerationConfig(
                            response_mime_type="application/json"
                        )
                    )
                    raw = response.text.strip()
                    result = self._parse_response(raw, text)
                    elapsed_ms = (time.perf_counter() - start) * 1000
                    _response_times.append(elapsed_ms)
                    if len(_response_times) > 100:
                        _response_times.pop(0)
                    return result
                except Exception as e:
                    if attempt == MAX_RETRIES - 1:
                        raise e
                    await asyncio.sleep(RETRY_BASE_DELAY * (2**attempt))
        finally:
            _active_requests -= 1

        return {"translated_text": text, "confidence": ConfidenceScore.LOW}

    def _parse_response(self, raw: str, fallback: str) -> dict[str, Any]:
        """Parse JSON response with fallback."""
        try:
            cleaned = raw
            if "```" in raw:
                match = re.search(r"
http://googleusercontent.com/immersive_entry_chip/1

Watch Railway until it turns green, then go upload your file in Vercel. You will finally watch that translation progress bar hit the finish line without spending a dime.