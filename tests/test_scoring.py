from backend.services.matching import calculate_match


def test_hybrid_score_exposes_weighted_components() -> None:
    resume = "Python SQL FastAPI engineer built PostgreSQL APIs"
    job = "Python SQL FastAPI PostgreSQL engineer needed for APIs"
    result = calculate_match(
        resume,
        job,
        {"experience": resume},
        semantic_similarity=0.8,
    )

    assert result.semantic_similarity == 80.0
    assert result.skills_coverage == 100.0
    assert result.experience_alignment == 100.0
    assert result.match_score <= 100.0
    assert result.missing_skills == []


def test_semantic_similarity_is_clamped() -> None:
    result = calculate_match("Python", "Python role", {}, semantic_similarity=1.2)

    assert result.semantic_similarity == 100.0
