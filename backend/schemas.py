import uuid
from typing import Literal

from pydantic import BaseModel, Field


class JobCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    company: str | None = Field(default=None, max_length=255)
    description: str = Field(min_length=50, max_length=50_000)


class AnalysisCreate(BaseModel):
    resume_id: uuid.UUID
    job_id: uuid.UUID


class GenerationRequest(BaseModel):
    kind: Literal["cover_letter", "recruiter_message", "gap_explanation"]


class AnalysisResponse(BaseModel):
    analysis_id: uuid.UUID
    resume_id: uuid.UUID
    job_id: uuid.UUID
    match_score: float
    components: dict[str, float]
    matched_skills: list[str]
    missing_skills: list[str]
    matched_keywords: list[str]
