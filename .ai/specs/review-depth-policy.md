# Review Depth Policy

The manager should not review every PR with the same depth.

## Light review

Use for:

- Documentation.
- Tests.
- Isolated low-risk bug fixes.
- Internal refactors with strong tests.
- Non-critical UI copy.

Check:

- Acceptance criteria.
- Validation evidence.
- Scope control.

## Normal review

Use for:

- Feature work.
- Multi-file changes.
- Error handling changes.
- Integration changes.
- Medium-risk changes.

Check:

- Correctness.
- Tests.
- Edge cases.
- Maintainability.
- Rollback.
- Observability.

## Deep review

Use for:

- Auth/authz.
- Billing/payments.
- Security.
- Data migrations.
- Public APIs.
- Infrastructure.
- Deployment pipelines.
- Production config.
- Cross-repo contracts.
- Major dependencies.
- Non-owned repos.

Check:

- Architecture.
- Ownership.
- Security.
- Data integrity.
- Backward compatibility.
- Rollback.
- Operational readiness.
- Human owner approval.
