import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from base_scraper import init_selenium_driver, parse_article
from utils.file_manager import save_articles
from utils.csv_manager import save_articles_csv



def scrape_chequeado_selenium(limit=50, max_wait=60, sleep_time=2):
    """
    Scraper de Chequeado usando Selenium, clickeando el boton 'Next'.
    """
    BASE_URL = "https://chequeado.com/chequeos/?current-page=1#listing"
    driver = init_selenium_driver(headless=False)
    driver.get(BASE_URL)
    time.sleep(sleep_time)

    articles = []
    # seen_urls = set()
    start_time = time.time()

    while len(articles) < limit and (time.time() - start_time) < max_wait:
        soup = BeautifulSoup(driver.page_source, "html.parser")
        cards = soup.select("article.c-card")

        for card in cards:
            # Ignorar noticias verdaderas
            if card.select_one("span.c-tax__item--verdadero"):
                print("[INFO] Noticia marcada como VERDADERA, saltando.")
                continue

            # a_tag = card.select_one("a")
            # if not a_tag:
            #     print("[WARN] Tarjeta sin enlace, saltando.")
            #     continue
            # link = a_tag.get("href")
            # print(f"[DEBUG] Procesando enlace: {link}")
            # if not link.startswith("http"):
            #     print("[WARN] Enlace relativo o inválido, saltando.")
            #     link = "https://chequeado.com" + link
            # if link in seen_urls:
            #     print("[INFO] Enlace ya visto, saltando.")
            #     continue
            # seen_urls.add(link)

            # titulo y descripcion
            title, description = parse_article(card, "h3.c-card__titulo", "div.c-card__descripcion")
            articles.append({
                "title": title,
                "description": description,
                "url": None
            })

            if len(articles) >= limit:
                break

        # intentar clickear el boton "Next"
        try:
            next_btn = driver.find_element(By.CSS_SELECTOR, "a.c-pagination__button--next")
            driver.execute_script("arguments[0].scrollIntoView(true);", next_btn)
            time.sleep(1)
            next_btn.click()
            time.sleep(sleep_time)
        except NoSuchElementException:
            print("[INFO] No hay más paginas para navegar.")
            break

    driver.quit()
    return articles


if __name__ == "__main__":
    noticias = scrape_chequeado_selenium(limit=50)
    save_articles(noticias, label="falso", portal="chequeado")
    save_articles_csv(noticias, label="falso", portal="chequeado")
    print(f"\nSe extrajeron {len(noticias)} noticias de Chequeado.")
    # for i, n in enumerate(noticias, 1):
    #     print(f"\n{i}. {n['title']} {n['description']}\n")
