# Build context is the repo root so the API can see schema/, samples/, services/ and templates/.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATA_DIR=/data

WORKDIR /app

COPY apps/api/requirements.txt apps/api/requirements.txt
RUN pip install --no-cache-dir -r apps/api/requirements.txt

# Mirror the repo layout so config.REPO_ROOT resolves to /app.
COPY schema/ schema/
COPY samples/ samples/
COPY services/ services/
COPY templates/ templates/
COPY apps/api/ apps/api/

WORKDIR /app/apps/api
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
