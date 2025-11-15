# Autor: Mauricio Vergara
# Minimal FastAPI app para Proyecto Centinela (MVP)
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Centinela API", version="0.1.0")


class Health(BaseModel):
    status: str


@app.get("/health", response_model=Health)
async def health():
    return {"status": "ok"}


@app.get("/version")
async def version():
    return {"version": "0.1.0", "author": "Mauricio Vergara"}


# Endpoint demo para encolar URL de scraping (stub)
class ScrapeRequest(BaseModel):
    url: str


@app.post("/scrape")
async def enqueue_scrape(req: ScrapeRequest):
    # En este MVP simplemente devolvemos ack.
    # En la siguiente iteración se publicará en Redis/Rabbit.
    return {"status": "queued", "url": req.url}
