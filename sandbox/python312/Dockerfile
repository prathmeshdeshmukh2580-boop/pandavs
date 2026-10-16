FROM python:3.12-slim

# Create sandbox non-root user
RUN useradd -m -u 1001 sandboxuser

WORKDIR /home/sandboxuser/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

USER sandboxuser

CMD ["python", "-c", "print('Python 3.12 sandbox ready')"]
