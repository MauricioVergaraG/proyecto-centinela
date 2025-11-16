import requests
import redis
import json
import time
import os
import psycopg2  # ¡NUEVO IMPORT!
from psycopg2.extras import execute_values

# ============================ 1. Configuración ============================

# --- Configuración de Redis ---
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
r = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)

# --- ¡NUEVO! Configuración de PostgreSQL ---
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
            print(f"Error conectando a PostgreSQL: {e}. Reintentando en 5 segundos...")
            time.sleep(5)


def setup_database():
    """Asegura que la tabla 'comments' exista."""
    connect_to_db()  # Asegura que estemos conectados
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


# ============================ 2. Lógica de Scraping (Hacker News) ============================


def get_hacker_news_comments(keyword, limit=25):
    # ... (Esta función es idéntica a la anterior)
    comments_data = []
    API_URL = f"http://hn.algolia.com/api/v1/search?query={keyword}&tags=comment"
    try:
        print(f"Contactando API de Hacker News para '{keyword}'...")
        response = requests.get(API_URL)
        response.raise_for_status()
        results = response.json()
        for hit in results.get("hits", []):
            if hit.get("comment_text") and hit.get("author"):
                comments_data.append(
                    {
                        "author": hit.get("author"),
                        "body": hit.get("comment_text"),
                        "score": hit.get("points") or 0,  # <--- ¡ARREGLADO!
                        "permalink": f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
                    }
                )
                if len(comments_data) >= limit:
                    break
    except requests.exceptions.RequestException as e:
        print(f"Error en la API de Hacker News: {e}")
        return []
    return comments_data[:limit]


# --- ¡NUEVO! Función para guardar en la BD ---
def save_comments_to_db(comments):
    """Guarda una lista de comentarios en la base de datos."""
    if not comments:
        return

    # Prepara los datos para la inserción
    # (autor, body, score, permalink)
    values = [(c["author"], c["body"], c["score"], c["permalink"]) for c in comments]

    try:
        with db_conn.cursor() as cur:
            # execute_values es la forma más rápida de insertar muchos datos
            # ON CONFLICT (permalink) DO NOTHING: Evita duplicados
            execute_values(
                cur,
                """
                INSERT INTO comments (author, body, score, permalink)
                VALUES %s
                ON CONFLICT (permalink) DO NOTHING
                """,
                values,
            )
            print(f"✅ Se guardaron/actualizaron {len(values)} comentarios en la BD.")
    except psycopg2.Error as e:
        print(f"Error al guardar en la BD: {e}")
        db_conn.rollback()  # Deshace la transacción en caso de error
    except Exception as e:
        print(f"Error inesperado en BD: {e}")


# ============================ 3. El Bucle del Worker ============================


def main():
    print("✅ Worker de scraping 'Centinela' (Hacker News) iniciado.")
    print(f"Conectando a Redis en {REDIS_HOST}...")
    setup_database()  # Se conecta a la BD y crea la tabla al iniciar

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
                        f"Iniciando trabajo: Scrapear Hacker News para '{keyword}'..."
                    )

                    comments = get_hacker_news_comments(keyword, limit=50)

                    if comments:
                        # --- ¡CAMBIO! ---
                        # En lugar de solo imprimir, ¡ahora guardamos!
                        save_comments_to_db(comments)
                    else:
                        print("❌ Trabajo completado: No se encontraron comentarios.")

        except redis.exceptions.ConnectionError as e:
            print(f"Error de conexión con Redis: {e}. Reintentando...")
            time.sleep(5)
        except Exception as e:
            print(f"Error inesperado: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
