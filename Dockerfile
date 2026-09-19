FROM python:3.11-slim AS base

WORKDIR /app
COPY requirements.txt requirements-dev.txt pyproject.toml ./
RUN pip install --no-cache-dir -r requirements.txt
RUN groupadd --gid 10001 applypilot && useradd --uid 10001 --gid applypilot --no-create-home applypilot
COPY --chown=applypilot:applypilot . .

FROM base AS runtime
USER applypilot
EXPOSE 8010 8501
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8010"]

FROM base AS test
RUN pip install --no-cache-dir -r requirements-dev.txt
USER applypilot
CMD ["pytest"]
