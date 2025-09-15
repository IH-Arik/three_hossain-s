# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt && \
    pip install --no-cache-dir gunicorn

COPY . /app

EXPOSE 8000

CMD ["gunicorn", "-b", "0.0.0.0:8000", "voting_api:app", "--workers", "2", "--threads", "4", "--timeout", "60"]


