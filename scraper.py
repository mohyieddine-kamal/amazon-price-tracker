from playwright.sync_api import sync_playwright
from db import init_db, insert_price, get_last_price
from alert import send_telegram_alert

url = "https://www.amazon.fr/dp/B0DCVMN51Z"


def get_product_info(page, url):
    page.goto(url)

    title = page.locator("span#productTitle").inner_text().strip()

    offscreen_prices = page.locator(".apex-core-price-identifier .a-offscreen").all_inner_texts()
    price = next((p for p in offscreen_prices if p.strip()), None)
    cleaned_price = price.replace("€", "").strip().replace(",", ".")
    price_value = float(cleaned_price)

    return {"title": title, "price": price_value}


def job():
    try:
        with sync_playwright() as p:
            conn = init_db()
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            try:
                # Tentative de scraping du titre et du prix
                info = get_product_info(page, url)
            except Exception as e:
                # Le scraping a echoue (page changee, produit indisponible, etc.)
                print(f"Erreur pendant le scraping: {e}")
                send_telegram_alert(f"Le scraper a echoue: {e}")
                return
            finally:
                # Le navigateur doit se fermer meme en cas d'erreur
                browser.close()

            # Recupere le dernier prix connu pour ce produit
            last_price = get_last_price(conn, url)
            print("Dernier prix connu:", last_price)

            # Compare avec le nouveau prix scrape
            if last_price is not None and info["price"] < last_price:
                message = f"Baisse de prix !\n{info['title']}\n{last_price}e -> {info['price']}e\n{url}"
                print(message)
                try:
                    # Envoi de l'alerte Telegram
                    send_telegram_alert(message)
                except Exception as e:
                    # Un probleme Telegram ne doit pas bloquer l'enregistrement du prix
                    print(f"Erreur lors de l'envoi Telegram: {e}")

            # Enregistre le nouveau prix dans l'historique
            insert_price(conn, info["title"], url, info["price"])
            print(info)

    except Exception as e:
        # Filet de securite final pour toute erreur imprevue
        print(f"Erreur critique dans job(): {e}")

if __name__ == "__main__":
    job()