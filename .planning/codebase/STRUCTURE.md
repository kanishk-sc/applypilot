# Repository Structure

**Analysis Date:** 2026-09-18

## Root files

- `app.py` contains all Streamlit pages, controls, state, and workflow orchestration.
- `utils.py` contains parsing, matching, template generation, SQLite access, and tracker aggregation.
- `requirements.txt` lists Streamlit, pandas, scikit-learn, and PyPDF.
- `README.md` provides a short feature list and incomplete setup block.
- `resume.txt` is a committed personal resume sample containing contact information and employment/project claims.

## UI sections in `app.py`

- Analyze Job uploads one resume, accepts a job description, calculates a score, and generates templates.
- Compare Resumes applies the same score to two uploads.
- Application Tracker lists persisted applications and exports CSV.
- Dashboard displays application counts, score averages, statuses, and frequent missing skills.

## Utility concerns

- Parser helpers and domain scoring share a file with SQLite implementation details.
- Global skill lists are part of executable source rather than versioned domain configuration.
- Database functions open a new connection per operation.
- Type annotations and domain models are absent.
- Imported TF-IDF and cosine similarity symbols are dead code.

## Missing target structure

- There is no `src/` package.
- There are no API routers, Pydantic schemas, SQLAlchemy models, migrations, repositories, or service modules.
- There is no `tests/` directory.
- There is no infrastructure, Docker, CI, environment example, or ignore configuration.
- There are no prompt templates, provider adapters, embedding abstractions, or evaluation fixtures.

## Recommended boundaries

- `src/applypilot/api` for FastAPI routers and dependency wiring.
- `src/applypilot/domain` for score models and pure rules.
- `src/applypilot/services` for parsing, embeddings, matching, and generation.
- `src/applypilot/db` for SQLAlchemy models, repositories, and migrations.
- `streamlit_app.py` as a thin API client if Streamlit is retained.

*Structure analysis: 2026-09-18*
