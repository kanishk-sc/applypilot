import hashlib
import uuid
from typing import Annotated, Any

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from backend.config import get_settings
from backend.database import get_session
from backend.models import Analysis, GeneratedContent, Job, Resume
from backend.schemas import (
    AnalysisCreate,
    AnalysisResponse,
    GenerationRequest,
    JobCreate,
)
from backend.services.ai import (
    OpenAIService,
    ProviderError,
    build_grounded_prompt,
)
from backend.services.matching import calculate_match, extract_keywords, extract_skills
from backend.services.parsing import DocumentParseError, parse_resume

settings = get_settings()
app = FastAPI(title="ApplyPilot API", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


def get_ai_service() -> OpenAIService:
    try:
        return OpenAIService()
    except ProviderError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


def _analysis_response(analysis: Analysis) -> AnalysisResponse:
    return AnalysisResponse(
        analysis_id=analysis.id,
        resume_id=analysis.resume_id,
        job_id=analysis.job_id,
        match_score=analysis.match_score,
        components={
            "semantic_similarity": analysis.semantic_similarity,
            "skills_coverage": analysis.skills_coverage,
            "keyword_coverage": analysis.keyword_coverage,
            "experience_alignment": analysis.experience_alignment,
        },
        matched_skills=analysis.matched_skills,
        missing_skills=analysis.missing_skills,
        matched_keywords=analysis.matched_keywords,
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def ready(session: Annotated[Session, Depends(get_session)]) -> dict[str, str]:
    try:
        session.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(status_code=503, detail="database_unavailable") from exc
    return {"status": "ready"}


@app.post("/api/resumes", status_code=status.HTTP_201_CREATED)
async def create_resume(
    session: Annotated[Session, Depends(get_session)],
    ai: Annotated[OpenAIService, Depends(get_ai_service)],
    file: UploadFile = File(...),
) -> dict[str, Any]:
    if not file.filename:
        raise HTTPException(status_code=400, detail="filename_required")
    content = await file.read(settings.max_upload_bytes + 1)
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="resume_exceeds_upload_limit")
    digest = hashlib.sha256(content).hexdigest()
    existing = session.scalar(select(Resume).where(Resume.content_sha256 == digest))
    if existing is not None:
        return {
            "resume_id": existing.id,
            "reused": True,
            "sections": list(existing.sections),
        }
    try:
        raw_text, sections = parse_resume(file.filename, content)
    except DocumentParseError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    try:
        embedding = ai.embed(raw_text)
    except ProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    safe_name = file.filename.replace("\\", "/").rsplit("/", 1)[-1][:255]
    resume = Resume(
        original_filename=safe_name,
        content_sha256=digest,
        raw_text=raw_text,
        sections=sections,
        embedding=embedding,
    )
    session.add(resume)
    session.commit()
    return {"resume_id": resume.id, "reused": False, "sections": list(sections)}


@app.post("/api/jobs", status_code=status.HTTP_201_CREATED)
def create_job(
    payload: JobCreate,
    session: Annotated[Session, Depends(get_session)],
    ai: Annotated[OpenAIService, Depends(get_ai_service)],
) -> dict[str, Any]:
    try:
        embedding = ai.embed(payload.description)
    except ProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    job = Job(
        title=payload.title.strip(),
        company=payload.company.strip() if payload.company else None,
        description=payload.description.strip(),
        parsed={
            "skills": extract_skills(payload.description),
            "keywords": extract_keywords(payload.description),
        },
        embedding=embedding,
    )
    session.add(job)
    session.commit()
    return {"job_id": job.id, "parsed": job.parsed}


@app.post(
    "/api/analyses",
    status_code=status.HTTP_201_CREATED,
    response_model=AnalysisResponse,
)
def create_analysis(
    payload: AnalysisCreate,
    session: Annotated[Session, Depends(get_session)],
) -> AnalysisResponse:
    existing = session.scalar(
        select(Analysis).where(
            Analysis.resume_id == payload.resume_id,
            Analysis.job_id == payload.job_id,
        )
    )
    if existing is not None:
        return _analysis_response(existing)
    resume = session.get(Resume, payload.resume_id)
    job = session.get(Job, payload.job_id)
    if resume is None or job is None:
        raise HTTPException(status_code=404, detail="resume_or_job_not_found")
    similarity = session.scalar(
        text(
            "SELECT 1 - (r.embedding <=> j.embedding) "
            "FROM resumes r CROSS JOIN jobs j "
            "WHERE r.id = :resume_id AND j.id = :job_id"
        ),
        {"resume_id": payload.resume_id, "job_id": payload.job_id},
    )
    result = calculate_match(
        resume.raw_text,
        job.description,
        resume.sections,
        float(similarity or 0),
    )
    analysis = Analysis(
        resume_id=resume.id,
        job_id=job.id,
        **result.to_dict(),
    )
    session.add(analysis)
    session.commit()
    return _analysis_response(analysis)


@app.get("/api/analyses/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(
    analysis_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
) -> AnalysisResponse:
    analysis = session.get(Analysis, analysis_id)
    if analysis is None:
        raise HTTPException(status_code=404, detail="analysis_not_found")
    return _analysis_response(analysis)


@app.get("/api/analyses", response_model=list[AnalysisResponse])
def list_analyses(
    session: Annotated[Session, Depends(get_session)],
) -> list[AnalysisResponse]:
    analyses = session.scalars(
        select(Analysis).order_by(Analysis.created_at.desc()).limit(50)
    ).all()
    return [_analysis_response(analysis) for analysis in analyses]


@app.post("/api/analyses/{analysis_id}/generate")
def generate_content(
    analysis_id: uuid.UUID,
    payload: GenerationRequest,
    session: Annotated[Session, Depends(get_session)],
    ai: Annotated[OpenAIService, Depends(get_ai_service)],
) -> dict[str, Any]:
    analysis = session.get(Analysis, analysis_id)
    if analysis is None:
        raise HTTPException(status_code=404, detail="analysis_not_found")
    existing = session.scalar(
        select(GeneratedContent).where(
            GeneratedContent.analysis_id == analysis_id,
            GeneratedContent.kind == payload.kind,
        )
    )
    if existing is not None:
        return {"kind": existing.kind, "content": existing.content, "reused": True}
    resume = session.get(Resume, analysis.resume_id)
    job = session.get(Job, analysis.job_id)
    if resume is None or job is None:
        raise HTTPException(status_code=409, detail="analysis_sources_missing")
    prompt = build_grounded_prompt(
        payload.kind,
        resume.sections,
        job.title,
        job.company,
        job.description,
        analysis.missing_skills,
    )
    try:
        output = ai.generate(prompt)
    except ProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    generated = GeneratedContent(
        analysis_id=analysis.id,
        kind=payload.kind,
        content=output,
        model=settings.generation_model,
    )
    session.add(generated)
    session.commit()
    return {"kind": generated.kind, "content": generated.content, "reused": False}
