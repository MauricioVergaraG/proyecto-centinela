# services/api/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis
import json
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

# --- 1. Configuración ---
app = FastAPI(title="Centinela API", version="0.2.0")  # Subimos versión

origins = [
    "http://localhost:3000",
    "http://localhost",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Conexiones ---
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
DATABASE_URL = os.getenv("DATABASE_URL")
r = None
db_conn = None

try:
    r = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)
    r.ping()
    print(f"Conectado exitosamente a Redis en {REDIS_HOST}")
except redis.exceptions.ConnectionError as e:
    print(f"FATAL: No se pudo conectar a Redis en {REDIS_HOST}. {e}")


def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except psycopg2.OperationalError as e:
        print(f"Error conectando a la BD: {e}")
        raise HTTPException(
            status_code=503, detail="Servicio de base de datos no disponible."
        )


# --- 2. Modelo de Datos (Pydantic) ---
class Health(BaseModel):
    status: str


# --- ¡CAMBIO CRÍTICO! ---
# Cambiamos la solicitud: Ya no pedimos keyword, pedimos URL
class AnalyzeRequest(BaseModel):
    url: str


# Mantenemos el modelo de respuesta igual para no romper el frontend por ahora
class AnalysisResult(BaseModel):
    id: int
    author: Optional[str] = "Desconocido"  # Aquí irá el dominio (ej: cnn.com)
    body: str  # Aquí irá el resumen del texto
    score: Optional[int] = 0  # Aquí irá la probabilidad de Fake (0-100)
    permalink: str  # La URL analizada


# --- 3. Endpoints de la API ---


@app.get("/", include_in_schema=False)
def read_root():
    return {"Proyecto": "Centinela API - Detector de Fake News"}


@app.get("/health", response_model=Health, tags=["Monitoring"])
async def health():
    redis_status = "ok"
    if r is None:
        redis_status = "disconnected"
    else:
        try:
            r.ping()
        except redis.exceptions.ConnectionError:
            redis_status = "disconnected"

    db_status = "ok"
    try:
        conn = get_db_connection()
        conn.close()
    except Exception:
        db_status = "disconnected"

    if redis_status == "ok" and db_status == "ok":
        return {"status": "ok", "redis": redis_status, "database": db_status}

    raise HTTPException(
        status_code=503,
        detail={"status": "error", "redis": redis_status, "database": db_status},
    )


@app.get("/version", tags=["Monitoring"])
async def version():
    return {"version": "0.2.0", "author": "Mauricio Vergara"}


# --- ¡NUEVO ENDPOINT DE ANÁLISIS! ---
@app.post("/analyze", tags=["Analysis"])
async def create_analysis_job(request: AnalyzeRequest):
    if r is None:
        raise HTTPException(status_code=503, detail="Servicio de Redis no disponible.")

    if not request.url.startswith("http"):
        raise HTTPException(
            status_code=400, detail="La URL debe comenzar con http:// o https://"
        )

    try:
        # Enviamos la URL a la cola de Redis
        # El worker espera recibir: {"url": "..."}
        job_data = {"url": request.url}

        r.rpush("scrape_queue", json.dumps(job_data))
        print(f"Solicitud de análisis enviada para: '{request.url}'")

        return {
            "status": "success",
            "message": "URL enviada a análisis forense.",
            "url": request.url,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {e}")


# Mantenemos este endpoint para ver el historial de análisis
@app.get("/results", response_model=List[AnalysisResult], tags=["Analysis"])
async def get_results(limit: int = 50):
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Recuperamos los últimos análisis
            cur.execute(
                """
                SELECT id, author, body, score, permalink
                FROM comments
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (limit,),
            )
            results = cur.fetchall()
        return results
    except Exception as e:
        print(f"Error al leer de la BD: {e}")
        raise HTTPException(status_code=500, detail="Error interno al leer resultados.")
    finally:
        if conn:
            conn.close()
