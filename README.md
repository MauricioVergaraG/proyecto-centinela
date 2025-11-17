# Proyecto Centinela 🛡️

**Autor:** Mauricio Vergara

> Pipeline DevSecOps de ciclo completo para una plataforma contenerizada de análisis de desinformación (OSINT).  
> El enfoque principal es la automatización y aseguramiento de todo el ciclo de vida de la aplicación (CI/CD/CS) integrando seguridad en cada fase (Shift-Left Security) con herramientas FOSS.

---

## 1. ⚙️ Arquitectura de la Aplicación

Plataforma de microservicios asíncrona, escalable y resiliente.

| Componente | Tecnología | Función | URL / Puerto |
|------------|------------|---------|--------------|
| Frontend | React | Interfaz de usuario | [http://localhost:3000](http://localhost:3000) |
| Backend | FastAPI | API que gestiona peticiones | [http://localhost:8000](http://localhost:8000) |
| Worker | Python | Scraper que procesa trabajos en cola | - |
| Cola de Mensajes | Redis | Comunicación asíncrona entre API y Worker | - |
| Base de Datos | PostgreSQL | Almacena resultados del scraping | - |
| Contenerización | Docker / Docker Compose | Orquestación local de todos los servicios | - |

---

## 2. 🚀 Pipeline DevSecOps

Archivo principal: `.github/workflows/ci-cd.yml`  
Integra seguridad en cada fase del ciclo de vida del software.

### 🔹 Fase 1: Plan
- **Modelado de amenazas:** OWASP Threat Dragon, STRIDE

### 🔹 Fase 2: Code (Seguridad Estática)
- **Pre-commit Hooks:**
    - `gitleaks` → Detecta secretos y claves API
    - `black` → Formato Python consistente
    - `fix-end-of-files / trailing-whitespace` → Limpieza de código
- **SAST (Análisis Estático):**
    - `flake8` → Errores y estilo
    - `bandit` → Vulnerabilidades comunes en Python
    - `semgrep` → Patrones de código complejos
- **SCA (Dependencias):** `trivy fs` → Detecta CVEs
- **IaC Scan:** `checkov` → Escaneo de Terraform

### 🔹 Fase 3: Build (Seguridad de Imágenes)
- **Construcción:** Docker de los 3 microservicios
- **Escaneo:** `trivy image` detecta HIGH/CRITICAL y bloquea el pipeline
- **Registro:** GHCR (GitHub Container Registry)

### 🔹 Fase 4: Test (Seguridad Dinámica)
- **Unit & Smoke Tests:** `pytest` para API y frontend
- **DAST:** OWASP ZAP analiza frontend (`http://frontend:80`)
- **Quality Gates:** Falla el pipeline si:
    - `pytest` falla
    - `trivy` detecta CVEs críticos
    - ZAP detecta vulnerabilidades críticas

### 🔹 Fase 5 & 6: Deploy & Monitor
- **Deploy:** Job `deploy-to-production` en main, actualiza VPS vía SSH con `docker compose pull`
- **Monitoreo:** Opcional, Falco (seguridad runtime) + stack PLG (Promtail, Loki, Grafana) para logs

---

## 3. 💻 Cómo Levantar Localmente (Desarrollo)

**Requisitos:**
- Git  
- Docker & Docker Compose v2+

**Clonar repositorio:**

    git clone https://github.com/MauricioVergaraG/proyecto-centinela.git
    cd proyecto-centinela

**Configurar variables de entorno:**  
Crear archivo `.env` en la raíz del proyecto y añadir tu clave de NewsAPI:

    NEWS_API_KEY=tu-clave-secreta-de-newsapi

**Levantar todos los servicios:**

    docker-compose up --build

**Acceder a los servicios:**
- Frontend (App): [http://localhost:3000](http://localhost:3000)  
- Backend (API Docs): [http://localhost:8000/docs](http://localhost:8000/docs)
