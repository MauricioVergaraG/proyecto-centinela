# Proyecto Centinela
[![CI/CD](https://github.com/MauricioVergaraG/proyecto-centinela/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/MauricioVergaraG/proyecto-centinela/actions/workflows/ci-cd.yml)
**Autor:** Mauricio Vergara
**Fecha inicio:** 2025-11-15
**Descripción corta:** MVP contenerizado para análisis de desinformación (Centinela). Contiene: API (FastAPI), Worker de scraping (stub), Frontend (React stub), Postgres y Redis para integración local con `docker-compose`.

## Requisitos
- Docker & Docker Compose (v2+)
- Node (para desarrollo frontend, opcional si usás solo container)
- GitHub account (para CI/CD y GHCR)

## Levantar local (rápido)
1. Desde la raíz del repo:
```bash
docker-compose up --build
