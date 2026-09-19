import re
from io import BytesIO

from pypdf import PdfReader
from pypdf.errors import PdfReadError

SECTION_NAMES = {
    "summary",
    "education",
    "experience",
    "work experience",
    "projects",
    "skills",
    "technical skills",
    "certifications",
}


class DocumentParseError(ValueError):
    pass


def normalize_text(text: str) -> str:
    return "\n".join(line.strip() for line in text.splitlines() if line.strip())


def parse_resume(filename: str, content: bytes) -> tuple[str, dict[str, str]]:
    lower_name = filename.lower()
    if lower_name.endswith(".pdf"):
        if not content.startswith(b"%PDF-"):
            raise DocumentParseError("invalid_pdf_signature")
        try:
            reader = PdfReader(BytesIO(content))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        except (PdfReadError, ValueError, OSError) as exc:
            raise DocumentParseError("malformed_pdf") from exc
    elif lower_name.endswith(".txt"):
        text = content.decode("utf-8", errors="replace")
    else:
        raise DocumentParseError("unsupported_file_type")

    text = normalize_text(text)
    if len(text) < 40:
        raise DocumentParseError("resume_has_insufficient_text")
    return text, parse_sections(text)


def parse_sections(text: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {"profile": []}
    current = "profile"
    for line in text.splitlines():
        heading = re.sub(r"[^a-z ]", "", line.lower()).strip()
        if heading in SECTION_NAMES and len(line) <= 40:
            current = heading.replace("work experience", "experience").replace(
                "technical skills", "skills"
            )
            sections.setdefault(current, [])
            continue
        sections[current].append(line)
    return {
        name: "\n".join(lines).strip()
        for name, lines in sections.items()
        if any(line.strip() for line in lines)
    }
