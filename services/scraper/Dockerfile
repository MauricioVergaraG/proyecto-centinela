# services/scraper/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias (requests, redis, psycopg2)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del worker
COPY worker.py .
# (¡Nota que la línea 'COPY __init__.py .' se ha eliminado!)

# --- Variables de entorno ---
# (Ya no necesitamos las claves de Reddit)
ENV REDIS_HOST="redis"
ENV DB_HOST="db"

# Comando para iniciar el worker
# El flag '-u' (unbuffered) fuerza a que los 'print()' salgan
# a la consola de Docker inmediatamente.
CMD ["python", "-u", "worker.py"]
