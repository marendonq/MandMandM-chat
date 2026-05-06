FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY frontend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY frontend/server.py ./server.py
COPY frontend/static ./static

EXPOSE 3000

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "3000"]
