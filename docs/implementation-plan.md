# ApplyPilot implementation checklist

Checkmarks indicate code that was executed or tested locally.

## Service and persistence

- [x] Move parsing, matching and generation behind FastAPI endpoints
- [x] Add PostgreSQL, pgvector and versioned Alembic migrations
- [x] Persist resumes, parsed sections, one embedding per source and analysis results
- [x] Keep Streamlit as an API client rather than the business-logic host

## Matching and generation

- [x] Call a configurable OpenAI embeddings model through a bounded provider client
- [x] Calculate semantic similarity with pgvector's cosine-distance operator
- [x] Expose semantic, skills, keyword and experience component scores
- [x] Ground generated drafts in retrieved resume sections and explicit gaps
- [x] Avoid commercial ATS or accuracy claims

## Quality and safety

- [x] Reject malformed, empty, unsupported and oversized resume uploads
- [x] Test parsing, unusual formatting, skills, provider failures and score calculation
- [x] Exercise the complete API flow against PostgreSQL/pgvector with mocked OpenAI calls
- [x] Remove the tracked personal resume and ignore local secrets and data artifacts
- [x] Run migration, lint, compile and test checks in GitHub Actions

## Honest boundary

- [x] Local PostgreSQL, API and Streamlit health checks verified
- [ ] Live OpenAI embedding/generation call (requires the repository owner's API key)
- [ ] Hosted deployment and authentication
