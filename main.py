from playwright.sync_api import sync_playwright
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import time
import os

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SHEET_NAME = os.getenv("SHEET_NAME")

SPX_EMAIL = os.getenv("SPX_EMAIL")
SPX_PASSWORD = os.getenv("SPX_PASSWORD")


def baixar_csv():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Login
        page.goto("https://spx.shopee.com.br")
        page.fill('input[type="email"]', SPX_EMAIL)
        page.fill('input[type="password"]', SPX_PASSWORD)
        page.click("button[type=submit]")

        page.wait_for_load_state("networkidle")

        # Ir para dashboard
        page.goto("https://spx.shopee.com.br/#/dashboard/toProductivity")
        page.wait_for_load_state("networkidle")

        # Exportar
        with page.expect_download() as download_info:
            page.click("text=Export")

        download = download_info.value
        path = "report.csv"
        download.save_as(path)

        browser.close()
        return path


def enviar_para_sheets(csv_path):
    df = pd.read_csv(csv_path)

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(
        eval(os.getenv("GOOGLE_CREDS")),
        scopes=scopes
    )

    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())

    print("Planilha atualizada com sucesso 🚀")


if __name__ == "__main__":
    arquivo = baixar_csv()
    enviar_para_sheets(arquivo)