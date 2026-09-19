import pytest

from backend.services.parsing import DocumentParseError, parse_resume


def test_text_resume_sections_handle_unusual_spacing() -> None:
    content = (
        b"Jane Example\n\nTECHNICAL SKILLS\nPython, SQL\n\n"
        b"WORK EXPERIENCE\nBuilt APIs and data pipelines."
    )

    text, sections = parse_resume("resume.txt", content)

    assert "Jane Example" in text
    assert sections["skills"] == "Python, SQL"
    assert "Built APIs" in sections["experience"]


@pytest.mark.parametrize(
    ("filename", "content", "error"),
    [
        ("resume.pdf", b"not a pdf", "invalid_pdf_signature"),
        ("resume.pdf", b"%PDF-broken", "malformed_pdf"),
        ("resume.txt", b"", "resume_has_insufficient_text"),
        ("resume.docx", b"content", "unsupported_file_type"),
    ],
)
def test_invalid_or_empty_resume_is_rejected(
    filename: str, content: bytes, error: str
) -> None:
    with pytest.raises(DocumentParseError, match=error):
        parse_resume(filename, content)
