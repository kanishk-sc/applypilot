import re
from collections import Counter
from dataclasses import asdict, dataclass

SKILLS = {
    "airflow",
    "aws",
    "azure",
    "celery",
    "docker",
    "fastapi",
    "flask",
    "git",
    "java",
    "javascript",
    "kafka",
    "kubernetes",
    "linux",
    "machine learning",
    "mongodb",
    "mysql",
    "node.js",
    "openai",
    "pandas",
    "postgresql",
    "power bi",
    "python",
    "react",
    "redis",
    "rest api",
    "snowflake",
    "spark",
    "sql",
    "tableau",
    "terraform",
    "typescript",
}
STOP_WORDS = {
    "and",
    "are",
    "for",
    "from",
    "have",
    "our",
    "that",
    "the",
    "this",
    "with",
    "will",
    "you",
    "your",
    "years",
}


def _normalized(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def extract_skills(text: str) -> list[str]:
    normalized = _normalized(text)
    found = {
        skill
        for skill in SKILLS
        if re.search(rf"(?<![a-z0-9]){re.escape(skill)}(?![a-z0-9])", normalized)
    }
    return sorted(found)


def extract_keywords(text: str, *, limit: int = 20) -> list[str]:
    words = re.findall(r"[a-z][a-z0-9+#.-]{2,}", text.lower())
    counts = Counter(word for word in words if word not in STOP_WORDS)
    return [word for word, _ in counts.most_common(limit)]


@dataclass(frozen=True)
class MatchResult:
    match_score: float
    semantic_similarity: float
    skills_coverage: float
    keyword_coverage: float
    experience_alignment: float
    matched_skills: list[str]
    missing_skills: list[str]
    matched_keywords: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


def calculate_match(
    resume_text: str,
    job_text: str,
    resume_sections: dict[str, str],
    semantic_similarity: float,
) -> MatchResult:
    resume_skills = set(extract_skills(resume_text))
    job_skills = set(extract_skills(job_text))
    matched_skills = sorted(resume_skills & job_skills)
    missing_skills = sorted(job_skills - resume_skills)
    skills_coverage = len(matched_skills) / len(job_skills) if job_skills else 0.0

    job_keywords = extract_keywords(job_text)
    resume_words = set(extract_keywords(resume_text, limit=200))
    matched_keywords = sorted(set(job_keywords) & resume_words)
    keyword_coverage = (
        len(matched_keywords) / len(job_keywords) if job_keywords else 0.0
    )

    experience_text = " ".join(
        resume_sections.get(name, "") for name in ("experience", "projects")
    )
    experience_skills = set(extract_skills(experience_text))
    experience_alignment = (
        len(experience_skills & job_skills) / len(job_skills) if job_skills else 0.0
    )
    semantic = min(max(semantic_similarity, 0.0), 1.0)
    score = 100 * (
        semantic * 0.50
        + skills_coverage * 0.25
        + keyword_coverage * 0.15
        + experience_alignment * 0.10
    )
    return MatchResult(
        match_score=round(score, 2),
        semantic_similarity=round(semantic * 100, 2),
        skills_coverage=round(skills_coverage * 100, 2),
        keyword_coverage=round(keyword_coverage * 100, 2),
        experience_alignment=round(experience_alignment * 100, 2),
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        matched_keywords=matched_keywords,
    )
