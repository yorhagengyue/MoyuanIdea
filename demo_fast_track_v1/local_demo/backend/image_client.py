from __future__ import annotations

import base64
import json
import os
import re
from pathlib import Path
from typing import Any
from urllib import error, request


_OPTION_SPECS = [
    {
        "key": "峰",
        "subtitle": "尖尖高高",
        "slug": "feng",
        "prompt": (
            "儿童自然教育插画，水彩手绘风，白色背景，单个山峰主体，"
            "山体尖尖高高，轮廓清晰，色彩柔和，适合4-8岁儿童认知卡片。"
        ),
    },
    {
        "key": "岭",
        "subtitle": "连绵起伏",
        "slug": "ling",
        "prompt": (
            "儿童自然教育插画，水彩手绘风，白色背景，连绵起伏的山脊线，"
            "多个低矮山头连续排列，轮廓清晰，适合4-8岁儿童认知卡片。"
        ),
    },
    {
        "key": "崖",
        "subtitle": "陡直落差",
        "slug": "ya_cliff",
        "prompt": (
            "儿童自然教育插画，水彩手绘风，白色背景，突出陡直悬崖与明显高度落差，"
            "画面简洁，边缘清晰，适合4-8岁儿童认知卡片。"
        ),
    },
    {
        "key": "谷",
        "subtitle": "两山低地",
        "slug": "gu",
        "prompt": (
            "儿童自然教育插画，水彩手绘风，白色背景，两侧山体中间低地形成山谷，"
            "结构清晰，颜色柔和，适合4-8岁儿童认知卡片。"
        ),
    },
]


class GeminiImageError(RuntimeError):
    pass


class GeminiImageClient:
    def __init__(self, frontend_dir: Path) -> None:
        self.base_url = os.getenv("FOURSAPI_BASE_URL", "https://4sapi.com/v1").rstrip("/")
        self.api_key = (
            os.getenv("FOURSAPI_GEMINI_API_KEY", "").strip()
            or os.getenv("FOURSAPI_API_KEY", "").strip()
        )
        self.model = os.getenv("GEMINI_IMAGE_MODEL", "gemini-3.1-flash-image-preview").strip()
        self.timeout_sec = float(os.getenv("GEMINI_IMAGE_TIMEOUT_SEC", "120"))
        self.generated_dir = frontend_dir / "generated_options"
        self.generated_dir.mkdir(parents=True, exist_ok=True)

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def ensure_option_images(self, force: bool = False) -> list[dict[str, str]]:
        items: list[dict[str, str]] = []
        for spec in _OPTION_SPECS:
            img_path = self.generated_dir / f"{spec['slug']}.jpg"
            if force or (not img_path.exists()) or img_path.stat().st_size == 0:
                image_bytes = self._generate_image_bytes(spec["prompt"])
                img_path.write_bytes(image_bytes)

            items.append(
                {
                    "key": spec["key"],
                    "subtitle": spec["subtitle"],
                    "image_url": f"/frontend/generated_options/{spec['slug']}.jpg",
                }
            )
        return items

    def _generate_image_bytes(self, prompt: str) -> bytes:
        if not self.enabled:
            raise GeminiImageError("FOURSAPI_GEMINI_API_KEY is not set")

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You generate one clean child-friendly illustration only. "
                        "No text labels, no watermark, no collage."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "modalities": ["text", "image"],
            "stream": False,
        }

        req = request.Request(
            url=f"{self.base_url}/chat/completions",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=self.timeout_sec) as resp:
                obj = json.loads(resp.read().decode("utf-8"))
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise GeminiImageError(f"http error {exc.code}: {detail}") from exc
        except Exception as exc:
            raise GeminiImageError(f"request failed: {exc}") from exc

        content = self._extract_content(obj)
        image_bytes = self._extract_image_bytes(content)
        if not image_bytes:
            raise GeminiImageError("image bytes not found in response")
        return image_bytes

    @staticmethod
    def _extract_content(response_obj: dict[str, Any]) -> str:
        choices = response_obj.get("choices") or []
        if not choices:
            raise GeminiImageError("empty choices")
        message = choices[0].get("message") or {}
        content = message.get("content")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            chunks: list[str] = []
            for item in content:
                if isinstance(item, dict):
                    if "text" in item:
                        chunks.append(str(item["text"]))
                    elif "content" in item:
                        chunks.append(str(item["content"]))
            if chunks:
                return "\n".join(chunks)
        raise GeminiImageError("unsupported content format")

    @staticmethod
    def _extract_image_bytes(content: str) -> bytes:
        match = re.search(r"data:image/[a-zA-Z0-9.+-]+;base64,([A-Za-z0-9+/=\n\r]+)", content)
        if not match:
            return b""
        b64 = re.sub(r"\s+", "", match.group(1))
        return base64.b64decode(b64)
