# Terraform Deployment Standard for Agentic Work

All new AWS components must be declared, reviewed, versioned, and deployed through GitHub + Terraform.

## Required for new AWS components

- Terraform module or resource in `infra/terraform/**` or `terraform/**`.
- `terraform fmt`.
- `terraform validate`.
- `terraform plan` artifact on PR.
- Least-privilege IAM.
- Tags for owner, workload, environment, cost center, managed-by.
- Rollback notes.
- Well-Architected notes for operational excellence, security, reliability, performance efficiency, cost optimization, and sustainability.

## Not allowed

- Manual console deployments.
- Raw `aws <service> create-*` commands in application scripts.
- Production applies from agent branches.
- Static long-lived AWS credentials committed to repo or workflow files.

## Recommended GitHub deployment model

```text
PR touching Terraform
  -> terraform plan workflow
  -> manager/repo owner review
  -> approved environment
  -> terraform apply workflow
```

Use GitHub OIDC to assume an AWS role instead of storing AWS access keys where possible.

## Dev deployments

Dev deployments can be automated if the repo explicitly opts in and the target account/environment is safe.

Production remains human-approved by default.
