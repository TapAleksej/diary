FROM python:3.13-slim
WORKDIR /app
COPY . .


RUN apt-get update && \
apt-get install -y --no-install-recommends curl libpq-dev && \
rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]