FROM python:3.13-slim
WORKDIR /app/web-ui
COPY . .

RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["uvicorn", "reader-bot/main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]