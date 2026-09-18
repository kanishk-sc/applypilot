# Testing Strategy

**Analysis Date:** 2026-09-18

## Current state

- No test framework is declared.
- No test files or fixtures exist.
- No CI workflow runs imports, lint, tests, or Streamlit smoke checks.
- No mock provider is needed today because there is no external model call.
- Baseline compile and utility import succeeded on Python 3.14.

## Untested parser behavior

- Valid text and PDF uploads have no repeatable fixtures.
- Empty PDFs, scanned/image-only PDFs, malformed PDFs, and unusual encodings are untested.
- Name extraction behavior is heuristic and untested.
- Resume comparison does not validate empty extraction.

## Untested scoring behavior

- Skill substring false positives are untested.
- Score weight totals and component bounds are untested.
- Empty resume/job behavior is untested.
- Results do not expose components, making regression diagnosis difficult.
- TF-IDF/cosine imports are unused and have no tests.

## Untested persistence behavior

- Table creation and repeated initialization are untested.
- Inserts, ordering, CSV conversion, and missing-skills aggregation are untested.
- Database errors and concurrent access are untested.
- Local `applications.db` is not ignored because no `.gitignore` exists.

## Target test layers

- Unit tests for PDF/TXT parsing, skill boundaries, embeddings, semantic similarity, and hybrid score calculation.
- Repository tests against PostgreSQL/pgvector with migrations applied.
- FastAPI tests for create/analyze/retrieve behavior and safe errors.
- Prompt-grounding tests that assert unsupported experience is never inserted.
- Provider failures should use deterministic mocks and never consume paid API credits.

## CI recommendation

- Pin a supported Python version and locked dependency set.
- Run Ruff format/lint, pytest, migration checks, and Docker build.
- Keep model and cloud credentials out of pull-request validation.

*Testing analysis: 2026-09-18*
