# Example Data Question

## Question

How many users started registration during the last 7 days, how many completed it, and where did users drop off?

## Business decision this supports

Decide whether the registration flow needs UX improvements before the next release.

## Time range

Last 7 days.

## Population / cohort

All users who started registration.

## Metric definition

- Started registration: user has `registration_started` event.
- Completed registration: user has `registration_completed` event.
- Drop-off step: last registration step event before no completion.

## Required dimensions

- Registration step
- Device type
- Browser

## Sensitivity

Aggregates only.
