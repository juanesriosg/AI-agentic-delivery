# Skill: Architecture Decision Records

## Purpose

Capture significant decisions so future agents and humans understand why the code is shaped this way.

## Create an ADR when

- A decision is hard to reverse.
- A new dependency, service, database, queue, or architecture pattern is introduced.
- A public contract changes.
- A scale, security, reliability, performance, cost, or sustainability tradeoff is accepted.

## Steps

1. Create `docs/adr/YYYY-MM-DD-short-title.md` or use the repo ADR location.
2. State context and problem.
3. List options considered.
4. State decision.
5. State consequences and rollback/reversal strategy.
6. Link the ADR from the PR.

## Template

Use `.ai/specs/adr-template.md`.
