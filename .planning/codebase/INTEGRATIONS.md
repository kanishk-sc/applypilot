# External Integrations

**Analysis Date:** 2026-09-18

## Current integrations

- Streamlit supplies the browser UI, file upload controls, state, tables, charts, and downloads.
- PyPDF parses in-memory PDF uploads.
- SQLite persists application tracker records to a local file.
- pandas reads and summarizes those records.

## Claimed but absent

- No OpenAI import, API key, HTTP call, model name, prompt client, or SDK dependency exists.
- No GitHub Actions workflow exists.
- No deployment configuration or live URL exists.
- No PostgreSQL or pgvector connection exists.
- No embedding provider or local embedding model exists.

## File handling

- Uploaded TXT files are decoded as UTF-8 with invalid bytes ignored.
- Uploaded PDFs are read fully into memory and parsed page by page.
- Resumes are not persisted by the application.
- A real-looking `resume.txt` with personal contact information and resume claims is committed to the public repository.

## Database behavior

- `init_db` creates one `applications` table if absent.
- `save_application` inserts tracker records with a local wall-clock timestamp string.
- `load_applications` reads all rows ordered by descending ID.
- There are no constraints beyond the integer primary key.

## Future integration boundaries

- A FastAPI service should own parsing, scoring, persistence, and generation contracts.
- An embedding adapter should support a deterministic/offline test double and a documented production provider.
- PostgreSQL with pgvector should persist one embedding per normalized resume/job representation.
- LLM generation should receive only grounded parsed sections and retrieved evidence.

## Privacy boundary

- Future provider calls must document what resume/job text leaves the local system.
- Logs and test fixtures must avoid personal contact information.

*Integration analysis: 2026-09-18*
