FROM python:3.13-slim
WORKDIR /app
COPY . .



RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]