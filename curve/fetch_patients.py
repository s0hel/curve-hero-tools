from playwright.sync_api import BrowserContext


def fetch_patients(context: BrowserContext, base_url: str) -> list[dict]:
    # context.request shares the browser context's cookie jar, so the
    # curve_hero_session cookie set during login is sent automatically -
    # no need to copy cookies over manually.
    url = f"{base_url}/cheetah/contacts/keywordSearch?addressType=mailing&status=Active,New+Patient"

    response = context.request.get(
        url,
        headers={
            "Accept": "application/json, text/plain, */*",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"{base_url}/",
        },
    )

    if not response.ok:
        raise RuntimeError(
            f"Failed to fetch patients: {response.status} {response.status_text}"
        )

    result = response.json()
    items = result["items"] if "items" in result else []
    return items
