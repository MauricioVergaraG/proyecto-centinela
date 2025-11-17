import json
import os
import time

import psycopg2  # ¡NUEVO IMPORT!
from psycopg2.extras import execute_values
import redis
import requests

# ============================ 1. Configuración ============================

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
r = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)

DATABASE_URL = os.getenv("DATABASE_URL")
db_conn = None


def connect_to_db():
    """Intenta conectarse a la base de datos."""
    global db_conn
    while db_conn is None:
        try:
            db_conn = psycopg2.connect(DATABASE_URL)
            db_conn.autocommit = True
            print("✅ Worker conectado a PostgreSQL.")
        except psycopg2.OperationalError as e:
            print(
                f"Error conectando a PostgreSQL: {e}. " "Reintentando en 5 segundos..."
            )
            time.sleep(5)


def setup_database():
    """Asegura que la tabla 'comments' exista."""
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
        print("Tabla 'comments' asegurada.")


# ============================ 2. Lógica de Scraping ============================


def get_hacker_news_comments(keyword, limit=25):
    """Obtiene comentarios de Hacker News con una palabra clave."""
    comments_data = []
    api_url = f"http://hn.algolia.com/api/v1/search?query={keyword}&tags=comment"

    try:
        print(f"Contactando API de Hacker News para '{keyword}'...")
        response = requests.get(api_url)
        response.raise_for_status()
        results = response.json()

        for hit in results.get("hits", []):
            if hit.get("comment_text") and hit.get("author"):
                comments_data.append(
                    {
                        "author": hit.get("author"),
                        "body": hit.get("comment_text"),
                        "score": hit.get("points") or 0,
                        "permalink": (
                            "https://news.ycombinator.com/item?id="
                            f"{hit.get('objectID')}"
                        ),
                    }
                )

                if len(comments_data) >= limit:
                    break

    except requests.exceptions.RequestException as e:
        print(f"Error en la API de Hacker News: {e}")
        return []

    return comments_data[:limit]


def save_comments_to_db(comments):
    """Guarda una lista de comentarios en la base de datos."""
    if not comments:
        return

    values = [(c["author"], c["body"], c["score"], c["permalink"]) for c in comments]

    try:
        with db_conn.cursor() as cur:
            execute_values(
                cur,
                """
                INSERT INTO comments (author, body, score, permalink)
                VALUES %s
                ON CONFLICT (permalink) DO UPDATE SET
                    body = EXCLUDED.body,
                    score = EXCLUDED.score,
                    created_at = CURRENT_TIMESTAMP
                """,
                values,
            )
            print(
                f"✅ Se guardaron/actualizaron {len(values)} " "comentarios en la BD."
            )

    except psycopg2.Error as e:
        print(f"Error al guardar en la BD: {e}")
        db_conn.rollback()

    except Exception as e:
        print(f"Error inesperado en BD: {e}")


# ============================ 3. Loop del Worker ============================


def main():
    print("✅ Worker de scraping 'Centinela' iniciado.")
    print(f"Conectando a Redis en {REDIS_HOST}...")
    setup_database()

    while True:
        try:
            with r.client() as conn:
                print("Esperando trabajos en la cola 'scrape_queue'...")
                job = conn.blpop("scrape_queue", 0)

            if job:
                job_data = json.loads(job[1])
                keyword = job_data.get("keyword")

                if keyword:
                    print(
                        f"Iniciando trabajo: Scrapear Hacker News "
                        f"para '{keyword}'..."
                    )

                    comments = get_hacker_news_comments(keyword, limit=50)

                    if comments:
                        save_comments_to_db(comments)
                    else:
                        print(
                            "❌ Trabajo completado: " "No se encontraron comentarios."
                        )

        except redis.exceptions.ConnectionError as e:
            print(f"Error de conexión con Redis: {e}. Reintentando...")
            time.sleep(5)

        except Exception as e:
            print(f"Error inesperado: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
