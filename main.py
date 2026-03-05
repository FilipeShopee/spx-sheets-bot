import os
import json
import time
from playwright.sync_api import sync_playwright
from google.oauth2.service_account import Credentials
import gspread

EMAIL = os.getenv("SPX_EMAIL")
PASSWORD = os.getenv("SPX_PASSWORD")
GOOGLE_CREDS = os.getenv("GOOGLE_CREDS")

REPORT_URL = "https://spx.shopee.com.br/#/dashboard/toProductivity"

def get_gspread_client():
    creds_dict = json.loads(GOOGLE_CREDS)

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)

    return gspread.authorize(credentials)

def run():

    print("Iniciando automação...")

    with sync_playwright() as p:

        print("Abrindo navegador...")

        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled"
            ]
        )

        context = browser.new_context()

        page = context.new_page()

        print("Acessando SPX login...")

        page.goto("https://spx.shopee.com.br")

        page.wait_for_timeout(5000)

        print("URL atual:", page.url)

        print("HTML da página:")
        print(page.content())

        print("Procurando campos de login...")

        inputs = page.locator("input").all()

        print("Campos encontrados:", len(inputs))

        for i, inp in enumerate(inputs):
            try:
                print(
                    f"Input {i} | name: {inp.get_attribute('name')} | type: {inp.get_attribute('type')}"
                )
            except:
                pass

        print("Preenchendo login...")

        page.fill('input[type="text"]', EMAIL)
        page.fill('input[type="password"]', PASSWORD)

        page.wait_for_timeout(2000)

        print("Clicando em login...")

        try:
            page.get_by_text("Log In").click(timeout=10000)
        except:
            try:
                page.get_by_role("button").click(timeout=10000)
            except:
                page.locator("button").last.click()

        print("Login enviado...")

        page.wait_for_timeout(10000)

        print("URL após login:", page.url)

        print("Abrindo dashboard produtividade...")

        page.goto(REPORT_URL)

        page.wait_for_timeout(15000)

        print("Página carregada!")

        print("HTML da página do relatório:")
        print(page.content())

        print("Extraindo tabelas...")

        tables = page.locator("table")

        total_tables = tables.count()

        print("Total de tabelas encontradas:", total_tables)

        data = []

        if total_tables > 0:

            rows = tables.first.locator("tr")

            for i in range(rows.count()):

                cols = rows.nth(i).locator("td,th")

                row = []

                for j in range(cols.count()):

                    row.append(cols.nth(j).inner_text())

                data.append(row)

        print("Linhas coletadas:", len(data))

        if len(data) > 0:

            print("Enviando para Google Sheets...")

            client = get_gspread_client()

            spreadsheet = client.open_by_key(os.getenv("SPREADSHEET_ID"))

            sheet = spreadsheet.sheet1

            sheet.clear()

            sheet.update("A1", data)

            print("Dados enviados!")

        else:

            print("Nenhum dado encontrado na tabela.")

        browser.close()

        print("Automação finalizada.")


if __name__ == "__main__":
    run()