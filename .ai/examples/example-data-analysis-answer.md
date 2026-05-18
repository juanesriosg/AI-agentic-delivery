# Data Analysis Answer

## Question

How many users started registration during the last 7 days, how many completed it, and where did users drop off?

## Answer

Registration completion is 72.4% for the last 7 days. The biggest drop-off is at the email verification step.

## Key numbers

| Metric | Value | Notes |
|---|---:|---|
| Started registration | 12,430 | Last 7 days |
| Completed registration | 8,997 | Completion rate 72.4% |
| Largest drop-off | Email verification | 1,892 users |

## Business interpretation

The form itself appears usable, but email verification is the largest conversion blocker. Product should review copy, resend behavior, spam-folder guidance, and timeout handling.

## Queries used

- Query 1: Count started and completed registrations.
- Query 2: Count last observed step for users without completion.

## Validation checks

- Confirmed completed users are a subset of started users.
- Compared event counts against daily active-user totals.

## Assumptions

- `registration_started` and `registration_completed` are the canonical events.
- Users are deduplicated by `user_id`.

## Data-quality warnings

- 2.1% of events have missing device type.

## Recommended actions

- Add PM task to improve email verification copy.
- Add QA test for resend verification flow.
- Add instrumentation for verification email delivered/opened if not already available.
