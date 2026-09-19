from openai import OpenAI

from backend.config import get_settings
from backend.services.matching import extract_keywords


class ProviderError(RuntimeError):
    pass


class OpenAIService:
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.openai_api_key:
            raise ProviderError("openai_api_key_not_configured")
        self.settings = settings
        self.client = OpenAI(
            api_key=settings.openai_api_key,
            timeout=30,
            max_retries=1,
        )

    def embed(self, text: str) -> list[float]:
        try:
            response = self.client.embeddings.create(
                model=self.settings.embedding_model,
                input=text[:30_000],
                dimensions=self.settings.embedding_dimensions,
            )
        except Exception as exc:
            raise ProviderError("embedding_request_failed") from exc
        embedding = response.data[0].embedding
        if len(embedding) != self.settings.embedding_dimensions:
            raise ProviderError("embedding_dimension_mismatch")
        return embedding

    def generate(self, prompt: str) -> str:
        try:
            response = self.client.responses.create(
                model=self.settings.generation_model,
                instructions=(
                    "Use only the supplied resume and job evidence. "
                    "Do not invent skills, "
                    "employment, metrics, credentials, or personal details."
                ),
                input=prompt,
            )
        except Exception as exc:
            raise ProviderError("generation_request_failed") from exc
        output = response.output_text.strip()
        if not output:
            raise ProviderError("generation_returned_empty_output")
        return output


def retrieve_sections(
    sections: dict[str, str], job_description: str, *, limit: int = 3
) -> list[tuple[str, str]]:
    job_terms = set(extract_keywords(job_description, limit=50))
    ranked = []
    for name, content in sections.items():
        content_terms = set(extract_keywords(content, limit=100))
        ranked.append((len(job_terms & content_terms), name, content))
    return [
        (name, content) for _, name, content in sorted(ranked, reverse=True)[:limit]
    ]


def build_grounded_prompt(
    kind: str,
    sections: dict[str, str],
    job_title: str,
    company: str | None,
    job_description: str,
    missing_skills: list[str],
) -> str:
    evidence = retrieve_sections(sections, job_description)
    evidence_text = "\n\n".join(f"[{name}]\n{content}" for name, content in evidence)
    return f"""Create a {kind.replace("_", " ")} for the role below.

Role: {job_title}
Company: {company or "not provided"}
Job description:
{job_description[:12000]}

Most relevant resume sections:
{evidence_text}

Detected gaps (do not claim these as experience):
{", ".join(missing_skills) or "none detected"}
"""
