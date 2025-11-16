# services/api/main.py
# Autor: Mauricio Vergara
# API de FastAPI para Proyecto Centinela (Conectada a Redis)

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis
import json
import os

# --- 1. Configuración ---
app = FastAPI(title="Centinela API", version="0.1.0")

# Conexión a Redis (usa el 'hostname' del servicio de docker-compose)
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
r = None # Inicializamos como None

try:
    # 'decode_responses=True' es importante para que Redis devuelva strings
    r = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)
    r.ping() # Prueba la conexión al inicio
    print(f"Conectado exitosamente a Redis en {REDIS_HOST}")
except redis.exceptions.ConnectionError as e:
    print(f"FATAL: No se pudo conectar a Redis en {REDIS_HOST}. {e}")
    # Si no se puede conectar, 'r' seguirá siendo None y el endpoint /scrape fallará

# --- 2. Modelo de Datos (Pydantic) ---
# Modelo para el endpoint de health
class Health(BaseModel):
    status: str

# Modelo para la solicitud de scraping (¡actualizado!)
# Ya no pedimos 'url', pedimos 'keyword' para Hacker News
class ScrapeRequest(BaseModel):
    keyword: str

# --- 3. Endpoints de la API ---

@app.get("/", include_in_schema=False) # Oculta este de la UI de /docs
def read_root():
    return {"Proyecto": "Centinela API"}

@app.get("/health", response_model=Health, tags=["Monitoring"])
async def health():
    """Devuelve el estado de la API y (si es posible) de Redis."""
    redis_status = "ok"
    if r is None:
        redis_status = "disconnected"
    else:
        try:
            r.ping()
        except redis.exceptions.ConnectionError:
            redis_status = "disconnected"

    if redis_status == "ok":
        return {"status": "ok", "redis": redis_status}

    # Si Redis falla, devolvemos un error 503
    raise HTTPException(status_code=503, detail={"status": "error", "redis": redis_status})

@app.get("/version", tags=["Monitoring"])
async def version():
    """Devuelve la versión de la API."""
    return {"version": "0.1.0", "author": "Mauricio Vergara"}

# --- ¡ENDPOINT PRINCIPAL ACTUALIZADO! ---
@app.post("/scrape", tags=["Scraping"])
async def create_scraping_job(request: ScrapeRequest):
    """
    Recibe una palabra clave (keyword), la empaqueta como un trabajo
    y la envía a la cola 'scrape_queue' en Redis para el worker.
    """
    if r is None:
        raise HTTPException(status_code=503, detail="Servicio de Redis no disponible.")

    try:
        # 1. Crear el "trabajo" (ahora más simple)
        job_data = {
            "keyword": request.keyword
        }

        # 2. Convertir a JSON y ponerlo en la cola 'scrape_queue'
        r.rpush('scrape_queue', json.dumps(job_data))

        print(f"Nuevo trabajo enviado a 'scrape_queue': '{request.keyword}'")

        # 3. Devolver respuesta inmediata al usuario
        return {
            "status": "success",
            "message": "Trabajo de scraping (Hacker News) iniciado.",
            "job_details": job_data
        }

    except redis.exceptions.ConnectionError as e:
        raise HTTPException(status_code=503, detail=f"No se pudo conectar a Redis: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {e}")
