from __future__ import annotations

from pydantic import BaseModel, Field


class DemoSessionState(BaseModel):
    session_id: str
    student_id: str
    current_node: str
    mode: str
    fallback_active: bool
    highlight_sentence: str = ""


class EvidenceItem(BaseModel):
    source_type: str
    source_ref_id: str
    session_id: str
    visibility_scope: str
    review_status: str


class GrowthScrollView(BaseModel):
    hero_artwork: str
    proud_moment: str
    teacher_note: str
    next_preview: str
    day_offset: int = 0


class RoleProgressCard(BaseModel):
    mission_done: str
    upgraded_sentence: str
    vocabulary_loot: list[str] = Field(default_factory=list)
    next_mission: str


class WordTimestamp(BaseModel):
    word: str
    start: float
    end: float
    confidence: float | None = None


class AsrResultEnvelope(BaseModel):
    engine: str
    transcript: str
    word_timestamps: list[WordTimestamp] = Field(default_factory=list)
    latency_ms: int
    warnings: list[str] = Field(default_factory=list)


class ErrorItem(BaseModel):
    type: str
    expected: str | None = None
    recognized: str | None = None
    start: float | None = None
    end: float | None = None
    reason: str


class ScoreBundle(BaseModel):
    accuracy: float
    fluency: float
    completeness: float
    overall: float


class ScoreRequest(BaseModel):
    transcript: str
    reference_text: str | None = None
    timing: list[WordTimestamp] = Field(default_factory=list)


class ScoreResponse(BaseModel):
    errors: list[ErrorItem]
    scores: ScoreBundle
    feedback: str


class ClassroomAskWhyRequest(BaseModel):
    selected_concept: str


class ClassroomAskWhyResponse(BaseModel):
    question: str
    encouragement: str
    engine: str


class ClassroomIssueItem(BaseModel):
    type: str
    message: str


class ClassroomEvaluateRequest(BaseModel):
    selected_concept: str
    student_answer: str


class ClassroomEvaluateResponse(BaseModel):
    is_correct: bool
    overall_judgement: str
    strengths: list[str] = Field(default_factory=list)
    issues: list[ClassroomIssueItem] = Field(default_factory=list)
    corrected_sentence: str
    feedback_to_child: str
    next_hint: str
    engine: str
