# Clarification Request from Spec

Status: Needs manager decision, safe progress continuing
Spec: `specs/export-orders-csv.spec.md`
Branch: `dev/export-orders-csv`
Agent: Mid Software Engineer

## Question

AC-004 says the export must complete within the repository's existing performance expectations, but no explicit threshold exists in the repo.

Which target should I use for the first implementation?

1. keep current synchronous endpoint and document measured local runtime,
2. target under 5 seconds for 10,000 orders in dev/test,
3. avoid time-based acceptance and only enforce bounded memory/streaming behavior.

## Why this matters

The answer affects architecture and validation. It determines whether a simple streaming response is enough or whether the feature needs a background job design.

## Safe progress continuing

I will continue with:

- endpoint discovery,
- authorization test discovery,
- CSV formatting unit tests,
- empty result behavior,
- forbidden user regression test.

I will not implement background jobs or change public API shape until this is clarified.
