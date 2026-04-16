# Hackathon-2026

## Challenge 01 - Licence Application Digital Service

A GOV.UK-styled digital replacement for `FORM-LIC-001-licence-application.pdf`, built with Flask.

## What it does

- Multi-page form following the GOV.UK "one thing per page" principle
- Server-side validation with GOV.UK-style error messages
- Age check (must be 18+) on date of birth
- Check your answers page before submission
- Confirmation page with a unique reference number
- Fully keyboard navigable and screen-reader friendly

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

Then open `http://localhost:5000`.

## Terraform deploy

Uses the shared S3 backend bucket `hackathon-state-ctrl-atl-defeat`.

```powershell
$env:AWS_PROFILE='co-hackathon'
terraform -chdir=infra/cognito/src init
terraform -chdir=infra/cognito/src plan -out=tfplan
terraform -chdir=infra/cognito/src apply tfplan
```

```powershell
$env:AWS_PROFILE='co-hackathon'
terraform -chdir=infra/hosting/src init
terraform -chdir=infra/hosting/src plan -out=tfplan
terraform -chdir=infra/hosting/src apply tfplan
```

Hosting clones the app from GitHub `main` onto the EC2 instance.
