from base_scraper import get_html_requests
from utils.file_manager import save_articles
from utils.csv_manager import save_articles_csv

def scrape_bbc(limit=50):
    """
    Scraper para BBC Mundo (noticias verdaderas).
    Extrae titulo, descripcion y link desde la portada.
    Retorna lista de dicts con los resultados.
    """
    BASE_URL = "https://www.bbc.com/mundo"

    soup = get_html_requests(BASE_URL)
    if not soup:
        return []

    # cada noticia esta dentro de un div con class="promo-text"
    articles = []
    for div in soup.select("div.promo-text"):
        title_tag = div.select_one("h3 a")
        desc_tag = div.select_one("p")

        if not title_tag or not desc_tag:
            continue  # solo nos quedamos con las que tienen titulo y descripcion

        title = title_tag.get_text(strip=True)
        url = title_tag.get("href")
        if url and not url.startswith("http"):
            url = "https://www.bbc.com" + url  # links relativos
        desc = desc_tag.get_text(strip=True)

        articles.append({
            "title": title,
            "description": desc,
            "url": url
        })

        if limit and len(articles) >= limit:
            break

    return articles


if __name__ == "__main__":
    noticias = scrape_bbc(limit=50)
    save_articles(noticias, label="verdad", portal="bbc")
    save_articles_csv(noticias, label="verdad", portal="bbc") 
    print(f"Se extrajeron {len(noticias)} noticias de BBC Mundo.")
    # for i, n in enumerate(noticias[:5], 1):
    #     print(f"{i}. {n['title']} -> {n['url']}")
    #     print(f"   {n['description']}\n")
