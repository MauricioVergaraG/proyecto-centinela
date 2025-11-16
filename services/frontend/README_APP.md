# ¿Cómo Funciona la App "Centinela"?

Este documento explica el flujo de trabajo de la **aplicación** desde que haces clic en "Buscar" hasta que se obtienen los datos.

Este flujo es asíncrono y utiliza una arquitectura de microservicios para separar responsabilidades.

### 1\. El Frontend (React)

- **Ubicación:** <http://localhost:3000>
- **Qué hace:** Muestras una interfaz de usuario simple (un formulario) construida con React y Tailwind CSS.
- **Acción:** Cuando escribes una palabra clave (ej. "devops") y haces clic en "Buscar", la aplicación React realiza una petición POST a la API de FastAPI.

### 2\. El Backend (FastAPI)

- **Ubicación:** <http://localhost:8000>
- **Qué hace:** Es el "cerebro" o "administrador". Escucha peticiones en el endpoint /scrape.
- **Acción:**
  - Recibe la petición POST del frontend.
  - Valida la entrada (asegura que keyword esté presente).
  - Crea un "trabajo" en formato JSON (ej. {"keyword": "devops"}).
  - **Encola** este trabajo en la cola de **Redis** llamada scrape_queue.
  - Responde **inmediatamente** al frontend con un mensaje de "Éxito", sin esperar a que el scraping termine.

### 3\. La Cola de Mensajes (Redis)

- **Ubicación:** redis:6379 (solo accesible por otros contenedores)
- **Qué hace:** Actúa como una "sala de espera" para los trabajos.
- **Acción:** Almacena la lista de trabajos (scrape_queue) en orden de llegada.

### 4\. El Worker (Scraper de Python)

- **Ubicación:** (Contenedor scraper)
- **Qué hace:** Es el "trabajador". No tiene API. Es un script de Python que se inicia y se queda escuchando la cola de Redis.
- **Acción:**
  - Está permanentemente "bloqueado", esperando un trabajo en scrape_queue.
  - Tan pronto como la API (Paso 2) añade un trabajo, el Worker lo "despierta".
  - Toma el trabajo (ej. {"keyword": "devops"}).
  - Realiza la tarea pesada: llama a la API de Hacker News (<http://hn.algolia.com/>...).
  - Recoge y procesa los comentarios.
  - **(Actualmente)** Imprime los resultados en los logs de Docker.
  - **(Próximo Paso)** Guardará estos resultados en la base de datos **PostgreSQL**.
