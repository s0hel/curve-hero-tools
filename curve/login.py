from playwright.sync_api import sync_playwright

def login(base_url: str, username: str, password: str):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(base_url)
        print(page.title())

        # Fill in username and password
        page.fill("#username", username)
        page.fill("#mat-input-1", password)

        # Submit the form (find and click login button)
        page.click("button[type='submit']")

        # Wait for navigation to complete
        page.wait_for_load_state("networkidle")
        print("Login successful")
        print(f"Current URL: {page.url}")

        browser.close()