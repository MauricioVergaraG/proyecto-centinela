import requests
from bs4 import BeautifulSoup
import redis
import json
import time
import os
import psycopg2
from urllib.parse import urlparse

# NOTA: Se eliminó 'from psycopg2.extras import execute_values' que causaba el error F401

# --- Configuración ---
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
r = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)
DATABASE_URL = os.getenv("DATABASE_URL")
db_conn = None


def connect_to_db():
    global db_conn
    while db_conn is None:
        try:
            db_conn = psycopg2.connect(DATABASE_URL)
            db_conn.autocommit = True
            print("✅ Worker conectado a PostgreSQL.")
        except psycopg2.OperationalError as e:
            print(f"Reintentando DB en 5s... {e}")
            time.sleep(5)


def setup_database():
    connect_to_db()
    with db_conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS comments (
                id SERIAL PRIMARY KEY,
                author VARCHAR(255),
                body TEXT,
                score INTEGER, 
                permalink VARCHAR(1024) UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """
        )


# --- Lógica de Análisis Mejorada ---
def analizar_contenido(titulo, texto):
    puntaje = 0
    razones = []

    # 1. Título Clickbait
    palabras_alarma = [
        "URGENTE",
        "INCREÍBLE",
        "SHOCK",
        "FINALMENTE",
        "SECRETO",
        "VIRAL",
        "MUERTE",
    ]
    if any(p in titulo.upper() for p in palabras_alarma):
        puntaje += 25
        razones.append("Lenguaje alarmista en título")

    # 2. Mayúsculas excesivas
    if titulo.isupper() or sum(1 for c in titulo if c.isupper()) / len(titulo) > 0.6:
        puntaje += 20
        razones.append("Uso excesivo de mayúsculas")

    # 3. Palabras de conflicto en cuerpo
    palabras_polarizantes = [
        "traición",
        "destruir",
        "vergüenza",
        "conspiración",
        "farsa",
    ]
    count_polar = sum(1 for p in palabras_polarizantes if p in texto.lower())
    if count_polar > 0:
        puntaje += 15
        razones.append(f"Detectadas {count_polar} palabras polarizantes")

    # 4. Texto muy corto (sospechoso)
    if len(texto.split()) < 150:
        puntaje += 10
        razones.append("Artículo sospechosamente corto")

    return min(puntaje, 100), razones


def scrapear_sitio_web(url):
    # --- MODO SIMULACRO ---
    if "simulacro" in url:
        return {
            "author": "dark-web-fake.com",
            "body": "REPORT_METADATA:['Título alarmista', 'Fuente no verificada', 'Texto generado artificialmente']::: ¡URGENTE! ¡INCREÍBLE! LO QUE NO QUIEREN QUE SEPAS. Este es un texto de prueba simulado para validar el sistema de alertas.",
            "score": 95,
            "permalink": url,
        }

    # --- SCRAPING REAL ---
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124"
    }
    try:
        print(f"Analizando: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        titulo = (
            soup.find("h1").get_text(strip=True) if soup.find("h1") else "Sin título"
        )
        texto_cuerpo = (
            " ".join([p.get_text(strip=True) for p in soup.find_all("p")])
            or "Sin texto legible"
        )

        puntaje, razones = analizar_contenido(titulo, texto_cuerpo)

        body_con_metadata = f"REPORT_METADATA:{json.dumps(razones)}::: {texto_cuerpo}"

        return {
            "author": urlparse(url).netloc,
            "body": body_con_metadata,
            "score": puntaje,
            "permalink": url,
        }
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None


def save_analysis_to_db(data):
    if not data:
        return
    try:
        with db_conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO comments (author, body, score, permalink)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (permalink) DO UPDATE SET
                    body = EXCLUDED.body,
                    score = EXCLUDED.score,
                    created_at = CURRENT_TIMESTAMP;
            """,
                (data["author"], data["body"], data["score"], data["permalink"]),
            )
            print(f"✅ Guardado: {data['score']}% Fake")
    except Exception as e:
        print(f"Error BD: {e}")
        db_conn.rollback()


def main():
    print("✅ Worker Centinela v2.0 INICIADO")
    setup_database()
    while True:
        try:
            with r.client() as conn:
                job = conn.blpop("scrape_queue", 0)
                if job:
                    data = json.loads(job[1])
                    url = data.get("url")
                    if url:
                        res = scrapear_sitio_web(url)
                        save_analysis_to_db(res)
        except Exception as e:
            # CORRECCIÓN ERROR F841: Ahora usamos la variable 'e' imprimiéndola
            print(f"Error en loop principal: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
