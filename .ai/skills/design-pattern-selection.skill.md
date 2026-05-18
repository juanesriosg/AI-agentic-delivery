# Skill: Design Pattern Selection

## Purpose

Use patterns to reduce complexity, not to make code look sophisticated.

## Rules

- Start with the simplest design.
- Add a pattern only when it solves a real force: variability, construction complexity, dependency inversion, orchestration, policy selection, or integration boundaries.
- Prefer composition over inheritance.
- Prefer explicit interfaces at architecture boundaries.
- Avoid pattern stacking.
- Document why the pattern was chosen when it affects architecture.

## Common choices

- Strategy: multiple interchangeable algorithms or policies.
- Factory: construction varies and should be centralized.
- Adapter: isolate third-party or legacy APIs.
- Facade: simplify a complex subsystem boundary.
- Repository: isolate persistence concerns when the domain benefits.
- Command: queue, retry, audit, or undo a request.
- Observer/Event: decouple producers from consumers, with caution around debugging and delivery guarantees.

## Anti-patterns

- Abstracting for a future that is not likely.
- Hiding simple logic behind too many interfaces.
- Using global singletons for mutable state.
- Creating generic frameworks inside feature work.
