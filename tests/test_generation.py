from backend.services.ai import build_grounded_prompt, retrieve_sections


def test_section_retrieval_prefers_job_relevant_evidence() -> None:
    sections = {
        "education": "Studied history and economics",
        "experience": "Built Python FastAPI services and PostgreSQL schemas",
        "projects": "Designed React dashboards",
    }

    ranked = retrieve_sections(sections, "Python backend engineer using FastAPI")

    assert ranked[0][0] == "experience"


def test_generation_prompt_is_grounded_and_marks_gaps() -> None:
    prompt = build_grounded_prompt(
        "cover_letter",
        {"experience": "Built Python APIs."},
        "Backend Engineer",
        "Example Co",
        "Build Java services and APIs.",
        ["java"],
    )

    assert "Built Python APIs" in prompt
    assert "do not claim these as experience" in prompt
    assert "java" in prompt
