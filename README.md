# Challenge 01 — Licence Application Digital Service

A GOV.UK-styled digital replacement for `FORM-LIC-001-licence-application.pdf`, built with Flask.

## What it does

- Multi-page form following the GOV.UK "one thing per page" principle
- Server-side validation with GOV.UK-style error messages
- Age check (must be 18+) on date of birth
- Check your answers page before submission
- Confirmation page with a unique reference number
- Fully keyboard navigable and screen-reader friendly (GOV.UK Frontend)

## Setup

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv python install 3.13
uv sync
```

## Run

```bash
uv run python run.py
```

Then open http://localhost:5000
