import os
import json
import time
import pandas as pd
import gspread

from google.oauth2.service_account import Credentials
from playwright.sync_api import sync_playwright

# ================================
# VARIÁVEIS DE AMBIENTE
# ================================

GOOGLE_CREDS = os.getenv("GOOGLE_CREDS")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SHEET_NAME = os.getenv("SHEET_NAME")

GOOGLE_EMAIL = os.getenv("GOOGLE_EMAIL")
GOOGLE_PASSWORD = os.getenv("GOOGLE_PASSWORD")

# ================================
# GOOGLE SHEETS
# ================================

def conectar_sheets():

    creds_dict = json.loads(GOOGLE_CREDS)

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)

    client = gspread.authorize(creds)

    sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

    return sheet


# ================================
# ENVIAR DATAFRAME PARA SHEETS
# ================================

def enviar_para_sheets(df):

    sheet = conectar_sheets()

    sheet.clear()

    data = [df.columns.values.tolist()] + df.values.tolist()

    sheet.update(data)

    print("Dados enviados para Google Sheets")


# ================================
# SCRAPING SPX
# ================================

def extrair_dados(page):

    print("Abrindo dashboard produtividade...")

    page.goto("https://spx.shopee.com.br/#/dashboard/toProductivity")

    page.wait_for_timeout(15000)

    print("Capturando HTML da página...")

    html = page.content()

    print(html[:2000])

    # Exemplo de dataset fake (até capturarmos a API real)
    data = {
        "status": ["logado"],
        "timestamp": [time.strftime("%Y-%m-%d %H:%M:%S")]
    }

    df = pd.DataFrame(data)

    return df


# ================================
# LOGIN GOOGLE
# ================================

def login_google(page):

    print("Abrindo SPX...")

    page.goto("https://spx.shopee.com.br")

    page.wait_for_timeout(8000)

    print("Procurando botão Google...")

    page.wait_for_selector("text=Entrar com o Google", timeout=60000)

    print("Clicando em Entrar com Google")

    page.click("text=Entrar com o Google")

    page.wait_for_timeout(5000)

    print("Digitando email Google")

    page.wait_for_selector('input[type="email"]', timeout=60000)

    page.fill('input[type="email"]', GOOGLE_EMAIL)

    page.click("#identifierNext")

    page.wait_for_timeout(5000)

    print("Digitando senha Google")

    page.wait_for_selector('input[type="password"]', timeout=60000)

    page.fill('input[type="password"]', GOOGLE_PASSWORD)

    page.click("#passwordNext")

    print("Aguardando login completar...")

    page.wait_for_timeout(15000)

    print("Login finalizado")



# ================================
# MAIN
# ================================

def run():

    print("Iniciando automação...")

    with sync_playwright() as p:

        print("Abrindo navegador...")

        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ]
        )

        context = browser.new_context()

        page = context.new_page()

        login_google(page)

        df = extrair_dados(page)

        enviar_para_sheets(df)

        browser.close()

        print("Processo finalizado")


# ================================

if __name__ == "__main__":
    run()