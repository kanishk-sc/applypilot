import os

import pytest
from sqlalchemy import text

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://applypilot:applypilot-local-only@localhost:5434/applypilot",
)

from backend.database import engine  # noqa: E402


@pytest.fixture(autouse=True)
def clean_database():
    with engine.begin() as connection:
        connection.execute(
            text(
                "TRUNCATE generated_content, analyses, jobs, resumes "
                "RESTART IDENTITY CASCADE"
            )
        )
    yield
