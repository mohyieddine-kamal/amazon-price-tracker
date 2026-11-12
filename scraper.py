from playwright.sync_api import sync_playwright
from db import init_db, insert_price, get_last_price

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
    with sync_playwright() as p:
        conn = init_db()
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        info = get_product_info(page, url)
        last_price = get_last_price(conn, url)
        print("Dernier prix connu:", last_price)

        if last_price is not None and info["price"] < last_price:
            print(f" Baisse de prix ! {last_price}€ → {info['price']}€")

        insert_price(conn, info["title"], url, info["price"])
        print(info)

        browser.close()


if __name__ == "__main__":
    job()