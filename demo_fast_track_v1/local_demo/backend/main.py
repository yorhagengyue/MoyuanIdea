from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .ai_client import FoursAPIClient
from .asr_engine import ASREngine
from .image_client import GeminiImageClient, GeminiImageError
from .models import (
    AsrResultEnvelope,
    ClassroomAskWhyRequest,
    ClassroomAskWhyResponse,
    ClassroomEvaluateRequest,
    ClassroomEvaluateResponse,
    ScoreRequest,
    ScoreResponse,
)
from .scoring import score_transcript


APP_DIR = Path(__file__).resolve().parent
LOCAL_DEMO_DIR = APP_DIR.parent
DEMO_FAST_TRACK_DIR = LOCAL_DEMO_DIR.parent
PROJECT_ROOT = DEMO_FAST_TRACK_DIR.parent

LESSON_PACK_PATH = PROJECT_ROOT / "phase2_interactive_lesson" / "SAMPLE_LESSON_PACK_MOUNTAIN.json"
MOUNTAIN_IMAGE_PATH = PROJECT_ROOT / "图片example" / "课件4.jpg"
FRONTEND_DIR = LOCAL_DEMO_DIR / "frontend"


app = FastAPI(
    title="Moyuan Local Mountain Demo API",
    version="0.2.0",
    description="Local classroom demo with real AI guidance and resilient fallback.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

asr_engine = ASREngine()
ai_client = FoursAPIClient()
image_client = GeminiImageClient(frontend_dir=FRONTEND_DIR)

if FRONTEND_DIR.exists():
    app.mount("/frontend", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


@app.get("/")
def index() -> FileResponse:
    index_file = FRONTEND_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="Frontend page not found")
    return FileResponse(index_file)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "ai_enabled": ai_client.enabled,
        "image_enabled": image_client.enabled,
        "image_model": image_client.model,
    }


@app.get("/assets/mountain")
def mountain_asset() -> FileResponse:
    if not MOUNTAIN_IMAGE_PATH.exists():
        raise HTTPException(status_code=404, detail="Mountain image not found")
    return FileResponse(MOUNTAIN_IMAGE_PATH)


@app.get("/api/lesson-pack")
def lesson_pack() -> dict:
    if not LESSON_PACK_PATH.exists():
        raise HTTPException(status_code=404, detail="Lesson pack not found")
    try:
        return json.loads(LESSON_PACK_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail=f"Lesson pack parse failed: {exc}") from exc


@app.get("/api/bootstrap")
def bootstrap() -> dict:
    return {
        "role_profile": {
            "role_id": "role_detective_01",
            "role_name": "安静侦探",
            "personality": "安静、认真、会鼓励人",
            "catchphrase": "我们来慢慢找答案。",
            "goal": "帮我把句子说完整。",
        },
        "scroll_history": [
            {
                "day_offset": -1,
                "hero_artwork": "/assets/mountain",
                "proud_moment": "这是山。",
                "teacher_note": "今天愿意开口，但句子还短。",
                "next_preview": "下次试试用“因为”说理由。",
            }
        ],
        "demo_session": {
            "session_id": "session_mountain_demo_01",
            "student_id": "stu_xq",
            "mode": "quick",
            "fallback_active": False,
            "current_node": "n1_intro",
            "highlight_sentence": "",
        },
    }


@app.get("/api/classroom/option-images")
def classroom_option_images(refresh: bool = False) -> dict:
    try:
        items = image_client.ensure_option_images(force=refresh)
    except GeminiImageError as exc:
        raise HTTPException(status_code=500, detail=f"image generation failed: {exc}") from exc

    return {
        "engine": image_client.model,
        "items": items,
    }


@app.post("/api/classroom/ask-why", response_model=ClassroomAskWhyResponse)
def classroom_ask_why(req: ClassroomAskWhyRequest) -> ClassroomAskWhyResponse:
    concept = req.selected_concept.strip()
    if not concept:
        raise HTTPException(status_code=400, detail="selected_concept is required")
    question, encouragement, engine = ai_client.ask_why(concept)
    return ClassroomAskWhyResponse(question=question, encouragement=encouragement, engine=engine)


@app.post("/api/classroom/evaluate", response_model=ClassroomEvaluateResponse)
def classroom_evaluate(req: ClassroomEvaluateRequest) -> ClassroomEvaluateResponse:
    concept = req.selected_concept.strip()
    answer = req.student_answer.strip()
    if not concept:
        raise HTTPException(status_code=400, detail="selected_concept is required")
    if not answer:
        raise HTTPException(status_code=400, detail="student_answer is required")
    return ai_client.evaluate_answer(concept, answer)


@app.post("/asr/transcribe", response_model=AsrResultEnvelope)
async def transcribe_audio(
    audio: UploadFile = File(...),
    optional_reference_text: str | None = Form(default=None),
) -> AsrResultEnvelope:
    body = await audio.read()
    if not body:
        raise HTTPException(status_code=400, detail="audio is empty")
    return asr_engine.transcribe(body, optional_reference_text=optional_reference_text)


@app.post("/asr/score", response_model=ScoreResponse)
def score_audio(req: ScoreRequest) -> ScoreResponse:
    if not req.transcript.strip():
        raise HTTPException(status_code=400, detail="transcript cannot be empty")
    return score_transcript(req.transcript, req.reference_text, req.timing)
