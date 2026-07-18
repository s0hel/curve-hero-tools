from urllib.parse import urlencode

from playwright.sync_api import BrowserContext


def fetch_appointments(context: BrowserContext, base_url: str, start_date: str, end_date: str, op_ids: list[str]) -> list[dict]:
    query = urlencode(
        [("startDate", start_date), ("endDate", end_date)]
        + [("opIds[]", op_id) for op_id in op_ids]
    )
    url = f"{base_url}/cheetah/calendar_event?{query}"

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
            f"Failed to fetch appointments: {response.status} {response.status_text}"
        )

    result = response.json()
    return result
