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