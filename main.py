from playwright.sync_api import sync_playwright
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import time
import os
import json


SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SHEET_NAME = os.getenv("SHEET_NAME")
SPX_EMAIL = os.getenv("SPX_EMAIL")
SPX_PASSWORD = os.getenv("SPX_PASSWORD")
GOOGLE_CREDS = os.getenv("GOOGLE_CREDS")


def baixar_csv():
    with sync_playwright() as p:
        print("Abrindo navegador stealth...")

        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled"
            ]
        )

        context = browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            locale="pt-BR",
            timezone_id="America/Sao_Paulo"
        )

        page = context.new_page()

        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        print("Acessando SPX...")
        page.goto("https://spx.shopee.com.br ", wait_until="networkidle")

        print("URL após carregamento:", page.url)

        # Espera a página montar
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(5000)

        # DEBUG INPUTS
        print("Verificando inputs disponíveis...")
        inputs = page.locator("input")
        total_inputs = inputs.count()
        print("Campos encontrados:", total_inputs)

        for i in range(total_inputs):
            print(
                "Input", i,
                "| name:", inputs.nth(i).get_attribute("name"),
                "| type:", inputs.nth(i).get_attribute("type"),
                "| id:", inputs.nth(i).get_attribute("id")
            )

        browser.close()
        return None


def enviar_para_sheets(csv_path):
    print("Enviando para Sheets...")

    df = pd.read_csv(csv_path)

    scopes = ["https://www.googleapis.com/auth/spreadsheets "]

    creds = Credentials.from_service_account_info(
        json.loads(GOOGLE_CREDS),
        scopes=scopes
    )

    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())

    print("Planilha atualizada 🚀")


if __name__ == "__main__":
    try:
        print("Iniciando automação...")
        arquivo = baixar_csv()
        enviar_para_sheets(arquivo)
        print("Processo finalizado com sucesso ✅")

    except Exception as e:
        print("Erro durante execução:")
        print(str(e))
        raise

analise essa funcao