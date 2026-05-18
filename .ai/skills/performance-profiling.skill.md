# Skill: Performance Profiling

## Purpose

Use data or disciplined reasoning to keep code fast and resource-efficient.

## Steps

1. Identify the critical path.
2. Estimate complexity and resource use.
3. Look for existing benchmarks, profiling tools, or load tests.
4. Add targeted benchmarks only when useful.
5. Optimize simple bottlenecks first.
6. Avoid caching unless invalidation and consistency are clear.
7. Record performance assumptions in the PR.

## Common fixes

- Replace O(n²) algorithms when input can grow.
- Avoid repeated database calls in loops.
- Batch or paginate external requests.
- Stream large files or result sets.
- Avoid unnecessary serialization and copying.
- Use indexes aligned to query patterns.

## PR evidence

```md
Performance impact:
- Critical path:
- Expected input size:
- Complexity:
- Measurement/benchmark:
- Risk:
```
