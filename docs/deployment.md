# Deployment Documentation

## Development Deployment (Local)

The application is designed to run locally using an in-memory database for rapid development and testing.

### Prerequisites

- [uv](https://github.com/astral-sh/uv) installed on your machine.

### Setup and Running

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Run the application:**
   ```bash
   uv run run.py
   ```
   The application will be available at `http://127.0.0.1:5000`.

3. **Login with Dummy Data:**
   - **User Type:** Referrer
   - **Email:** `referrer@test.com`
   - **Password:** `password`

### Dummy Data
In development mode, the application is pre-loaded with sample referrers and referrals. See [Dummy Data Reference](./dummy_data_reference.md) for details.

---

## Live Deployment (AWS)

Live deployment uses AWS services:
- **Compute:** EC2
- **Authentication:** Amazon Cognito
- **Database:** DynamoDB
- **Storage:** S3 (for assets)

### Prerequisites

- AWS Account and CLI configured.
- [Terraform](https://www.terraform.io/) installed.

### Infrastructure Setup

Infrastructure is managed via Terraform in the `infra/` directory.

1. **Navigate to the infrastructure source:**
   ```bash
   cd infra/hosting/src
   ```

2. **Initialize and apply Terraform:**
   ```bash
   terraform init
   terraform apply
   ```
   (Repeat for `infra/cognito/src`, `infra/dynamodb/src`, and `infra/s3/src` as necessary).

### Application Deployment

The application is typically deployed to EC2 using the provided `user_data.sh.tftpl` template, which sets up the environment and runs the Flask application.

Set the following environment variables in your production environment:
- `APP_BACKEND=aws`
- `AWS_REGION`
- `COGNITO_USER_POOL_ID`
- `COGNITO_USER_POOL_CLIENT_ID`
- `REFERRALS_TABLE_NAME`
