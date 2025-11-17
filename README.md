# 🟢 Proyecto Centinela 🛡️

**Autor:** Mauricio Vergara  
Pipeline DevSecOps de ciclo completo para una plataforma contenerizada de análisis de desinformación (OSINT).  
El enfoque principal es la automatización y aseguramiento de todo el ciclo de vida de la aplicación (CI/CD/CS) integrando seguridad en cada fase (Shift-Left Security) con herramientas FOSS.

---

## 1. ⚙️ Arquitectura de la Aplicación

Plataforma de microservicios asíncrona, escalable y resiliente.

| Componente | Tecnología | Función | URL / Puerto |
|------------|------------|--------|--------------|
| Frontend | React | Interfaz de usuario | http://localhost:3000 |
| Backend | FastAPI | API que gestiona peticiones | http://localhost:8000 |
| Worker | Python | Scraper que procesa trabajos en cola | - |
| Cola de Mensajes | Redis | Comunicación asíncrona entre API y Worker | - |
| Base de Datos | PostgreSQL | Almacena resultados del scraping | - |
| Contenerización | Docker / Docker Compose | Orquestación local de todos los servicios | - |

---

## 2. 🚀 Pipeline DevSecOps

**Archivo principal:** `.github/workflows/ci-cd.yml`  
Integra seguridad en cada fase del ciclo de vida del software.

### 🔹 Fase 1: Plan
- Modelado de amenazas: OWASP Threat Dragon, STRIDE

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
- Construcción: Docker de los 3 microservicios
- Escaneo: `trivy image` detecta HIGH/CRITICAL y bloquea el pipeline
- Registro Temporal: GHCR (GitHub Container Registry) con la `run_id`

### 🔹 Fase 4: Test (Seguridad Dinámica)
- Unit & Smoke Tests: `pytest` para API y frontend
- DAST: OWASP ZAP analiza frontend (`http://frontend:80`)
- Quality Gates: Falla el pipeline si:
  - `pytest` falla
  - `trivy` detecta CVEs críticos
  - ZAP detecta vulnerabilidades críticas

### 🔹 Fase 5 & 6: Release, Deploy & Monitor
- Publicación: Las imágenes validadas se publican en:
  - GitHub Container Registry (GHCR) con tag `:latest`
  - Docker Hub con tag `:latest`
- Deploy (Simulado): Job `deploy-to-production` simula la conexión SSH a un VPS y la actualización con `docker compose pull` y `docker compose up -d`.
- Monitoreo: Opcional, Falco (seguridad runtime) + stack PLG (Promtail, Loki, Grafana) para logs.

---

## 3. 💻 Cómo Levantar Localmente (Desarrollo)

Este método es para desarrolladores que quieren modificar el código fuente. Utiliza:

```
docker-compose up --build
```

**Requisitos:**
- Git
- Docker & Docker Compose v2+

**Clonar repositorio:**

```
git clone https://github.com/MauricioVergaraG/proyecto-centinela.git
cd proyecto-centinela
```

**Configurar variables de entorno:**  
Crear archivo `.env` en la raíz del proyecto y añadir tu clave de NewsAPI:

```
# .env
NEWS_API_KEY=tu-clave-secreta-de-newsapi

# Variables para la Base de Datos (puedes dejarlas así)
POSTGRES_USER=centinela
POSTGRES_PASSWORD=supersecretpassword
POSTGRES_DB=centineladb
```

**Levantar todos los servicios:**

```
docker-compose up --build
```

**Acceder a los servicios:**
- Frontend (App): http://localhost:3000
- Backend (API Docs): http://localhost:8000/docs

---

## 4. 📦 Cómo Consumir las Imágenes (Usuario/Producción)

Este método es para usuarios o para un servidor de producción. No construye nada localmente, sino que descarga y consume las imágenes públicas que el pipeline ya verificó y publicó en Docker Hub.

**Requisitos:**
- Docker & Docker Compose v2+

**Pasos:**

1. Crear un directorio de trabajo:

```
mkdir centinela-prod
cd centinela-prod
```

2. Configurar variables de entorno:  
Crear un archivo `.env` dentro de `centinela-prod` (el mismo que en desarrollo).

```
# .env
NEWS_API_KEY=tu-clave-secreta-de-newsapi
POSTGRES_USER=centinela
POSTGRES_PASSWORD=supersecretpassword
POSTGRES_DB=centineladb
```

3. Crear archivo `docker-compose.prod.yml`:

```
version: '3.8'

services:
  frontend:
    image: mauriciovergara/centinela-frontend:latest
    ports:
      - "3000:80"
    depends_on:
      - api

  api:
    image: mauriciovergara/centinela-api:latest
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      - db
      - redis

  scraper:
    image: mauriciovergara/centinela-scraper:latest
    env_file: .env
    depends_on:
      - db
      - redis

  redis:
    image: redis:7-alpine

  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    env_file: .env

volumes:
  postgres_data:
```

4. Levantar la aplicación:

```
# 1. Descargar todas las imágenes de Docker Hub
docker-compose -f docker-compose.prod.yml pull

# 2. Iniciar todos los contenedores en segundo plano
docker-compose -f docker-compose.prod.yml up -d
```

**Acceder a los servicios:**
- Frontend (App): http://localhost:3000
- Backend (API Docs): http://localhost:8000/docs

