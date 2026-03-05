import os
import time
from playwright.sync_api import sync_playwright

# ==========================
# CONFIG
# ==========================

GOOGLE_EMAIL = os.getenv("GOOGLE_EMAIL")
GOOGLE_PASSWORD = os.getenv("GOOGLE_PASSWORD")

SPX_URL = "https://spx.shopee.com.br/#/dashboard/toProductivity"


# ==========================
# LOGIN GOOGLE
# ==========================

def login_google(page):

    print("Procurando botão Google...")

    page.wait_for_timeout(5000)

    # tenta encontrar botão google
    if page.locator("text=Google").count() > 0:
        print("Clicando em Entrar com Google")
        page.locator("text=Google").first.click()
    else:
        print("Botão Google não encontrado, tentando seletor alternativo")
        page.click("button:has-text('Google')")

    # =====================
    # EMAIL
    # =====================

    print("Aguardando campo de email...")

    page.wait_for_selector('input[type="email"]', timeout=60000)

    print("Digitando email Google")

    page.fill('input[type="email"]', GOOGLE_EMAIL)

    page.keyboard.press("Enter")

    page.wait_for_timeout(4000)

    # =====================
    # PASSWORD
    # =====================

    print("Aguardando campo de senha...")

    page.wait_for_selector('input[name="Passwd"]', timeout=60000)

    print("Digitando senha...")

    page.fill('input[name="Passwd"]', GOOGLE_PASSWORD)

    page.keyboard.press("Enter")

    page.wait_for_timeout(8000)

    print("Login Google finalizado")


# ==========================
# MAIN
# ==========================

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

        # =====================
        # ABRIR SPX
        # =====================

        print("Abrindo SPX...")

        page.goto(SPX_URL, timeout=60000)

        page.wait_for_timeout(5000)

        # =====================
        # LOGIN
        # =====================

        login_google(page)

        # =====================
        # IR PARA DASHBOARD
        # =====================

        print("Acessando dashboard produtividade...")

        page.goto(SPX_URL)

        page.wait_for_timeout(15000)

        # DEBUG
        print("URL atual:", page.url)

        print("HTML da página:")

        print(page.content())

        print("Automação finalizada")

        browser.close()


# ==========================
# START
# ==========================

if __name__ == "__main__":
    run()