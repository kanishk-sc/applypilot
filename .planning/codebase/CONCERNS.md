# Technical Concerns

**Analysis Date:** 2026-09-18

## Misleading public claims

- The README claims OpenAI API even though no provider integration exists.
- The README claims GitHub Actions even though `.github/workflows` is absent.
- “AI-generated” outputs are deterministic string templates.
- “ATS optimization” is not supported by an ATS evaluation or commercial ATS integration.
- These claims should be removed before any architecture expansion.

## Correctness

- Substring skill matching can treat partial words as evidence.
- `api` and other short tokens are especially prone to false positives.
- The responsibility denominator includes every fixed term, not job-specific terms, suppressing scores unpredictably.
- A job with no soft skills receives a free 7.5 percentage points.
- The score is not decomposed for explanation or debugging.

## Security and privacy

- `resume.txt` exposes personal email, phone number, and resume claims in a public repository.
- There is no `.gitignore`, so `applications.db`, caches, and environment files can be committed accidentally.
- Uploaded content is not size-limited.
- Future LLM calls could send sensitive resume data without a documented consent/privacy boundary.

## Maintainability

- Streamlit UI, domain rules, generation, and storage are tightly coupled.
- Import-time database initialization makes isolated testing harder.
- Dependencies are unpinned and no lock file exists.
- SQLite schema changes cannot be migrated safely.
- Dead scikit-learn imports suggest unfinished matching work.

## Reliability and operations

- No structured logs, health checks, error telemetry, tests, or CI exist.
- PDF exceptions can terminate a user interaction.
- Local-time string timestamps are ambiguous.
- There is no Docker or repeatable service setup.

## Hiring-manager risk

- Current evidence supports a small deterministic Streamlit prototype, not AI engineering or semantic search.
- The false README claims are more damaging than the missing features.
- Highest value is truthful cleanup followed by a tested FastAPI/domain extraction, then PostgreSQL/pgvector and actual embeddings.

*Concern analysis: 2026-09-18*
