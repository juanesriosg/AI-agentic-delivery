# Skill: Risk Assessment

## Purpose

Classify task/PR risk so the manager can review the right things deeply.

## Low risk

Examples:

- Small isolated bug fix.
- Test addition.
- Documentation update.
- Internal refactor with tests.
- Non-critical UI copy.

Agent may proceed to PR.

## Medium risk

Examples:

- Moderate feature change.
- Multiple modules touched.
- New dependency patch/minor.
- Error handling behavior changes.
- Performance-sensitive code.
- External integration behavior.

Agent may proceed to PR, but must flag manager attention.

## High risk

Examples:

- Auth/authz.
- Security.
- Billing/payments.
- Data migrations.
- Data deletion.
- Production config.
- Infrastructure.
- Deployment pipeline.
- Public API contracts.
- Cross-repo contracts.
- Major dependency upgrades.
- Large refactors.
- Non-owned repo changes.

Agent must escalate before implementation unless the task explicitly authorizes the change.

## Risk score

Score each dimension 1-5:

```yaml
customer_impact:
security:
data_integrity:
rollback_difficulty:
blast_radius:
ownership_complexity:
test_confidence:
```

Overall risk:

```text
Low: no score above 2
Medium: any score 3
High: any score 4 or 5
```

## Output

```md
Risk level:
Reason:
Blast radius:
Rollback difficulty:
Human review required:
```
