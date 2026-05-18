# Skill: Scalable Design

## Purpose

Make changes that remain reliable, secure, and maintainable as usage grows.

## Use when

- APIs or endpoints change.
- Database access changes.
- Background jobs or queues change.
- Caches are introduced or modified.
- External service calls are added.
- Concurrency, async, or parallelism is used.
- Data volume can grow.

## Checklist

- Bound every unbounded loop, query, queue, and payload.
- Add pagination, streaming, batching, or limits for large data.
- Add timeouts to external calls.
- Add retries only when operations are safe or idempotent.
- Add jitter to retries to avoid synchronized load.
- Add idempotency keys for commands that can be repeated.
- Avoid global mutable state in concurrent code.
- Make expensive work asynchronous when user latency matters.
- Add observability for latency, error rate, saturation, and business outcomes.
- Document capacity assumptions.

## Scale statement

Every relevant PR must answer:

```md
Scale consideration:
- Expected current usage:
- Main growth risk:
- Boundary/limit added:
- Observability added:
- Follow-up needed before larger scale:
```
