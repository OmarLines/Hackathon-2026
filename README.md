# Hackathon-2026

## Terraform S3 state bucket

Uses `hackathon-state-ctrl-atl-defeat/shared/terraform.tfstate` from `C:\dev\repo\Hackathon-2026\infra\s3\src`.

```powershell
$env:AWS_PROFILE='co-hackathon'
terraform -chdir=infra/s3/src init
terraform -chdir=infra/s3/src plan -out=tfplan
terraform -chdir=infra/s3/src apply tfplan
```
