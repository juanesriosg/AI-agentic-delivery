# Repo Onboarding Checklist

Complete this once per repo so agents can work safely.

## Basic info

```yaml
repo:
default_branch:
repo_owner:
technical_owner:
business_owner:
primary_reviewers:
deployment_owner:
data_owner:
```

## Repository commands

```yaml
install_command:
test_command:
targeted_test_command:
lint_command:
typecheck_command:
build_command:
format_check_command:
security_scan_command:
dependency_scan_command:
run_local_command:
```

## Tech stack

```yaml
language:
runtime_version:
framework:
package_manager:
database:
cloud_provider:
deployment_platform:
```

## Protected areas

```yaml
protected_paths:
  - path:
    owner:
    reason:
approval_required_paths:
  - path:
    owner:
    reason:
```

## Risk areas

```yaml
auth_paths:
billing_paths:
security_paths:
migration_paths:
infrastructure_paths:
public_api_paths:
deployment_paths:
```

## Testing

```yaml
test_framework:
coverage_command:
coverage_threshold:
known_flaky_tests:
manual_test_needs:
```

## CI/CD

```yaml
ci_provider:
required_checks:
merge_policy:
release_policy:
deployment_policy:
rollback_policy:
```

## Observability

```yaml
logs:
metrics:
traces:
dashboards:
alerts:
runbooks:
```

## Agent policy

```yaml
default_autonomy_level:
max_autonomy_level:
can_open_pr:
can_merge:
can_deploy_nonprod:
can_deploy_prod:
manager_review_required_for:
```

## Missing mechanisms

List missing items:

```text
[ ] README
[ ] test command
[ ] lint command
[ ] typecheck command
[ ] CI
[ ] branch protection
[ ] CODEOWNERS
[ ] PR template
[ ] rollback docs
[ ] runbooks
[ ] observability docs
```
