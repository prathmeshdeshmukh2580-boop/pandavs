FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-jdk \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from root services and app
COPY apps/api/requirements.txt apps/api/requirements.txt
COPY services/verifier/requirements.txt services/verifier/requirements.txt
COPY services/renderer/requirements.txt services/renderer/requirements.txt

RUN pip install --no-cache-dir \
    -r apps/api/requirements.txt \
    -r services/verifier/requirements.txt \
    -r services/renderer/requirements.txt

# Copy project files
COPY . .

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
