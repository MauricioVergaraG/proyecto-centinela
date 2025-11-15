# Autor: Mauricio Vergara
# Worker stub: simula scraping básico
import time
import requests
from bs4 import BeautifulSoup


def simple_scrape(url):
    try:
        r = requests.get(url, timeout=6)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.title.string if soup.title else ""
        return {"url": url, "title": title}
    except Exception as e:
        return {"url": url, "error": str(e)}


if __name__ == "__main__":
    # demo loop: solo para probar el contenedor
    test_urls = ["https://example.com", "https://news.ycombinator.com"]
    for u in test_urls:
        print("Scraping:", u)
        res = simple_scrape(u)
        print(res)
        time.sleep(2)
    print("Worker demo complete.")
