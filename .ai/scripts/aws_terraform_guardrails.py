#!/usr/bin/env python3
"""Guardrails that require Terraform for AWS infrastructure changes."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import List

AWS_MUTATING_CLI_PATTERNS = [
    r"aws\s+lambda\s+create-function",
    r"aws\s+lambda\s+update-function-(?:configuration|code)",
    r"aws\s+ec2\s+(?:run-instances|create-|modify-)",
    r"aws\s+rds\s+(?:create-|modify-|delete-)",
    r"aws\s+dynamodb\s+(?:create-table|update-table|delete-table)",
    r"aws\s+s3api\s+(?:create-bucket|delete-bucket|put-bucket)",
    r"aws\s+s3\s+(?:mb|rb|sync)",
    r"aws\s+apigateway.*(?:create|update|delete)",
    r"aws\s+apigatewayv2.*(?:create|update|delete)",
    r"aws\s+iam\s+(?:create-|put-|attach-|detach-|delete-)",
    r"aws\s+cloudformation\s+(?:create-stack|update-stack|deploy|delete-stack)",
    r"aws\s+ecs\s+(?:create-|update-|delete-)",
    r"aws\s+eks\s+(?:create-|update-|delete-)",
    r"aws\s+ecr\s+(?:create-|put-|delete-)",
    r"aws\s+sqs\s+(?:create-queue|delete-queue|set-queue-attributes)",
    r"aws\s+sns\s+(?:create-topic|delete-topic|set-topic-attributes)",
    r"aws\s+secretsmanager\s+(?:create-secret|put-secret-value|delete-secret)",
    r"aws\s+kms\s+create-key",
    r"aws\s+events\s+(?:put-rule|put-targets|delete-rule)",
    r"aws\s+scheduler\s+(?:create-|update-|delete-)",
]
AWS_SERVICE_HINTS = [
    "aws_lambda_function", "aws_apigateway", "aws_api_gateway", "aws_dynamodb_table",
    "aws_db_instance", "aws_s3_bucket", "aws_ec2", "aws_iam_role", "aws_cloudwatch",
    "aws_sqs_queue", "aws_sns_topic", "aws_kms_key", "aws_vpc", "aws_eks", "aws_ecs",
]
APP_AWS_HINTS = ["boto3", "aws-sdk", "@aws-sdk/", "DynamoDBClient", "LambdaClient", "S3Client"]
TERRAFORM_PATHS = ["infra/terraform/", "terraform/", "modules/terraform/"]


def run(cmd: List[str], check: bool = True) -> str:
    cp = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and cp.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{cp.stderr}")
    return cp.stdout


def ref_exists(ref: str) -> bool:
    cp = subprocess.run(["git", "rev-parse", "--verify", "--quiet", ref], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return cp.returncode == 0


def resolve_base_ref(base: str) -> str:
    run(["git", "fetch", "origin", f"{base}:refs/remotes/origin/{base}", "--depth", "1"], check=False)
    remote_base = f"origin/{base}"
    if ref_exists(remote_base):
        return remote_base
    if ref_exists(base):
        return base
    roots = run(["git", "rev-list", "--max-parents=0", "HEAD"], check=False).splitlines()
    return roots[0] if roots else "HEAD"


def expand_path(path: str) -> list[str]:
    if " -> " in path:
        path = path.split(" -> ", 1)[1]
    path = path.strip().replace("\\", "/")
    if not path:
        return []
    p = Path(path)
    if p.is_dir():
        return [child.as_posix() for child in p.rglob("*") if child.is_file() and ".git" not in child.parts]
    return [path]


def changed_files(base: str) -> List[str]:
    base_ref = resolve_base_ref(base)
    out = run(["git", "diff", "--name-only", f"{base_ref}...HEAD"], check=False)
    files = [x.strip() for x in out.splitlines() if x.strip()]
    status = run(["git", "status", "--porcelain"], check=False)
    for line in status.splitlines():
        if line.strip():
            raw = line[3:].strip() if len(line) > 3 else line.strip()
            files.extend(expand_path(raw))
    return sorted(set(files))


def untracked_text() -> str:
    chunks: list[str] = []
    for name in run(["git", "ls-files", "--others", "--exclude-standard"], check=False).splitlines():
        p = Path(name)
        try:
            data = p.read_bytes()
        except Exception:
            continue
        if b"\0" in data:
            continue
        text = data.decode("utf-8", errors="replace")
        chunks.append(f"\n# Untracked file: {name}\n" + "\n".join("+" + line for line in text.splitlines()))
    return "\n".join(chunks)


def changed_text(base: str) -> str:
    base_ref = resolve_base_ref(base)
    parts = [
        run(["git", "diff", f"{base_ref}...HEAD"], check=False),
        run(["git", "diff", "--cached"], check=False),
        run(["git", "diff"], check=False),
        untracked_text(),
    ]
    return "\n".join(part for part in parts if part)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--aws-change", action="store_true")
    args = parser.parse_args()

    files = changed_files(args.base)
    diff = changed_text(args.base)
    failures: list[str] = []
    warnings: list[str] = []

    raw_aws_mutations = [pat for pat in AWS_MUTATING_CLI_PATTERNS if re.search(pat, diff, re.I)]
    terraform_files = [f for f in files if f.endswith(".tf") or any(f.startswith(prefix) for prefix in TERRAFORM_PATHS)]
    terraform_service_refs = [hint for hint in AWS_SERVICE_HINTS if hint in diff]
    app_aws_refs = [hint for hint in APP_AWS_HINTS if hint.lower() in diff.lower()]
    github_workflow_deploys = [f for f in files if f.startswith(".github/workflows/") and ("deploy" in f or "terraform" in f or "infra" in f)]

    if raw_aws_mutations:
        failures.append("Raw mutating AWS CLI commands detected. Use Terraform + GitHub workflow instead: " + ", ".join(raw_aws_mutations))

    if args.aws_change and not terraform_files:
        failures.append("AWS/cloud change marked but no Terraform files changed.")

    if terraform_files:
        if shutil.which("terraform"):
            fmt = subprocess.run(["terraform", "fmt", "-check", "-recursive"], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if fmt.returncode != 0:
                failures.append("terraform fmt -check -recursive failed. Run fmt and include plan evidence.")
        else:
            warnings.append("Terraform CLI is not installed here; dedicated Terraform plan workflow must validate fmt/plan.")

    if terraform_service_refs and not terraform_files:
        failures.append("AWS Terraform resource references found, but no Terraform path changed.")

    if app_aws_refs and not terraform_files and not args.aws_change:
        warnings.append("AWS SDK usage detected. Confirm this is runtime integration, not infrastructure provisioning.")

    report = {
        "files": files,
        "terraform_files": terraform_files,
        "workflow_deploy_files": github_workflow_deploys,
        "raw_aws_mutating_patterns": raw_aws_mutations,
        "terraform_service_refs": terraform_service_refs,
        "app_aws_refs": app_aws_refs,
        "warnings": warnings,
        "failures": failures,
    }
    print(json.dumps(report, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
