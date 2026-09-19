from fastapi.testclient import TestClient

from backend.main import app, get_ai_service
from backend.services.ai import ProviderError


class FakeAI:
    last_prompt = ""

    def embed(self, text: str) -> list[float]:
        return [1.0] + [0.0] * 1535

    def generate(self, prompt: str) -> str:
        type(self).last_prompt = prompt
        return "Grounded draft"


RESUME_TEXT = (
    b"Jane Example\nSKILLS\nPython SQL FastAPI\n"
    b"EXPERIENCE\nBuilt PostgreSQL APIs for customers."
)


def client() -> TestClient:
    app.dependency_overrides[get_ai_service] = FakeAI
    return TestClient(app)


def test_full_analysis_and_generation_flow() -> None:
    api = client()
    resume = api.post(
        "/api/resumes",
        files={
            "file": (
                "../resume.txt",
                RESUME_TEXT,
                "text/plain",
            )
        },
    )
    assert resume.status_code == 201
    resume_id = resume.json()["resume_id"]

    duplicate = api.post(
        "/api/resumes",
        files={
            "file": (
                "resume.txt",
                RESUME_TEXT,
                "text/plain",
            )
        },
    )
    assert duplicate.json()["reused"] is True

    job = api.post(
        "/api/jobs",
        json={
            "title": "Backend Engineer",
            "company": "Example Co",
            "description": (
                "Build Python FastAPI and PostgreSQL services with SQL and Docker "
                "for customers."
            ),
        },
    )
    assert job.status_code == 201

    analysis = api.post(
        "/api/analyses",
        json={"resume_id": resume_id, "job_id": job.json()["job_id"]},
    )
    assert analysis.status_code == 201
    body = analysis.json()
    assert body["components"]["semantic_similarity"] == 100.0
    assert "docker" in body["missing_skills"]

    generated = api.post(
        f"/api/analyses/{body['analysis_id']}/generate",
        json={"kind": "cover_letter"},
    )
    assert generated.status_code == 200
    assert generated.json()["content"] == "Grounded draft"
    assert "Built PostgreSQL APIs" in FakeAI.last_prompt
    assert "docker" in FakeAI.last_prompt


def test_embedding_failure_returns_safe_error() -> None:
    class FailingAI(FakeAI):
        def embed(self, text: str) -> list[float]:
            raise ProviderError("embedding_request_failed")

    app.dependency_overrides[get_ai_service] = FailingAI
    response = TestClient(app).post(
        "/api/jobs",
        json={
            "title": "Engineer",
            "description": (
                "A sufficiently long job description for request validation and "
                "provider failure."
            ),
        },
    )

    assert response.status_code == 502
    assert response.json() == {"detail": "embedding_request_failed"}
