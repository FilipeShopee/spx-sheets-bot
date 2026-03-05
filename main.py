import os
import json
import time
import pandas as pd
import gspread

from google.oauth2.service_account import Credentials
from playwright.sync_api import sync_playwright

SPX_EMAIL = os.getenv("SPX_EMAIL")
SPX_PASSWORD = os.getenv("SPX_PASSWORD")

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SHEET_NAME = os.getenv("SHEET_NAME")

GOOGLE_CREDS = os.getenv("GOOGLE_CREDS")


# ===============================
# AUTENTICAÇÃO GOOGLE SHEETS
# ===============================
def conectar_sheets():

    creds_dict = json.loads(GOOGLE_CREDS)

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    credentials = Credentials.from_service_account_info(
        creds_dict,
        scopes=scopes
    )

    client = gspread.authorize(credentials)

    return client


# ===============================
# DOWNLOAD CSV DO SPX
# ===============================
def baixar_csv():

    print("Iniciando automação...")

    with sync_playwright() as p:

        print("Abrindo navegador...")
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"]
        )

        context = browser.new_context()

        page = context.new_page()

        print("Acessando SPX login...")

        page.goto(
            "https://spx.shopee.com.br/",
            timeout=60000
        )

        page.wait_for_timeout(5000)

        print("URL atual:", page.url)

        print("Procurando campos de login...")

        inputs = page.query_selector_all("input")

        print("Campos encontrados:", len(inputs))

        for i, inp in enumerate(inputs):

            print(
                f"Input {i} | name:",
                inp.get_attribute("name"),
                "| type:",
                inp.get_attribute("type")
            )

        print("Preenchendo login...")

        page.fill('input[type="text"]', SPX_EMAIL)
        page.fill('input[type="password"]', SPX_PASSWORD)

        print("Clicando em login...")

        page.click('button[type="submit"]')

        page.wait_for_load_state("networkidle")

        page.wait_for_timeout(8000)

        print("Login realizado, indo para relatório...")

        # ⚠️ COLOQUE AQUI A URL DO RELATÓRIO
        page.goto(
            "COLE_AQUI_URL_DO_RELATORIO",
            timeout=60000
        )

        page.wait_for_timeout(8000)

        print("Iniciando download...")

        with page.expect_download() as download_info:

            page.click("text=Export")

        download = download_info.value

        path = "/tmp/relatorio.csv"

        download.save_as(path)

        print("Download concluído:", path)

        browser.close()

        return path


# ===============================
# ENVIAR PARA GOOGLE SHEETS
# ===============================
def enviar_para_sheets(csv_path):

    print("Enviando para Google Sheets...")

    df = pd.read_csv(csv_path)

    client = conectar_sheets()

    sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

    sheet.clear()

    sheet.update(
        [df.columns.values.tolist()] +
        df.values.tolist()
    )

    print("Dados enviados com sucesso!")


# ===============================
# EXECUÇÃO PRINCIPAL
# ===============================
if __name__ == "__main__":

    try:

        arquivo = baixar_csv()

        if arquivo:
            enviar_para_sheets(arquivo)
        else:
            print("Nenhum CSV gerado")

    except Exception as e:

        print("Erro durante execução:")
        print(e)