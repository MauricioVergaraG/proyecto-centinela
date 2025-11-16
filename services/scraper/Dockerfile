# services/scraper/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias (praw, redis, psycopg2)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del worker
COPY worker.py .
COPY __init__.py .

# ¡Importante! Estas son las variables que el worker.py espera.
# Las pasaremos desde docker-compose.yml, pero es bueno definirlas.
ENV REDDIT_CLIENT_ID=""
ENV REDDIT_CLIENT_SECRET=""
ENV REDDIT_USER_AGENT=""
ENV REDIS_HOST="redis"
ENV DB_HOST="db"

# Comando para iniciar el worker
CMD ["python", "-u", "worker.py"]
