**¿Cómo Funciona la App "Centinela"?**

Este documento explica el flujo de trabajo de la **aplicación** desde que haces clic en "Buscar" hasta que ves los resultados en pantalla.

Este flujo es **asíncrono**, lo que significa que la búsqueda se realiza "en segundo plano" (background) para que la interfaz de usuario sea rápida.

**1\. El Frontend (React)**

- **Qué es:** La interfaz de usuario que ves en <http://localhost:3000>.
- **Cómo lo hace:** Está construida con **React** y **Tailwind CSS**.
- **De dónde lo hace:** Es un archivo index.html estático servido por un contenedor **Nginx** (services/frontend).

**2\. La API (FastAPI)**

- **Qué es:** El "cerebro" y administrador de la aplicación, ubicado en <http://localhost:8000>.
- **Cómo lo hace:** Escucha peticiones en dos endpoints principales:
  - POST /scrape: No hace el scraping. Recibe la palabra clave (ej. "devops") del Frontend y la pone en una "cola de trabajos". Responde "¡Éxito!" inmediatamente.
  - GET /results: Es llamado por el Frontend cada 3 segundos para preguntar: "¿Hay resultados nuevos?". Consulta la base de datos y devuelve los comentarios que encuentra.
- **De dónde lo hace:** Es una aplicación **FastAPI** (Python) en el contenedor api (services/api).

**3\. La Cola de Mensajes (Redis)**

- **Qué es:** Una "sala de espera" súper rápida para los trabajos.
- **Cómo lo hace:** Mantiene una lista llamada scrape_queue. La API (Paso 2) "añade" trabajos a esta lista, y el Worker (Paso 4) los "recoge".
- **De dónde lo hace:** Es un contenedor oficial de **Redis** (redis:7).

**4\. El Worker (Scraper de Python)**

- **Qué es:** El "trabajador" que hace el trabajo pesado.
- **Cómo lo hace:**
  - Se inicia y se queda escuchando permanentemente la cola de Redis (scrape_queue).
  - Cuando ve un nuevo trabajo (ej. {"keyword": "devops"}), lo toma.
  - Llama a la API externa (Hacker News) para buscar comentarios.
  - Se conecta a la base de datos **PostgreSQL**.
  - **Guarda** los resultados (INSERT) en la tabla comments.
- **De dónde lo hace:** Es un script de **Python** (usando requests y psycopg2) en el contenedor scraper (services/scraper).

**5\. La Base de Datos (PostgreSQL)**

- **Qué es:** La "memoria" permanente de la aplicación.
- **Cómo lo hace:** Almacena la tabla comments donde el Worker (Paso 4) guarda los resultados.
- **De dónde lo hace:** Es un contenedor oficial de **PostgreSQL** (postgres:15).
