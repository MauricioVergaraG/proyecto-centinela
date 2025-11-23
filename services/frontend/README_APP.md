# 🛡️ CENTINELA - Sistema de Análisis Forense Digital

> **App del Grupo 3 para DevSecOps** | Especialización en Ciberseguridad | UNIMINUTO

![Centinela Dashboard](https://img.shields.io/badge/Estado-Activo-success) ![Docker](https://img.shields.io/badge/Docker-Containerized-blue) ![Stack](https://img.shields.io/badge/Microservicios-FullStack-orange)

**Centinela** es una plataforma de auditoría y análisis forense diseñada para detectar patrones de desinformación (Fake News) en sitios web. Utilizando una arquitectura de microservicios, el sistema realiza *web scraping* en tiempo real, analiza heurísticas de contenido y genera reportes de evidencia digital.

---

## 🚀 Características Principales

* **🔍 Análisis Forense de URLs:** Examina sitios web en busca de patrones sospechosos (títulos alarmistas, exceso de mayúsculas, lenguaje polarizante).
* **📊 Dashboard en Tiempo Real:** Visualización estadística de amenazas detectadas vs. sitios seguros.
* **📄 Generación de Evidencia:** Exportación de reportes forenses en formato **PDF** con hash del análisis y metadatos.
* **🚥 Sistema de Scoring:** Algoritmo de puntuación de riesgo (0-100%) con clasificación visual (Confiable, Dudoso, Alto Riesgo).
* **💾 Persistencia de Datos:** Historial global de análisis almacenado en base de datos relacional.
* **⚡ Modo Simulacro:** Herramienta integrada para demos y pruebas de estrés con inyección de amenazas simuladas.

---

## 🏗️ Arquitectura del Sistema

El proyecto implementa una arquitectura de **Microservicios Desacoplados** orquestados con Docker Compose:

1.  **Frontend (React + Tailwind):** Interfaz de usuario para gestión de casos y visualización.
2.  **Backend (FastAPI):** API Gateway que gestiona solicitudes y validaciones.
3.  **Broker (Redis):** Cola de mensajería para manejo asíncrono de tareas de scraping.
4.  **Worker (Python Scraper):** Motor de análisis que navega, extrae y evalúa el contenido.
5.  **Database (PostgreSQL):** Persistencia de resultados históricos y evidencia.

---

## ⚙️ ¿Cómo funciona paso a paso?

El flujo de un análisis forense dentro de Centinela sigue estos pasos rigurosos:

1.  **Ingesta:** El analista ingresa una URL sospechosa en el Dashboard.
2.  **Encolado:** La API recibe la URL y crea un "Trabajo de Análisis" (Job) en la cola `scrape_queue` de Redis.
3.  **Procesamiento (Scraping):**
    * El **Worker** detecta el nuevo trabajo.
    * Realiza una petición HTTP segura al sitio objetivo.
    * Extrae el DOM (HTML) y limpia el contenido para obtener solo texto legible.
4.  **Análisis Heurístico:** El algoritmo interno evalúa:
    * *Palabras Clave de Pánico:* "URGENTE", "VIRAL", "MUERTE", etc.
    * *Formato:* Uso excesivo de mayúsculas (Gritar digitalmente).
    * *Longitud:* Textos demasiado cortos sin sustento.
5.  **Veredicto y Persistencia:** Se calcula un **Score (0-100)** y se guarda el resultado junto con la evidencia (texto extraído) en PostgreSQL.
6.  **Reporte:** El Frontend consulta la base de datos y actualiza la interfaz, mostrando la tarjeta de riesgo y permitiendo descargar el PDF.

---

## 🛠️ Instalación y Despliegue

Este proyecto está 100% dockerizado para facilitar su despliegue en cualquier entorno.

### Prerrequisitos
* Docker y Docker Compose instalados.

### Pasos para ejecutar

1.  **Construir y levantar los servicios:**
    ```bash
    docker-compose up -d --build
    ```

2.  **Acceder a la Aplicación:**
    * Abra su navegador en: `http://localhost:3000`

### Comandos Útiles

* **Ver logs del sistema:** `docker-compose logs -f`
* **Detener el sistema:** `docker-compose down`
* **Limpieza total (Borrar BD):** `docker-compose down -v`

---

## 🧪 Pruebas y Simulación

Para validar el funcionamiento del sistema de alertas sin depender de noticias externas cambiantes, Centinela incluye modos de prueba rápida:

* **Botón "🚨 Cargar Simulacro":** Envía una URL interna de prueba que fuerza al sistema a detectar un positivo de Fake News (Score 95%), mostrando las alertas rojas y el desglose de evidencias.
* **Botón "✅ Cargar BBC":** Envía una URL confiable para validar el caso negativo (Score bajo).

---

## 👥 Créditos - Grupo 3

Proyecto desarrollado como parte de la **Especialización en Ciberseguridad (DevSecOps)** de la Corporación Universitaria Minuto de Dios (UNIMINUTO).

* **Desarrollo y Arquitectura:** Mauricio Vergara
* **Stack:** Python, React, Docker, Postgres.

---
*Centinela v3.0 - 2025*