# Skill: Concurrency and Reliability

## Purpose

Prevent race conditions, hidden failure modes, retry storms, and unsafe async behavior.

## Rules

- Shared mutable state must be protected or removed.
- Background tasks need lifecycle management, cancellation, errors, and observability.
- Network calls need timeouts.
- Retries need backoff and jitter.
- Retried operations must be idempotent or explicitly safe.
- Queues need dead-letter, retry, and poison-message handling where applicable.
- Locks need scope, timeout, and failure handling.
- Transactions need clear boundaries.

## Required tests when applicable

- Duplicate request / retry test.
- Concurrent request test.
- Timeout or dependency failure test.
- Partial failure test.
- Queue/job retry test.

## Escalate

- Distributed locks.
- Cross-service transactions.
- Exactly-once semantics claims.
- Consistency model changes.
- High-throughput or high-concurrency code without test support.
