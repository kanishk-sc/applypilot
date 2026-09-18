# Technology Stack

**Analysis Date:** 2026-09-18

## Runtime and UI

- Python is the only implementation language.
- Streamlit owns the complete application lifecycle and all views in `app.py`.
- pandas supports tracker tables and dashboard aggregation.
- PyPDF extracts text from uploaded resumes.

## Matching

- scikit-learn is declared and TF-IDF/cosine imports exist in `utils.py` but are unused.
- The active match score is deterministic substring coverage over hard-coded skill, soft-skill, and responsibility lists.
- There are no embeddings, vector database, semantic retrieval, or LLM calls.
- Generated cover letters, recruiter messages, bullets, and questions are string templates.

## Persistence

- Python's built-in SQLite driver stores applications in `applications.db`.
- Tables are created with inline SQL in `utils.py`.
- pandas reads tracker rows directly from SQLite.
- There are no migrations, SQLAlchemy models, PostgreSQL settings, or pgvector support.

## Tooling

- `requirements.txt` has four unpinned runtime dependencies.
- There is no project metadata, lock file, lint configuration, type checking, test framework, Dockerfile, Compose file, or CI workflow.
- There is no `.gitignore` or `.env.example`.
- Baseline compilation and utility import succeeded on 2026-09-18.

## Documentation mismatch

- `README.md` claims OpenAI API and GitHub Actions, neither of which exists.
- The README calls template output AI-generated.
- The README setup code fence is not closed.

## Target gaps

- FastAPI, PostgreSQL, pgvector, Alembic, embeddings, provider-backed generation, Docker, pytest, and GitHub Actions all remain unimplemented.

*Stack analysis: 2026-09-18*
