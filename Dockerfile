# PaluScan — conteneur de démonstration (compatible Hugging Face Spaces, port 7860)
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PALUSCAN_ROOT=/app

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv && uv sync --frozen --no-dev

COPY src ./src
COPY models ./models
COPY reports ./reports

EXPOSE 7860
CMD ["uv", "run", "--no-dev", "python", "-m", "paluscan.app"]
