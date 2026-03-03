from playwright.sync_api import sync_playwright
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import time
import os
import json
import tempfile


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
        page.goto("https://spx.shopee.com.br", wait_until="networkidle")

        print("URL após carregamento:", page.url)

        # Aguarda página de login carregar completamente
        page.wait_for_load_state("networkidle")
        time.sleep(3)

        # VERIFICA SE ESTÁ NA PÁGINA DE LOGIN
        if "authenticate/login" in page.url or "fms.business.accounts" in page.url:
            print("Detectada página de login centralizado da Shopee")
            
            # Preenche pelo tipo (já que name/id são None)
            print("Preenchendo credenciais...")
            
            # Input de email (type="text")
            email_input = page.locator('input[type="text"]').first
            email_input.wait_for(state="visible", timeout=10000)
            email_input.fill(SPX_EMAIL)
            
            # Input de senha (type="password")  
            pass_input = page.locator('input[type="password"]').first
            pass_input.wait_for(state="visible", timeout=10000)
            pass_input.fill(SPX_PASSWORD)
            
            # Clica no botão de login (geralmente é um button ou div com texto específico)
            # Tentativa 1: button com type submit
            submit_btn = page.locator('button[type="submit"]')
            if submit_btn.count() > 0:
                submit_btn.first.click()
            else:
                # Tentativa 2: button com texto "Entrar" ou "Login"
                page.click('button:has-text("Entrar"), button:has-text("Login"), button:has-text("Sign in")')
            
            print("Aguardando autenticação...")
            
            # Aguarda redirecionamento de volta ao SPX
            page.wait_for_url("**/spx.shopee.com.br/**", timeout=60000)
            print("Login realizado! URL atual:", page.url)
            
            # Aguarda dashboard carregar
            page.wait_for_load_state("networkidle")
            time.sleep(3)
        
        else:
            print("Já está logado ou página diferente do esperado")

        # NAVEGAÇÃO PARA O RELATÓRIO
        print("Navegando para relatório de produtividade...")
        page.goto("https://spx.shopee.com.br/#/dashboard/toProductivity", wait_until="networkidle")
        
        # Aguarda carregar
        time.sleep(5)
        
        # Tenta encontrar botão de Export
        print("Procurando botão de exportação...")
        export_selectors = [
            'text=Export',
            'button:has-text("Export")',
            '[data-testid="export"]',
            '.export-btn',
            'button:has-text("Exportar")'
        ]
        
        export_btn = None
        for selector in export_selectors:
            if page.locator(selector).count() > 0:
                export_btn = page.locator(selector).first
                print(f"Botão encontrado com: {selector}")
                break
        
        if not export_btn:
            # DEBUG: salvar screenshot para ver o que está na página
            page.screenshot(path="/tmp/debug_page.png")
            print("Screenshot salvo em /tmp/debug_page.png")
            raise Exception("Botão de exportação não encontrado")

        # DOWNLOAD DO ARQUIVO
        print("Iniciando download...")
        with page.expect_download(timeout=60000) as download_info:
            export_btn.click()
        
        download = download_info.value
        
        # Salva em arquivo temporário
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.csv') as tmp:
            download_path = tmp.name
        
        download.save_as(download_path)
        print(f"Download concluído: {download_path}")

        browser.close()
        return download_path


def enviar_para_sheets(csv_path):
    if not csv_path or not os.path.exists(csv_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {csv_path}")
    
    print(f"Enviando {csv_path} para Sheets...")

    df = pd.read_csv(csv_path)

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]

    creds = Credentials.from_service_account_info(
        json.loads(GOOGLE_CREDS),
        scopes=scopes
    )

    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())

    print("Planilha atualizada 🚀")
    
    # Limpa arquivo temporário
    os.unlink(csv_path)


if __name__ == "__main__":
    # Validação de variáveis
    required = [SPREADSHEET_ID, SHEET_NAME, SPX_EMAIL, SPX_PASSWORD, GOOGLE_CREDS]
    if not all(required):
        raise ValueError("Variáveis de ambiente obrigatórias não configuradas!")
    
    try:
        print("Iniciando automação...")
        arquivo = baixar_csv()
        if arquivo:
            enviar_para_sheets(arquivo)
            print("Processo finalizado com sucesso ✅")
        else:
            print("Falha ao baixar arquivo")
            
    except Exception as e:
        print(f"Erro durante execução: {e}")
        raise