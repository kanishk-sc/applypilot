# Engineering Conventions

**Analysis Date:** 2026-09-18

## Current Python style

- Functions and variables use snake_case; constants use upper snake case.
- No type annotations are used in application utilities.
- Imports are not consistently grouped or alphabetized.
- Long lists and calls exceed common formatter widths.
- No formatter or linter enforces style.

## Streamlit state

- Session-state keys are initialized individually at module import.
- Page selection is a sidebar radio.
- Actions validate required UI inputs with warnings and errors.
- Analysis output is stored in a loosely typed dictionary.
- Database initialization occurs as an import-time side effect.

## Error handling

- PDF parser exceptions are not caught.
- TXT decode errors are silently ignored.
- Empty extracted text is handled in only the primary Analyze Job flow.
- Resume comparison does not check for empty parsed content.
- SQLite connections are manually closed without context managers or rollback handling.

## Matching rules

- Text is lowercased and whitespace-normalized.
- Skill detection is naive substring membership.
- Results are sorted and deduplicated.
- The score uses fixed weights embedded directly in the function.
- A missing soft-skill list receives an unexplained neutral score of 0.5.

## Generation rules

- Cover letters and recruiter messages are deterministic templates.
- Resume bullets recommend adding evidence rather than fabricating it, which is a useful boundary.
- Generic template language is not grounded in parsed resume sections beyond skill names.

## Documentation conventions

- Current public language uses “AI-powered” and “ATS optimization” without implemented evidence.
- No current-status or planned-feature section exists.
- Setup is not reproducible because dependencies are unpinned and the code fence is malformed.

*Convention analysis: 2026-09-18*
