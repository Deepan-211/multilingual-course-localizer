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
        """Parse native JSON response with fallback."""
        try:
            data = json.loads(raw)
            confidence = str(data.get("confidence", "medium")).lower()
            if confidence not in ("high", "medium", "low"):
                confidence = "medium"
            return {
                "translated_text": data.get("translated_text", fallback),
                "confidence": confidence,
            }
        except (json.JSONDecodeError, KeyError):
            return {"translated_text": raw or fallback, "confidence": ConfidenceScore.MEDIUM}

    @classmethod
    def get_ai_status(cls) -> dict[str, Any]:
        """Return aggregate API metrics."""
        avg_time = sum(_response_times) / len(_response_times) if _response_times else 0.0
        return {
            "status": "operational" if _active_requests < 10 else "busy",
            "avg_response_time_ms": round(avg_time, 2),
            "current_load": _active_requests,
            "model": MODEL,
        }