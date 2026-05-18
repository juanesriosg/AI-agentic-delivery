# Concurrency Standards

## Default rule

Do not add concurrency unless it clearly improves latency, throughput, responsiveness, or isolation.

## Required when adding concurrency

- Define ownership of shared state.
- Avoid mutable global state.
- Use locks, channels, queues, actors, or immutable data intentionally.
- Add cancellation or timeout behavior.
- Propagate errors from worker tasks.
- Limit concurrency with a pool, semaphore, queue, or worker count.
- Test failure and cancellation paths where practical.

## Review questions

- Can two requests modify the same data at the same time?
- Can the same job run twice?
- Can workers leak after cancellation?
- Can failures be swallowed?
- Can ordering assumptions break?
- Can this cause a thundering herd?
- Can this starve other work?

## Blockers

- Unbounded goroutines/threads/tasks.
- Fire-and-forget work without error handling.
- Shared mutable state without protection.
- Retried non-idempotent operations.
- Locks without timeout or clear release path.
