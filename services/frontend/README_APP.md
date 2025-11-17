# ¿Cómo Funciona la App "Centinela"?

Este documento explica el flujo de trabajo de la aplicación desde que haces clic en "Buscar" hasta que ves los resultados en pantalla.  
El flujo es **asíncrono**, lo que significa que la búsqueda se realiza en **segundo plano** (background) para que la interfaz de usuario sea rápida.

---

## 1. El Frontend (React)

**Qué es:** La interfaz de usuario que ves en [http://localhost:3000](http://localhost:3000).  

**Cómo lo hace:** Construida con **React** y **Tailwind CSS** (cargados desde CDN).  

**De dónde lo hace:** Archivo `index.html` estático servido por un contenedor **Nginx** (`services/frontend`).  

**Flujo:**
1. Escribes una palabra clave (ej. `"IA"`) y un idioma (ej. `"es"`).  
2. La app React realiza una petición **POST** a la API (`/scrape`).  
3. Al mismo tiempo, la aplicación empieza a **sondear** (`polling`) el endpoint `/results` cada 3 segundos, pidiendo los artículos más nuevos.

---

## 2. El Backend (FastAPI)

**Qué es:** El "cerebro" y administrador de la aplicación, ubicado en [http://localhost:8000](http://localhost:8000).  

**Cómo lo hace:** Escucha peticiones en dos endpoints principales:

- **POST /scrape:**  
  - No hace el scraping directamente.  
  - Recibe la `keyword` y `language` del Frontend y las pone en una **cola de trabajos**.  
  - Responde `"¡Éxito!"` inmediatamente.

- **GET /results:**  
  - Llamado por el Frontend cada 3 segundos.  
  - Consulta la base de datos y devuelve los **50 artículos más recientes** (`ORDER BY created_at DESC`).

**De dónde lo hace:** Aplicación **FastAPI (Python)** en el contenedor `api` (`services/api`).

---

## 3. La Cola de Mensajes (Redis)

**Qué es:** Una "sala de espera" súper rápida para los trabajos.  

**Cómo lo hace:**  
- Mantiene una lista llamada `scrape_queue`.  
- La API (Paso 2) **añade trabajos** (ej. `{"keyword": "IA", "language": "es"}`) a esta lista.

**De dónde lo hace:** Contenedor oficial **Redis** (`redis:7`).

---

## 4. El Worker (Scraper de Python)

**Qué es:** El "trabajador" (o "Chef") que hace el trabajo pesado.  

**Cómo lo hace:**  
1. Se inicia y se queda escuchando permanentemente la cola de Redis (`scrape_queue`).  
2. Cuando ve un nuevo trabajo, lo toma.  
3. Llama a la API externa **NewsAPI.org** para buscar artículos reales que coincidan con la palabra clave y el idioma.  
4. Se conecta a la base de datos **PostgreSQL**.  
5. Guarda (`INSERT`) los resultados en la tabla `comments`.  
   - Si el artículo ya existe (`ON CONFLICT`), actualiza su fecha (`created_at = CURRENT_TIMESTAMP`) para que aparezca primero en la lista.

**De dónde lo hace:** Script de **Python** (usando `requests` y `psycopg2`) en el contenedor `scraper` (`services/scraper`).

---

## 5. La Base de Datos (PostgreSQL)

**Qué es:** La "memoria" permanente de la aplicación.  

**Cómo lo hace:**  
- Almacena la tabla `comments` donde el Worker (Paso 4) guarda los resultados y la API (Paso 2) los lee.

**De dónde lo hace:** Contenedor oficial **PostgreSQL** (`postgres:15`).
