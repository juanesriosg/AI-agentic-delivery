# Skill: Self-Critique and Refactor

## Purpose

Force the agent to behave like a thoughtful mid-level engineer who reviews and improves its own code before asking for manager review.

## Loop

1. Complete the implementation.
2. Run tests.
3. Read the diff as if reviewing another engineer.
4. Score the change against clean code, architecture, reliability, performance, security, operability, and scale.
5. Fix the useful findings.
6. Rerun validation.
7. Document what was improved and what remains.

## Required questions

- Is the code simpler than the problem requires?
- Did I introduce accidental complexity?
- Are names clear and domain-aligned?
- Are responsibilities separated?
- Are edge cases tested?
- Are errors handled explicitly?
- Is there duplication that should be removed?
- Is there abstraction that should be removed?
- Does this remain safe under concurrency?
- Does this remain safe under high volume?
- Could a future engineer debug this quickly?

## Output format

```md
## Agent self-review

Findings fixed:
- ...

Findings accepted as follow-up:
- ...

Quality score: N/100
Rationale: ...
```
