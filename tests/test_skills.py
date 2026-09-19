from backend.services.matching import extract_keywords, extract_skills


def test_skill_extraction_uses_token_boundaries() -> None:
    skills = extract_skills(
        "Built REST APIs with Python, FastAPI, PostgreSQL and React."
    )

    assert skills == ["fastapi", "postgresql", "python", "react"]
    assert "java" not in extract_skills("javascript")


def test_keywords_are_ranked_without_common_stop_words() -> None:
    keywords = extract_keywords(
        "Python systems and Python APIs for distributed systems"
    )

    assert keywords[:2] == ["python", "systems"]
    assert "and" not in keywords
