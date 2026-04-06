from __future__ import annotations

import os
from pathlib import Path
import tempfile
import time

from .models import AsrResultEnvelope, WordTimestamp
from .scoring import normalize_text

try:
    from faster_whisper import WhisperModel
except Exception:  # pragma: no cover
    WhisperModel = None


def synthesize_timing(text: str) -> list[WordTimestamp]:
    tokens = list(normalize_text(text))
    if not tokens:
        return []
    slots: list[WordTimestamp] = []
    cursor = 0.0
    for token in tokens:
        slots.append(WordTimestamp(word=token, start=round(cursor, 3), end=round(cursor + 0.24, 3)))
        cursor += 0.24
    return slots


class ASREngine:
    def __init__(self) -> None:
        self.mode = os.getenv("DEMO_ASR_MODE", "auto").lower()  # auto | mock | whisper
        self.model_name = os.getenv("DEMO_ASR_MODEL", "tiny")
        self.device = os.getenv("DEMO_ASR_DEVICE", "cpu")
        self.compute_type = os.getenv("DEMO_ASR_COMPUTE_TYPE", "int8")
        self._model = None
        self._load_error: str | None = None

    def _ensure_model(self) -> None:
        if self._model is not None or self._load_error is not None:
            return
        if WhisperModel is None:
            self._load_error = "faster-whisper 不可用，自动切换到演示兜底。"
            return
        try:
            self._model = WhisperModel(
                self.model_name,
                device=self.device,
                compute_type=self.compute_type,
            )
        except Exception as exc:  # pragma: no cover
            self._load_error = f"Whisper 模型加载失败：{exc}"

    def transcribe(self, audio_bytes: bytes, optional_reference_text: str | None = None) -> AsrResultEnvelope:
        started = time.perf_counter()
        warnings: list[str] = []

        force_mock = self.mode == "mock"
        if not force_mock:
            self._ensure_model()

        if not force_mock and self._model is not None:
            temp_path: Path | None = None
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
                    tmp.write(audio_bytes)
                    temp_path = Path(tmp.name)

                segments, _ = self._model.transcribe(
                    str(temp_path),
                    language="zh",
                    word_timestamps=True,
                    vad_filter=True,
                )
                transcript_parts: list[str] = []
                words: list[WordTimestamp] = []
                for seg in segments:
                    if seg.text:
                        transcript_parts.append(seg.text.strip())
                    for word in getattr(seg, "words", []) or []:
                        token = (word.word or "").strip()
                        if not token:
                            continue
                        words.append(
                            WordTimestamp(
                                word=token,
                                start=round(float(word.start), 3),
                                end=round(float(word.end), 3),
                                confidence=round(float(getattr(word, "probability", 0.0)), 3),
                            )
                        )

                transcript = "".join(transcript_parts).strip()
                if not transcript:
                    raise RuntimeError("ASR 返回空结果")

                latency_ms = int((time.perf_counter() - started) * 1000)
                return AsrResultEnvelope(
                    engine="faster_whisper",
                    transcript=transcript,
                    word_timestamps=words or synthesize_timing(transcript),
                    latency_ms=latency_ms,
                    warnings=warnings,
                )
            except Exception as exc:
                warnings.append(f"深研ASR处理失败，切换兜底模式：{exc}")
            finally:
                if temp_path and temp_path.exists():
                    try:
                        temp_path.unlink()
                    except Exception:
                        pass

        if self._load_error:
            warnings.append(self._load_error)

        fallback_text = optional_reference_text or "我觉得这是峰，因为它尖尖的。"
        transcript = normalize_text(fallback_text) or "我觉得这是峰，因为它尖尖的"
        latency_ms = int((time.perf_counter() - started) * 1000)
        return AsrResultEnvelope(
            engine="demo_fallback",
            transcript=transcript,
            word_timestamps=synthesize_timing(transcript),
            latency_ms=latency_ms,
            warnings=warnings,
        )
