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

## Specific problem:
Currently, when early years professionals or healthcare staff (such as midwives or nursery workers) refer a parent and child to a Family Hub, they are forced to navigate a heavily manual, paper-based workflow. The existing process relies on a cumbersome 4-page PDF ("Request for Children's Centre Service") that creates immediate administrative friction and delays vital support for families.

The Core Challenges:

Administrative Burden for Staff: Referring professionals must locate, download, manually complete, and securely email extensive PDF forms. This redirects valuable time away from frontline care and bogs them down in repetitive paperwork.

High Friction for Parents: Families—who may already be in vulnerable situations or under stress—face unnecessary bureaucratic hurdles, including physical signature requirements and delays in processing. Furthermore, they often have to repeat the same basic information upon arriving at the Hub for their first session.

Inefficient Processing & Data Silos: Family Hub administration must manually transcribe data from emailed PDFs into internal systems. This slows down triage, delays assigning a caseworker, and leaves Service Managers without real-time analytics regarding referral volumes and physical check-ins.

## Our objective:

To replace the legacy PDF referral process with a streamlined, end-to-end digital portal. By introducing rapid digital registration, automated caseworker routing, and unique family IDs for self-service check-ins, this project aims to reduce referral turnaround times from days to minutes—ensuring families get connected to the support they need with zero administrative friction.

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
terraform -chdir=infra/dynamodb/src init
terraform -chdir=infra/dynamodb/src plan -out=tfplan
terraform -chdir=infra/dynamodb/src apply tfplan
```

```powershell
$env:AWS_PROFILE='co-hackathon'
terraform -chdir=infra/hosting/src init
terraform -chdir=infra/hosting/src plan -out=tfplan
terraform -chdir=infra/hosting/src apply tfplan
```

Hosting clones the app from GitHub `main` onto the EC2 instance.
