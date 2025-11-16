# services/api/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis
import json
import os
import psycopg2  # ¡NUEVO IMPORT!
from psycopg2.extras import RealDictCursor  # ¡NUEVO! Para resultados como diccionarios
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional  # ¡NUEVO!

# --- 1. Configuración ---
app = FastAPI(title="Centinela API", version="0.1.0")

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
DATABASE_URL = os.getenv("DATABASE_URL")  # ¡NUEVO!
r = None
db_conn = None

try:
    r = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)
    r.ping()
    print(f"Conectado exitosamente a Redis en {REDIS_HOST}")
except redis.exceptions.ConnectionError as e:
    print(f"FATAL: No se pudo conectar a Redis en {REDIS_HOST}. {e}")


# --- ¡NUEVO! Función para conectar a la BD ---
def get_db_connection():
    """Se conecta a la BD. Lanza excepción si falla."""
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


class ScrapeRequest(BaseModel):
    keyword: str


# ¡NUEVO! Modelo para el comentario (Respuesta)
class Comment(BaseModel):
    id: int
    author: Optional[str] = None  # <- Añadido por si acaso
    body: str
    score: Optional[int] = 0  # <--- ¡ARREGLADO!
    permalink: str


# --- 3. Endpoints de la API ---


@app.get("/", include_in_schema=False)
def read_root():
    return {"Proyecto": "Centinela API"}


@app.get("/health", response_model=Health, tags=["Monitoring"])
async def health():
    # ... (código de health check sin cambios) ...
    # ... (Revisión de Redis...)
    redis_status = "ok"
    if r is None:
        redis_status = "disconnected"
    else:
        try:
            r.ping()
        except redis.exceptions.ConnectionError:
            redis_status = "disconnected"

    # ¡NUEVO! Revisión de la BD
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
    return {"version": "0.1.0", "author": "Mauricio Vergara"}


@app.post("/scrape", tags=["Scraping"])
async def create_scraping_job(request: ScrapeRequest):
    # ... (código de /scrape sin cambios) ...
    if r is None:
        raise HTTPException(status_code=503, detail="Servicio de Redis no disponible.")
    try:
        job_data = {"keyword": request.keyword}
        r.rpush("scrape_queue", json.dumps(job_data))
        print(f"Nuevo trabajo enviado a 'scrape_queue': '{request.keyword}'")
        return {
            "status": "success",
            "message": "Trabajo de scraping (Hacker News) iniciado.",
            "job_details": job_data,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {e}")


# --- ¡NUEVO ENDPOINT! ---
@app.get("/results", response_model=List[Comment], tags=["Scraping"])
async def get_results(limit: int = 50):
    """
    Obtiene los últimos comentarios guardados de la base de datos.
    """
    conn = None
    try:
        conn = get_db_connection()
        # RealDictCursor devuelve cada fila como un diccionario (¡perfecto para JSON!)
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
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
