from dotenv import load_dotenv
import os
import sys
import json
import mysql.connector
from playwright.sync_api import sync_playwright

from curve.login import login
from curve.fetch_patients import fetch_patients

load_dotenv()

base_url = os.getenv("CURVE_BASE_URL")
username = os.getenv("CURVE_LOGIN")
password = os.getenv("CURVE_PASSWORD")
patients_path = os.getenv("PATIENTS_JSON_PATH", "data/patients.json")

db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")

if not base_url or not username or not password:
    raise ValueError("CURVE_BASE_URL, CURVE_LOGIN, and CURVE_PASSWORD must be set in .env file")

if not db_host or not db_user or not db_password or not db_name:
    raise ValueError("DB_HOST, DB_USER, DB_PASSWORD, and DB_NAME must be set in .env file")


def fetch_patients_from_new_session():
    with sync_playwright() as p:
        # Headless Chromium gets flagged by CurveHero's login risk scoring
        # (reCAPTCHA-based) and forces a 2FA step-up that a real browser
        # session skips, so launch the real, headed Chrome instead.
        browser = p.chromium.launch(channel="chrome", headless=False)
        context = browser.new_context()
        page = context.new_page()

        login(page, base_url, username, password)
        patients = fetch_patients(context, base_url)
        print(f"Fetched {len(patients)} patients")

        # Save patients to JSON file
        try:
            with open(patients_path, "w", encoding="utf-8") as f:
                json.dump(patients, f, ensure_ascii=False, indent=2)
            print(f"Saved patients to {patients_path}")
        except Exception as e:
            print(f"Failed to save patients to {patients_path}: {e}")

        browser.close()

def save_patients_to_db():
    with open(patients_path, "r", encoding="utf-8") as f:
        patients = json.load(f)

    connection = mysql.connector.connect(
        host=db_host, user=db_user, password=db_password, database=db_name
    )
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM patients")
        cursor.executemany(
            "INSERT INTO patients (id, data) VALUES (%s, %s)",
            [(patient["id"], json.dumps(patient)) for patient in patients],
        )
        connection.commit()
        cursor.close()
        print(f"Saved {len(patients)} patients to the database")
    finally:
        connection.close()


if __name__ == '__main__':

    if not os.path.exists(patients_path):
        fetch_patients_from_new_session()

    if not os.path.exists(patients_path):
        print(f"No {patients_path} found. Nothing to persist", file=sys.stderr)
        sys.exit(1)

    save_patients_to_db()
