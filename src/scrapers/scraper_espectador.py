from bs4 import BeautifulSoup
from base_scraper import init_selenium_driver, incremental_scroll, get_html_requests
from utils.file_manager import save_articles
from utils.csv_manager import save_articles_csv
import time


def scrape_espectador(limit=30, max_wait=60):
    """
    Scraper para El Espectador.
    Hace scroll hasta recolectar `limit` noticias o agotar `max_wait`.
    Luego visita cada link para obtener la descripción real.
    """
    BASE_URL = "https://www.elespectador.com/"
    driver = init_selenium_driver(headless=True)
    driver.get(BASE_URL)
    time.sleep(3)

    start_time = time.time()
    articles = []
    seen_urls = set()
    retries_without_new = 0

    # titulos y links de la pagina principal
    while len(articles) < limit and (time.time() - start_time) < max_wait:
        incremental_scroll(driver, wait=2, step=800)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        new_count = 0

        for card in soup.select("div.Card-Container"):
            # # Asegurarnos que tenga fecha
            # if not card.select_one("div.Card-DateContainer p.Card-Datetime"):
            #     continue

            title_tag = card.select_one("h2.Card-Title a")
            if not title_tag:
                continue

            title = title_tag.get_text(strip=True)
            url = title_tag.get("href")
            if url and not url.startswith("http"):
                url = BASE_URL.rstrip("/") + url

            if url not in seen_urls:
                seen_urls.add(url)
                articles.append({
                    "title": title,
                    "url": url,
                    "description": None  # luego visitamos el link
                })
                new_count += 1

            if len(articles) >= limit:
                break

        # paramos el scroll si no hay nuevas noticias encontradas
        if new_count == 0:
            retries_without_new += 1
        else:
            retries_without_new = 0

        if retries_without_new >= 3:
            break

    driver.quit()

    # visitar cada link
    for article in articles:
        url = article["url"]
        soup = get_html_requests(url, sleep_time=2)
        if not soup:
            continue

        desc_tag = soup.select_one("h2.ArticleHeader-Hook div")
        if desc_tag:
            article["description"] = desc_tag.get_text(strip=True)
        else:
            article["description"] = ""
        
        time.sleep(2)

    return articles


if __name__ == "__main__":
    noticias = scrape_espectador(limit=50, max_wait=60)
    save_articles(noticias, label="verdad", portal="espectador")
    save_articles_csv(noticias, label="verdad", portal="espectador") 
    print(f"\nSe extrajeron {len(noticias)} noticias de El Espectador.")
    # for i, n in enumerate(noticias, 1):
    #     print(f"\n{i}. {n['title']}\n   {n['description']}\n   {n['url']}")
