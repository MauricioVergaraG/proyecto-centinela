# services/scraper/worker.py

import requests # ¡Cambiamos praw por requests!
import redis
import json
import time
import os
# import psycopg2

# ============================ 1. Configuración ============================

# --- ¡YA NO NECESITAMOS CLAVES DE API! ---
# ... (Se borra toda la configuración de PRAW) ...

# --- Configuración de Redis ---
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
r = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)

# ============================ 2. Lógica de Scraping (Hacker News) ============================

def get_hacker_news_comments(keyword, limit=25):
    """
    Busca comentarios en Hacker News que contengan una palabra clave.
    """
    comments_data = []

    # Esta es la URL de la API pública de HN (Algolia)
    # Buscamos comentarios ('comment') que contengan la 'keyword'
    API_URL = f"http://hn.algolia.com/api/v1/search?query={keyword}&tags=comment"

    try:
        print(f"Contactando API de Hacker News para '{keyword}'...")
        response = requests.get(API_URL)
        response.raise_for_status() # Lanza un error si la petición falla

        results = response.json() # Convierte la respuesta en un diccionario

        # Iteramos sobre los 'hits' (resultados)
        for hit in results.get('hits', []):
            # Nos aseguramos de que tenga texto de comentario y autor
            if hit.get('comment_text') and hit.get('author'):
                comments_data.append({
                    'author': hit.get('author'),
                    'body': hit.get('comment_text'),
                    'score': hit.get('points', 0), # 'points' es el análogo a 'score'
                    'permalink': f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
                })

                if len(comments_data) >= limit:
                    break

    except requests.exceptions.RequestException as e:
        print(f"Error en la API de Hacker News: {e}")
        return []
    except Exception as e:
        print(f"Error al parsear JSON: {e}")
        return []

    return comments_data[:limit]

# ============================ 3. El Bucle del Worker (Idéntico) ============================

def main():
    print("✅ Worker de scraping 'Centinela' (Hacker News) iniciado.")
    print(f"Conectando a Redis en {REDIS_HOST}...")

    while True:
        try:
            with r.client() as conn:
                print("Esperando trabajos en la cola 'scrape_queue'...")
                job = conn.blpop('scrape_queue', 0)

            if job:
                job_data = json.loads(job[1])
                # --- CAMBIO ---
                # Ya no es 'subreddit', ahora solo nos importa 'keyword'
                keyword = job_data.get('keyword')

                if keyword:
                    print(f"Iniciando trabajo: Scrapear Hacker News para '{keyword}'...")

                    # --- Ejecuta la nueva lógica de scraping ---
                    comments = get_hacker_news_comments(keyword, limit=50)

                    if comments:
                        print(f"✅ Trabajo completado: Se encontraron {len(comments)} comentarios.")
                        for c in comments:
                            print(f"  - [Score: {c['score']}] u/{c['author']}: {c['body'][:50]}...")
                        # TODO: Guardar en Postgres
                    else:
                        print(f"❌ Trabajo completado: No se encontraron comentarios.")

        except redis.exceptions.ConnectionError as e:
            print(f"Error de conexión con Redis: {e}. Reintentando...")
            time.sleep(5)
        except Exception as e:
            print(f"Error inesperado: {e}")
            time.sleep(5)

if __name__ == '__main__':
    main()
