# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A small Python automation tool that uses Playwright to log into CurveHero (a dental practice
management web app) as a real user, fetches the practice's patient list via CurveHero's internal
API, and persists it to a MySQL database. Early-stage / single-purpose project.

## Commands

This project uses `uv` for dependency management (Python >=3.12).

```bash
# Install dependencies
uv sync

# Install Playwright's browser binaries (required once, and after Playwright upgrades)
uv run playwright install chromium

# One-time: create the `patients` table
uv run db/create_schema.py

# Run the tool: fetches patients (if data/patients.json doesn't exist yet) and loads them into MySQL
uv run save_patients.py
```

There is no test suite, linter, or formatter configured yet.

## Configuration

Read from a `.env` file (via `python-dotenv`, gitignored) — see `.env.example` for the template:

```
CURVE_BASE_URL=https://xxxx.curvehero.com
CURVE_LOGIN=<username>
CURVE_PASSWORD=<password>

DB_HOST=...
DB_USER=...
DB_PASSWORD=...
DB_NAME=...
```

Both `save_patients.py` and `db/create_schema.py` raise a `ValueError` at import time if their
required variables are missing.

## Architecture

- `save_patients.py` — entry point with two phases, run unconditionally in sequence:
  1. `fetch_patients_from_new_session()` — only runs if `data/patients.json` (path overridable via
     `PATIENTS_JSON_PATH`) doesn't already exist. Launches Playwright, logs in via
     `curve.login.login`, fetches patients via `curve.fetch_patients.fetch_patients`, and writes
     the raw JSON to disk.
  2. `save_patients_to_db()` — always runs. Reads `data/patients.json`, and does a full
     delete-and-reinsert into the MySQL `patients` table (one row per patient: `id` +
     full record as a `JSON` column).

  Because phase 1 is skipped once the JSON file exists, re-running the script re-imports from the
  cached file into the DB without re-scraping. Delete `data/patients.json` to force a fresh fetch.

- `curve/login.py` — logs into CurveHero. **Must launch headed Chrome** (`channel="chrome",
  headless=False`), not headless Chromium — CurveHero's login risk scoring (reCAPTCHA-based) flags
  headless sessions and forces a 2FA step-up that a real browser session skips. Fills the login
  form via `formcontrolname` attribute selectors (not the auto-generated `#mat-input-N` ids, which
  are Angular Material internals that shift if the page's field order changes) and waits for
  `networkidle` after submit.

- `curve/fetch_patients.py` — calls CurveHero's internal `keywordSearch` REST endpoint directly via
  `context.request` (not page scraping). This reuses the browser context's cookie jar, so the
  session cookie set during login is sent automatically. Fetches active patients with mailing
  addresses.

- `db/create_schema.py` — standalone script to create the `patients` table
  (`id VARCHAR(64) PRIMARY KEY, data JSON NOT NULL`). Run once before the first `save_patients.py`
  run against a new database.

- `data/patients.json` — local cache of the last successful fetch; acts as a checkpoint between the
  scrape and DB-load phases. Not committed to git.
