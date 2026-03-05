import os
import time
from playwright.sync_api import sync_playwright

EMAIL = os.getenv("SPX_EMAIL")
PASSWORD = os.getenv("SPX_PASSWORD")

LOGIN_URL = "https://spx.shopee.com.br/#/dashboard/toProductivity"

def run():

    print("Iniciando automação...")

    with sync_playwright() as p:

        print("Abrindo navegador...")

        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )

        context = browser.new_context()

        page = context.new_page()

        print("Acessando SPX login...")
        page.goto(LOGIN_URL, timeout=60000)

        page.wait_for_timeout(5000)

        print("URL atual:", page.url)

        print("HTML da página:")
        print(page.content())

        print("Procurando campos de login...")

        inputs = page.query_selector_all("input")

        print("Campos encontrados:", len(inputs))

        for i, inp in enumerate(inputs):
            name = inp.get_attribute("name")
            tipo = inp.get_attribute("type")
            print(f"Input {i} | name: {name} | type: {tipo}")

        print("Preenchendo login...")

        # DIGITAÇÃO REAL (corrige botão desabilitado)
        page.click('input[type="text"]')
        page.type('input[type="text"]', EMAIL, delay=120)

        page.click('input[type="password"]')
        page.type('input[type="password"]', PASSWORD, delay=120)

        page.wait_for_timeout(2000)

        print("Procurando botão Entrar...")

        page.wait_for_selector('button:has-text("Entrar")', timeout=20000)

        print("Clicando em login...")

        page.locator('button:has-text("Entrar")').click()

        print("Login enviado...")

        page.wait_for_timeout(10000)

        print("URL após login:", page.url)

        print("Página carregada!")

        print("Abrindo dashboard produtividade...")

        page.goto("https://spx.shopee.com.br/#/dashboard/toProductivity")

        page.wait_for_timeout(15000)

        print("HTML da página do relatório:")

        html = page.content()

        print(html[:5000])

        print("Automação finalizada!")

        browser.close()


if __name__ == "__main__":
    run()