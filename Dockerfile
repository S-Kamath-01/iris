# Dockerfile
FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    NLTK_DATA=/usr/share/nltk_data

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p $NLTK_DATA \
    && python -c "import nltk; nltk.download('stopwords', download_dir='$NLTK_DATA')"

COPY . .

RUN groupadd -r appuser && useradd -r -g appuser appuser \
    && chown -R appuser:appuser /app "$NLTK_DATA"
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=15s --retries=3 \
    CMD ["python", "-c", "import urllib.request,sys; r=urllib.request.urlopen('http://localhost:8000/health'); sys.exit(0 if r.status==200 else 1)"]

CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]