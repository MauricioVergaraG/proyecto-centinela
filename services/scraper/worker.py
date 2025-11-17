import requests
import redis
import json
import time
import os
import psycopg2
from psycopg2.extras import execute_values

# ============================ 1. Configuración ============================

# --- ¡CAMBIO! ---
# Leemos la nueva clave de API desde las variables de entorno
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

if not NEWS_API_KEY:
    print("FATAL: No se encontró la variable de entorno 'NEWS_API_KEY'.")
    # (El worker fallará, lo cual es correcto)

# --- Configuración de Redis ---
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
r = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)

# --- Configuración de PostgreSQL ---
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
            print(f"Error conectando a PostgreSQL: {e}. Reintentando en 5 segundos...")
            time.sleep(5)

def setup_database():
    connect_to_db()
    with db_conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id SERIAL PRIMARY KEY,
                author VARCHAR(255),
                body TEXT,
                score INTEGER,
                permalink VARCHAR(1024) UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("Tabla 'comments' (artículos) asegurada.")


# ============================ 2. Lógica de Scraping (NewsAPI) ============================

# --- ¡NUEVA FUNCIÓN! ---
def get_news_articles(keyword, language="es", limit=25):
    """
    Busca artículos de noticias usando NewsAPI.
    """
    articles_data = []

    # URL de la API de NewsAPI
    API_URL = "https://newsapi.org/v2/everything"

    params = {
        'q': keyword,
        'language': language,
        'pageSize': limit,
        'apiKey': NEWS_API_KEY
    }

    try:
        print(f"Contactando NewsAPI para '{keyword}' en '{language}'...")
        response = requests.get(API_URL, params=params)
        response.raise_for_status()

        results = response.json()

        for article in results.get('articles', []):
            # Mapeamos los campos de NewsAPI a nuestro modelo de 'comments'
            articles_data.append({
                'author': article.get('author') or "Fuente desconocida",
                'body': f"{article.get('title')} - {article.get('description')}",
                'score': 0, # NewsAPI no tiene 'score'
                'permalink': article.get('url') # 'url' es nuestro 'permalink' único
            })

            if len(articles_data) >= limit:
                break

    except requests.exceptions.RequestException as e:
        print(f"Error en NewsAPI: {e}")
        return []
    except Exception as e:
        print(f"Error al parsear JSON: {e}")
        return []

    return articles_data

# --- Función para guardar en la BD (Modificada para ser más robusta) ---
def save_articles_to_db(articles):
    if not articles:
        return

    values = [(a['author'], a['body'], a['score'], a['permalink']) for a in articles]

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
                values
            )
            print(f"✅ Se guardaron/actualizaron {len(values)} artículos en la BD.")
    except psycopg2.Error as e:
        print(f"Error al guardar en la BD: {e}")
        db_conn.rollback()
    except Exception as e:
        print(f"Error inesperado en BD: {e}")

# ============================ 3. El Bucle del Worker ============================

def main():
    print("✅ Worker de scraping 'Centinela' (NewsAPI) iniciado.")
    print(f"Conectando a Redis en {REDIS_HOST}...")
    setup_database()

    while True:
        try:
            with r.client() as conn:
                print("Esperando trabajos en la cola 'scrape_queue'...")
                job = conn.blpop('scrape_queue', 0)

            if job:
                job_data = json.loads(job[1])
                keyword = job_data.get('keyword')
                language = job_data.get('language', 'es') # 'es' por defecto

                if keyword:
                    print(f"Iniciando trabajo: Scrapear NewsAPI para '{keyword}' en '{language}'...")

                    # --- ¡CAMBIO! ---
                    articles = get_news_articles(keyword, language, limit=50)

                    if articles:
                        save_articles_to_db(articles)
                    else:
                        print(f"❌ Trabajo completado: No se encontraron artículos.")

        except redis.exceptions.ConnectionError as e:
            print(f"Error de conexión con Redis: {e}. Reintentando...")
            time.sleep(5)
        except Exception as e:
            print(f"Error inesperado: {e}")
            time.sleep(5)

if __name__ == '__main__':
    main()
