# Architecture

**Analysis Date:** 2026-09-18

## Current pattern

- ApplyPilot is a Streamlit monolith with UI orchestration in `app.py` and mixed business/data utilities in `utils.py`.
- Importing `app.py` immediately configures Streamlit and initializes the SQLite database.
- There is no network API or independently testable service layer.
- All features share global constants and a fixed local database filename.

## Analysis flow

1. The user uploads a PDF or TXT resume and pastes a job description.
2. `extract_text_from_file` returns unstructured text.
3. `extract_name` guesses a name from the first short line.
4. Substring checks identify hard-coded skills and soft skills.
5. `calculate_match_score` combines 60% skill coverage, 25% fixed responsibility-term coverage, and 15% soft-skill coverage.
6. Template functions produce application materials from detected strings.
7. The UI optionally saves the summary to SQLite.

## Other flows

- Resume comparison computes the same deterministic score twice.
- Application Tracker displays every SQLite record and supports CSV download.
- Dashboard aggregates counts, mean score, statuses, and missing skills in pandas.

## Data model

- The only persisted entity is an application tracker row.
- Resume text, job text, parsed sections, score components, and generated outputs are not persisted.
- Missing skills are stored as comma-separated text.
- There is no schema versioning or migration history.

## Required target architecture

- Separate pure parsing, extraction, embedding, similarity, scoring, generation, and persistence services.
- FastAPI should expose typed request/response contracts.
- PostgreSQL should own resumes, jobs, normalized sections, embeddings, and analysis results.
- Streamlit may remain a thin client consuming the API.
- Hybrid score components must be individually visible and testable.

## Architectural risks

- Substring matching yields false positives such as `api` inside unrelated words.
- The displayed score is not semantic and should not be marketed as ATS accuracy.
- Template generation can imply experience not supported by resume evidence.

*Architecture analysis: 2026-09-18*
