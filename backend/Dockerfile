FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Dependencies first so code changes reuse the cached layer
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
# Tables/columns are created at startup (create_all + ensure_schema_upgrades in app/main.py).
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
