from playwright.sync_api import sync_playwright

def get_product_info(page, url):
    page.goto(url)
    
    title = page.locator("span#productTitle").inner_text().strip()
    
    offscreen_prices = page.locator(".apex-core-price-identifier .a-offscreen").all_inner_texts()
    price = next((p for p in offscreen_prices if p.strip()), None)
    price_value = float(price.replace("€", "").strip())

    return {"title": title, "price": price_value}

url = "https://www.amazon.fr/dp/B0DCVMN51Z"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    info = get_product_info(page, url)
    print(info)

    browser.close()