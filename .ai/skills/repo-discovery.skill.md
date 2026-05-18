# Skill: Repository Discovery

## Purpose

Quickly understand how to work in an unfamiliar repository without creating unnecessary risk.

## Steps

1. Read README and docs.
2. Inspect package/build files.
3. Inspect CI configuration.
4. Inspect existing test structure.
5. Identify lint/typecheck/build commands.
6. Identify app entry points.
7. Identify high-risk directories.
8. Identify ownership metadata.
9. Identify deployment mechanisms.
10. Record findings in the PR or repo context pack.

## Commands to discover

Look for equivalents of:

```text
install
test
targeted test
lint
typecheck
build
run local
format check
security scan
dependency scan
```

## Risk indicators

Escalate if the repo has:

- No tests.
- No CI.
- No README.
- No clear owner.
- Production credentials in config.
- Direct deployment scripts with no approval gate.
- Database migrations with no rollback guidance.
- Many generated files.
- Large untracked build artifacts.

## Output

```yaml
repo:
language:
framework:
test_command:
lint_command:
typecheck_command:
build_command:
high_risk_paths:
protected_paths:
assumptions:
missing_mechanisms:
```
