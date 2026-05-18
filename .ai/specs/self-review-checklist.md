# Agent Self-Review Checklist

Before opening a PR, the agent must review its own diff as if reviewing another engineer.

## Clean code

- [ ] Names are clear and domain-specific.
- [ ] Functions/classes have focused responsibilities.
- [ ] No broad unrelated formatting.
- [ ] No accidental complexity.
- [ ] Duplication is handled thoughtfully.
- [ ] Abstractions are justified.

## Architecture

- [ ] Boundaries are respected.
- [ ] Dependencies point in the right direction.
- [ ] Public contracts are stable or explicitly versioned.
- [ ] Configuration is not hardcoded.
- [ ] Significant decisions have ADRs.

## Tests

- [ ] Acceptance criteria have tests or manual evidence.
- [ ] Edge cases are covered.
- [ ] Failure paths are covered where practical.
- [ ] Tests are not weakened.

## Reliability and scale

- [ ] Inputs and resource use are bounded.
- [ ] External calls have timeouts.
- [ ] Retries are limited and idempotent.
- [ ] Concurrent paths are safe.
- [ ] Observability is sufficient.

## Security

- [ ] No secrets are committed.
- [ ] Inputs are validated.
- [ ] Authorization is preserved.
- [ ] Sensitive data is not logged.
- [ ] Injection risks are addressed.

## PR evidence

- [ ] Validation commands and results are included.
- [ ] Self-review findings are included.
- [ ] Scale-readiness findings are included.
- [ ] Risk and rollback are included.
- [ ] Manager action is clear.
