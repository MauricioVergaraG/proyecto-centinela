# Proyecto Centinela 🛡️

![Pipeline de CI/CD - DevSecOps](https://github.com/MauricioVergaraG/proyecto-centinela/actions/workflows/ci-cd.yml/badge.svg)

Este repositorio contiene el trabajo práctico "Proyecto Centinela", un ejercicio de implementación de un **pipeline DevSecOps de ciclo completo** para una plataforma contenerizada de análisis de desinformación (OSINT).

El objetivo principal **no es** la aplicación en sí, sino la **construcción, automatización y aseguramiento de todo el ciclo de vida de la aplicación (CI/CD/CS)**, utilizando exclusivamente herramientas de código abierto (FOSS) y un enfoque 100% contenerizado.

---

## 1. Contexto de la Aplicación "Centinela"

La aplicación es una plataforma de microservicios diseñada para:
* Combatir noticias falsas mediante web scraping y contrastación de fuentes.
* Evaluar el impacto de campañas de información/desinformación.
* Gestionar la publicación de contenido verificado.

### ✨ Funcionalidades Planeadas
* **API Principal:** Un gateway en FastAPI (Python) para gestionar todas las peticiones.
* **Frontend:** Una SPA (Single Page Application) en React para visualizar los datos.
* **Servicio de Scraping:** **[PENDIENTE: Aquí se integrará la nueva app de scraping (appscraping.md)]**
* **Análisis de Sentimiento:** Un worker básico con NLTK.
* **Publicación Social:** Conexión con APIs de redes sociales.

---

## 2. ⚙️ Arquitectura de Microservicios

La plataforma está diseñada para ser escalable y resiliente, usando los siguientes componentes:

* **Frontend:** `React` (servido con Nginx)
* **Backend (API):** `FastAPI` (Python)
* **Workers (Scraper, Análisis):** `Python`
* **Base de Datos:** `PostgreSQL`
* **Broker de Mensajes:** `Redis`
* **Contenerización:** `Docker` y `Docker Compose`


---

## 3. 🚀 El Corazón del Proyecto: El Pipeline DevSecOps

Este es el núcleo del trabajo. El pipeline está construido con **GitHub Actions** (`.github/workflows/ci-cd.yml`) e integra la seguridad en cada fase.

### Fase 2: Code (SAST, SCA y Pre-commit)
*Se analiza el código fuente antes y durante la integración.*
* **Gitleaks / TruffleHog:** Detecta secretos y claves API hardcodeadas antes del commit (vía `pre-commit`).
* **Bandit:** Escáner SAST específico para vulnerabilidades en Python.
* **Semgrep:** SAST basado en reglas para encontrar patrones de código inseguros.
* **Trivy (Filesystem):** Escáner SCA que analiza `requirements.txt` y `package.json` en busca de dependencias con CVEs.

### Fase 3: Build (Escaneo de Imágenes)
*Se construye y asegura la imagen Docker.*
* **Docker Build:** Las imágenes de cada microservicio son construidas y etiquetadas.
* **Trivy (Image Scan):** Escanea las imágenes Docker finales en busca de CVEs en las capas del sistema operativo y librerías.
* **GitHub Container Registry (GHCR):** Almacena las imágenes seguras.

### Fase 4: Test (DAST y Quality Gates)
*Se prueba la aplicación en vivo en un entorno temporal.*
* **Pytest:** Ejecución de pruebas unitarias del backend.
* **OWASP ZAP (DAST):** Levanta la aplicación con `docker-compose` y lanza un escaneo dinámico (DAST) contra el frontend para encontrar vulnerabilidades web (ej. cabeceras faltantes, XSS).
* **Quality Gate:** El pipeline **falla automáticamente** si ZAP detecta vulnerabilidades críticas o altas, previniendo el despliegue.

### Fase 5: Release & Deploy (IaC y Despliegue)
*Se define la infraestructura y se despliega la aplicación.*
* **Checkov (IaC Scan):** Escanea los archivos de `Terraform` en busca de configuraciones inseguras en la infraestructura.
* **Publicación (Release):** Si todos los chequeos pasan en la rama `main`, se publican las imágenes con la etiqueta `:latest`.
* **Despliegue (CD):** (Actualmente en pausa) El job `deploy-to-production` se conecta a un VPS vía SSH, inicia sesión en GHCR y actualiza la aplicación con `docker compose pull && docker compose up -d`.

---

## 4. 🛠️ Requisitos Previos (Locales)

* [Git](https://git-scm.com/)
* [Docker & Docker Compose (v2+)](https://www.docker.com/products/docker-desktop/)
* [Node.js v18+](https://nodejs.org/) (Opcional, para desarrollo de frontend)
* [Python 3.11+](https://www.python.org/) (Opcional, para desarrollo de backend)
* **Opcional (Recomendado):** `pip install pre-commit && pre-commit install` para activar los ganchos de Gitleaks.

---

## 5. 💻 Cómo Levantar Localmente (Desarrollo)

1.  **Clonar el repositorio:**
    ```bash
    git clone [https://github.com/MauricioVergaraG/proyecto-centinela.git](https://github.com/MauricioVergaraG/proyecto-centinela.git)
    cd proyecto-centinela
    ```

2.  **(Opcional) Crear archivo de entorno:**
    *Este proyecto usa configuraciones por defecto, pero si fuera necesario, se crearía un `.env`.*

3.  **Levantar todos los servicios:**
    *Este comando construirá todas las imágenes y levantará la pila completa.*
    ```bash
    docker-compose up --build
    ```

4.  **Acceder a los servicios:**
    * **Frontend (React):** `http://localhost:8080`
    * **Backend (API Docs):** `http://localhost:8000/docs`
