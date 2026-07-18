from dotenv import load_dotenv
import os
import sys
import json
import mysql.connector
from playwright.sync_api import sync_playwright

from curve.fetch_appointments import fetch_appointments
from curve.login import login

load_dotenv()

base_url = os.getenv("CURVE_BASE_URL")
username = os.getenv("CURVE_LOGIN")
password = os.getenv("CURVE_PASSWORD")
op_ids = os.getenv("CURVE_OP_IDS")
appointments_path = os.getenv("APPOINTMENTS_JSON_PATH", "data/appointments.json")

db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")

if not base_url or not username or not password or not op_ids:
    raise ValueError("CURVE_BASE_URL, CURVE_OP_IDS, CURVE_LOGIN, and CURVE_PASSWORD must be set in .env file")

if not db_host or not db_user or not db_password or not db_name:
    raise ValueError("DB_HOST, DB_USER, DB_PASSWORD, and DB_NAME must be set in .env file")

op_ids = op_ids.split(",")

def fetch_appointments_from_new_session(start_date: str, end_date: str, op_ids: list[str]) -> None:
    with sync_playwright() as p:
        # Headless Chromium gets flagged by CurveHero's login risk scoring
        # (reCAPTCHA-based) and forces a 2FA step-up that a real browser
        # session skips, so launch the real, headed Chrome instead.
        browser = p.chromium.launch(channel="chrome", headless=False)
        context = browser.new_context()
        page = context.new_page()

        login(page, base_url, username, password)
        appointments = fetch_appointments(context, base_url, start_date, end_date, op_ids)
        print(f"Fetched {len(appointments)} appointments")

        # Save appointments to JSON file
        try:
            with open(appointments_path, "w", encoding="utf-8") as f:
                json.dump(appointments, f, ensure_ascii=False, indent=2)
            print(f"Saved appointments to {appointments_path}")
        except Exception as e:
            print(f"Failed to save appointments to {appointments_path}: {e}")

        browser.close()

def save_appointments_to_db():
    with open(appointments_path, "r", encoding="utf-8") as f:
        appointments = json.load(f)

    connection = mysql.connector.connect(
        host=db_host, user=db_user, password=db_password, database=db_name
    )
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM appointments")
        cursor.executemany(
            "INSERT INTO appointments (id, data) VALUES (%s, %s)",
            [(appt["id"], json.dumps(appt)) for appt in appointments],
        )
        connection.commit()
        cursor.close()
        print(f"Saved {len(appointments)} appointments to the database")
    finally:
        connection.close()


if __name__ == '__main__':

    if len(sys.argv) != 3:
        print("Usage: save_appointments.py <start_date> <end_date>", file=sys.stderr)
        sys.exit(1)

    start_date, end_date = sys.argv[1], sys.argv[2]

    if not os.path.exists(appointments_path):
        fetch_appointments_from_new_session(start_date, end_date, op_ids)

    if not os.path.exists(appointments_path):
        print(f"No {appointments_path} found. Nothing to persist", file=sys.stderr)
        sys.exit(1)

    save_appointments_to_db()
