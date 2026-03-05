from __future__ import annotations

import base64
import json
import os
from io import BytesIO
from urllib import request

from PIL import Image, ImageStat

from app.schemas import ChartAnalysis

PROMPT = (
    "Analyze this trading chart image. Return JSON with keys: trend (bullish|bearish|sideways), "
    "confidence (0-1), patterns (array of strings), key_levels (array of numbers), thesis, "
    "suggested_entry (number), suggested_stop_loss (number)."
)


class ChartAnalyzer:
    def __init__(self) -> None:
        self.provider_name = os.getenv("VISION_PROVIDER", "heuristic").lower()

    def analyze(self, image_bytes: bytes) -> ChartAnalysis:
        if self.provider_name == "openai" and os.getenv("OPENAI_API_KEY"):
            return self._analyze_openai(image_bytes)
        if self.provider_name == "anthropic" and os.getenv("ANTHROPIC_API_KEY"):
            return self._analyze_anthropic(image_bytes)
        return self._analyze_heuristic(image_bytes)

    def _analyze_openai(self, image_bytes: bytes) -> ChartAnalysis:
        payload = {
            "model": os.getenv("OPENAI_VISION_MODEL", "gpt-4o-mini"),
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64.b64encode(image_bytes).decode('utf-8')}"
                            },
                        },
                    ],
                }
            ],
        }
        req = request.Request(
            "https://api.openai.com/v1/chat/completions",
            method="POST",
            headers={
                "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
                "Content-Type": "application/json",
            },
            data=json.dumps(payload).encode("utf-8"),
        )
        with request.urlopen(req, timeout=30) as resp:
            parsed = json.loads(resp.read().decode("utf-8"))
        content = parsed["choices"][0]["message"]["content"]
        data = json.loads(content)
        return ChartAnalysis(provider="openai", **data)

    def _analyze_anthropic(self, image_bytes: bytes) -> ChartAnalysis:
        payload = {
            "model": os.getenv("ANTHROPIC_VISION_MODEL", "claude-3-5-sonnet-20241022"),
            "max_tokens": 500,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": PROMPT + " Return only JSON."},
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": base64.b64encode(image_bytes).decode("utf-8"),
                            },
                        },
                    ],
                }
            ],
        }
        req = request.Request(
            "https://api.anthropic.com/v1/messages",
            method="POST",
            headers={
                "x-api-key": os.environ["ANTHROPIC_API_KEY"],
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            data=json.dumps(payload).encode("utf-8"),
        )
        with request.urlopen(req, timeout=30) as resp:
            parsed = json.loads(resp.read().decode("utf-8"))
        content = parsed["content"][0]["text"]
        data = json.loads(content)
        return ChartAnalysis(provider="anthropic", **data)

    @staticmethod
    def _analyze_heuristic(image_bytes: bytes) -> ChartAnalysis:
        image = Image.open(BytesIO(image_bytes)).convert("L")
        stat = ImageStat.Stat(image)
        avg_brightness = stat.mean[0]

        if avg_brightness > 150:
            trend = "bullish"
            patterns = ["ascending channel", "higher highs"]
            confidence = 0.67
            thesis = "Momentum appears constructive with continuation bias."
        elif avg_brightness < 100:
            trend = "bearish"
            patterns = ["lower highs", "distribution zone"]
            confidence = 0.64
            thesis = "Price structure implies potential downside continuation."
        else:
            trend = "sideways"
            patterns = ["range-bound consolidation"]
            confidence = 0.55
            thesis = "No clear directional edge; wait for breakout confirmation."

        key_levels = [round(avg_brightness * 0.5, 2), round(avg_brightness * 0.65, 2)]
        entry = round(key_levels[0] * 1.02, 2)
        stop = round(key_levels[0] * 0.97, 2)

        return ChartAnalysis(
            trend=trend,
            confidence=confidence,
            patterns=patterns,
            key_levels=key_levels,
            thesis=thesis,
            suggested_entry=entry,
            suggested_stop_loss=stop,
            provider="heuristic",
        )
