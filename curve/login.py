from playwright.sync_api import Page


def login(page: Page, base_url: str, username: str, password: str):
    page.goto(base_url)
    print(page.title())

    # Fill in username and password. formcontrolname is used instead of the
    # auto-generated #mat-input-N ids, which shift if the page's field order
    # changes.
    page.fill("#username", username)
    page.fill("[formcontrolname='password']", password)

    # Submit the form (find and click login button)
    page.click("button[type='submit']")

    # Wait for navigation to complete
    page.wait_for_load_state("networkidle")

    print("Login successful")
    print(f"Current URL: {page.url}")

