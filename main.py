import os
import time
from playwright.sync_api import sync_playwright

GOOGLE_EMAIL = os.getenv("GOOGLE_EMAIL")
GOOGLE_PASSWORD = os.getenv("GOOGLE_PASSWORD")

SPX_URL = "https://spx.shopee.com.br/#/dashboard/toProductivity"

def run():

    print("Iniciando automação...")

    with sync_playwright() as p:

        print("Abrindo navegador...")
        browser = p.chromium.launch(headless=True)

        context = browser.new_context()

        page = context.new_page()

        print("Abrindo SPX...")
        page.goto("https://spx.shopee.com.br")

        page.wait_for_load_state("networkidle")

        print("Clicando em Entrar com Google...")

        with page.expect_popup() as popup_info:
            page.click("text=Entrar com o Google")

        google_page = popup_info.value

        google_page.wait_for_load_state()

        print("Página Google aberta")

        print("Digitando email...")

        google_page.fill('input[type="email"]', GOOGLE_EMAIL)

        google_page.click("#identifierNext")

        google_page.wait_for_timeout(3000)

        print("Digitando senha...")

        google_page.fill('input[type="password"]', GOOGLE_PASSWORD)

        google_page.click("#passwordNext")

        print("Aguardando login...")

        page.wait_for_timeout(10000)

        print("Abrindo dashboard produtividade...")

        page.goto(SPX_URL)

        page.wait_for_timeout(10000)

        print("URL atual:", page.url)

        print("Capturando HTML da página")

        html = page.content()

        print(html[:5000])

        browser.close()

if __name__ == "__main__":
    run()