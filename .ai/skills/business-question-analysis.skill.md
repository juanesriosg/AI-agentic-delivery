# Skill: Business Question Analysis

## Purpose

Turn a business question into an answer backed by context, metrics, and safe data queries.

## Steps

1. Identify the decision being made.
2. Define the metric or outcome.
3. Define the population/cohort.
4. Define the time window.
5. Identify relevant business rules.
6. Identify relevant specs and PRs.
7. Identify database entities and tables.
8. Ask clarifying questions if ambiguity blocks correctness.
9. Continue with safe exploratory analysis if ambiguity is not blocking.
10. Run read-only SQL only through `.ai/scripts/safe_sql_query.py`.
11. Validate results.
12. Provide recommendation and confidence level.

## Output quality

A good answer is actionable, short, and traceable. It should say what changed, why it matters, and what the manager should decide next.
