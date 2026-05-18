# Design Patterns Policy

Agents may use design patterns only when they reduce complexity or isolate a real source of change.

## Good reasons to use a pattern

- The code has multiple interchangeable behaviors.
- Construction is complex and should be centralized.
- A third-party integration should be isolated.
- Domain logic should not depend directly on infrastructure.
- A command needs retry, queueing, audit, or undo semantics.
- A subsystem needs a simpler public interface.

## Bad reasons to use a pattern

- To look senior.
- Because a pattern name appeared in training data.
- Because a future requirement might appear someday.
- To hide a small amount of simple code.
- To create a framework inside a feature.

## Required PR explanation

When adding a non-trivial pattern, include:

```md
Pattern used:
Problem it solves:
Alternatives considered:
Why this is not over-engineering:
How future engineers should extend it:
```
