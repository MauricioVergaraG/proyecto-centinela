**Proyecto Centinela 🛡️**

**Autor:** Mauricio Vergara

Este repositorio es la implementación de un **pipeline DevSecOps de ciclo completo** para una plataforma contenerizada de análisis de desinformación (OSINT), como parte de un trabajo práctico universitario.

El objetivo principal **no es** la aplicación en sí, sino la **construcción, automatización y aseguramiento de todo el ciclo de vida de la aplicación (CI/CD/CS)**, integrando la seguridad en cada fase (Shift-Left Security) con herramientas FOSS.

**1\. ⚙️ Arquitectura de la Aplicación**

La aplicación es una plataforma de microservicios asíncrona, diseñada para ser escalable y resiliente.

- **Frontend (React):** Interfaz de usuario (localhost:3000).
- **Backend (FastAPI):** API que gestiona las peticiones (localhost:8000).
- **Worker (Python):** Un servicio scraper que consume de una cola y ejecuta el trabajo pesado (llamar a APIs externas y guardar en la BD).
- **Cola de Mensajes (Redis):** Gestiona la comunicación asíncrona entre la API y el Worker.
- **Base de Datos (PostgreSQL):** Almacena los resultados del scraping.
- **Contenerización:** Toda la aplicación se ejecuta con Docker y se orquesta localmente con Docker Compose.

**2\. 🚀 El Pipeline DevSecOps (El Resultado del Proyecto)**

Este es el núcleo del trabajo, implementado en .github/workflows/ci-cd.yml. El pipeline automatiza e integra la seguridad en cada fase del ciclo de vida del software.

**Fase 1: Plan**

- **Modelado de Amenazas:** Realizado con **OWASP Threat Dragon** para identificar amenazas (STRIDE) en el flujo de datos.

**Fase 2: Code (Seguridad Estática)**

_Se analiza el código fuente en cada "push" y "pull request"._

- **Pre-commit Hooks:** Se usa pre-commit para ejecutar "guardias locales":
  - gitleaks: Detecta secretos y claves API _antes_ de que lleguen al repositorio.
  - black: Asegura un formato de código Python consistente.
  - fix-end-of-files / trailing-whitespace: Mantienen la limpieza del código.
- **SAST (Análisis Estático):**
  - flake8: Analiza el código Python en busca de errores lógicos y de estilo.
  - bandit: Escáner SAST que busca patrones de vulnerabilidades comunes en Python.
  - semgrep: Escáner SAST basado en reglas para patrones de código complejos.
- **SCA (Análisis de Dependencias):**
  - trivy fs: Escanea requirements.txt y otros archivos de dependencias en busca de librerías con CVEs (Vulnerabilidades) conocidas.
- **IaC Scan (Escaneo de Infraestructura):**
  - checkov: Escanea archivos de Terraform (/terraform) en busca de malas configuraciones de seguridad en la infraestructura.

**Fase 3: Build (Seguridad de Imágenes)**

_Se construyen y aseguran los artefactos de Docker._

- **Docker Build:** Se construyen las imágenes de los 3 microservicios (api, frontend, scraper).
- **Escaneo de Imágenes:**
  - trivy image: Escanea las imágenes Docker finales. El pipeline **falla (🔴)** si se encuentra una vulnerabilidad de severidad HIGH o CRITICAL, previniendo el uso de imágenes inseguras.
- **Registro:** Las imágenes seguras se publican en **GitHub Container Registry (GHCR)**.

**Fase 4: Test (Seguridad Dinámica)**

_Se prueba la aplicación completa en un entorno en vivo (temporal)._

- **Unit & Smoke Tests:** Se ejecutan pytest (para la API) y un "smoke test" (para el frontend) para asegurar que la lógica de la app funciona.
- **DAST (Análisis Dinámico):**
  - Se levanta la pila completa (docker-compose up) dentro del pipeline.
  - **OWASP ZAP (Zed Attack Proxy)** se lanza contra el frontend (<http://frontend:80>) para "hackear" la aplicación y encontrar vulnerabilidades en tiempo de ejecución (ej. cabeceras de seguridad faltantes, XSS, etc.).
- **Quality Gates:** El pipeline tiene "porteros de calidad" que detienen el proceso si:
  - pytest falla.
  - Trivy (SCA o Imagen) encuentra un CVE crítico.
  - DAST (ZAP) encuentra una vulnerabilidad crítica.

**Fase 5 & 6: Deploy & Monitor (Despliegue y Monitoreo)**

- **Despliegue (CD):** (Pendiente) El job deploy-to-production (que solo se ejecuta en main) está configurado para conectarse a un VPS vía SSH y actualizar la aplicación usando docker compose pull.
- **Monitoreo (Plan):** La Fase 6 (Opcional) implicaría instalar Falco (para seguridad en runtime) y el stack PLG (Promtail, Loki, Grafana) para la observabilidad de logs.

**3\. 💻 Cómo Levantar Localmente (Desarrollo)**

- **Requisitos:**
  - Git
  - Docker & Docker Compose (v2+)
- **Clonar el repositorio:**
- git clone \[<https://github.com/MauricioVergaraG/proyecto-centinela.git\>](<https://github.com/MauricioVergaraG/proyecto-centinela.git>)
- cd proyecto-centinela
- **Levantar todos los servicios:** _Este comando construirá todas las imágenes y levantará la pila completa._
- docker-compose up --build
- **Acceder a los servicios:**
  - **Frontend (App):** <http://localhost:3000>
  - **Backend (API Docs):** <http://localhost:8000/docs>
