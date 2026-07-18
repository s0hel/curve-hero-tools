# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A small Python automation tool that uses Playwright to log into CurveHero (a dental practice
management web app, at `https://zpdentistry.curvehero.com`) using credentials from environment
variables. This is an early-stage project — currently just automates login.

## Commands

This project uses `uv` for dependency management (Python >=3.12).

```bash
# Install dependencies
uv sync

# Install Playwright's browser binaries (required once, and after Playwright upgrades)
uv run playwright install chromium

# Run the tool
uv run save_patients.py
```

There is no test suite, linter, or formatter configured yet.

## Configuration

Credentials are read from a `.env` file (via `python-dotenv`), not committed to git:

```
CURVE_LOGIN=<username>
CURVE_PASSWORD=<password>
```

`main.py` raises a `ValueError` at import time if either variable is missing.

## Architecture

- `main.py` — entry point: loads `.env`, validates credentials are present, calls `curve.login.login`.
- `curve/login.py` — Playwright automation: launches headless Chromium, navigates to the CurveHero
  login page, fills in the username/password fields by CSS selector, submits, and waits for
  `networkidle`.

The login form selectors (`#username`, `#mat-input-1`) are specific to CurveHero's Angular Material
UI and were found by inspecting the live page — if login starts failing, the selectors are the first
thing to re-check, since Angular Material generates the `#mat-input-N` id sequentially and it can
shift if the page's field order changes.
