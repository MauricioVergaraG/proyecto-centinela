# services/scraper/worker.py

import praw
import redis
import json
import time
import os
# import psycopg2 # Lo usaremos en el futuro para guardar en la BD

# ============================ 1. Configuración ============================

# --- Configuración de PRAW ---
# ¡Leemos las claves desde Variables de Entorno!
# Esto es CRÍTICO para DevSecOps. NUNCA escribas tus claves aquí.
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")

# Validar que las claves existan
if not all([REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT]):
    print("FATAL: Faltan variables de entorno de Reddit (CLIENT_ID, CLIENT_SECRET, USER_AGENT).")
    # En un sistema real, saldríamos con error, pero aquí solo advertimos
    # y PRAW fallará más adelante.

reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT
)

# --- Configuración de Redis ---
# 'redis' es el nombre del servicio en docker-compose.yml
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
r = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)


# ============================ 2. Lógica de Scraping ============================

# Esta es la función de tu guía, adaptada para el worker
def get_reddit_comments(subreddit_name, keyword, limit=25):
    """
    Busca comentarios en un subreddit dado que contengan una palabra clave.
    """
    comments_data = []
    try:
        print(f"Contactando API de Reddit para r/{subreddit_name}...")
        subreddit = reddit.subreddit(subreddit_name)
        # Busca en los 5 posts más relevantes
        for submission in subreddit.search(keyword, limit=5):
            submission.comments.replace_more(limit=0)
            for comment in submission.comments.list():
                if hasattr(comment, 'body'):
                    comments_data.append({
                        'author': comment.author.name if comment.author else '[deleted]',
                        'body': comment.body,
                        'score': comment.score,
                        'permalink': f"https://www.reddit.com{comment.permalink}"
                    })
                    if len(comments_data) >= limit: break
                if len(comments_data) >= limit: break
    except Exception as e:
        print(f"Error en PRAW: {e}")
        return [] # Devuelve lista vacía en caso de error

    return comments_data[:limit]

# ============================ 3. El Bucle del Worker ============================

def main():
    print("✅ Worker de scraping 'Centinela' iniciado.")
    print(f"Conectando a Redis en {REDIS_HOST}...")

    while True:
        try:
            # Intenta conectarse y esperar un trabajo
            with r.client() as conn:
                print("Esperando trabajos en la cola 'scrape_queue'...")
                # BLPOP es un "bloqueo" que espera un trabajo
                # '0' significa esperar indefinidamente
                job = conn.blpop('scrape_queue', 0)

            # job será una tupla (nombre_cola, datos_json)
            if job:
                job_data = json.loads(job[1])
                subreddit = job_data.get('subreddit')
                keyword = job_data.get('keyword')

                if subreddit and keyword:
                    print(f"Iniciando trabajo: Scrapear r/{subreddit} para '{keyword}'...")

                    # --- Ejecuta la lógica de scraping ---
                    comments = get_reddit_comments(subreddit, keyword, limit=50)

                    if comments:
                        print(f"✅ Trabajo completado: Se encontraron {len(comments)} comentarios.")

                        # --- Aquí es donde guardarías en la Base de Datos ---
                        # (Por ahora, solo los imprimimos)
                        for c in comments:
                            print(f"  - [Score: {c['score']}] u/{c['author']}: {c['body'][:50]}...")

                        # TODO: Conectar a Postgres y hacer INSERT de 'comments'

                    else:
                        print(f"❌ Trabajo completado: No se encontraron comentarios.")

        except redis.exceptions.ConnectionError as e:
            print(f"Error de conexión con Redis: {e}. Reintentando en 5 segundos...")
            time.sleep(5)
        except Exception as e:
            print(f"Error inesperado en el worker: {e}")
            time.sleep(5)

if __name__ == '__main__':
    main()
