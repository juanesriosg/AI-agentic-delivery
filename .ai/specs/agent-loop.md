# Agent Execution Loop

## Main loop

```text
while workday_active:
  refresh_board()
  if has_review_comments_on_my_prs:
      handle_review_comments()
      continue

  if active_task_exists:
      continue_active_task()
      continue

  next_task = select_next_ready_task()
  if not next_task:
      report_queue_empty()
      stop_or_wait_for_next_manual_trigger()

  if not ready(next_task):
      mark_not_ready_with_reason()
      continue

  claim(next_task)
  create_branch(next_task)
  discover_repo_context()
  assess_risk()

  if risk_high and approval_missing:
      block_and_notify()
      continue

  implement()
  validate()
  self_review()

  if quality_score < threshold:
      iterate_once()
      validate()
      self_review()

  if still_not_ready:
      block_and_notify()
      continue

  open_pr()
  notify_manager()
  record_metrics()
  continue
```

## Task selection algorithm

Choose the highest-priority task that:

- Has `ai:ready`.
- Is not claimed.
- Has clear acceptance criteria.
- Does not touch files in one of your open PRs.
- Is within your autonomy level.
- Does not require blocked dependency.

Tie-breakers:

1. Lower risk first.
2. Smaller PR first.
3. Same repo as previous context if no conflict.
4. Bugfix before feature.
5. Test/mechanism improvement when queue lacks low-risk product tasks.

## Review response loop

```text
if review_comments:
  classify_comments()
  implement_must_fix_comments()
  answer_questions()
  rerun_validation()
  update_pr()
  notify_manager()
```

## Stop conditions

Stop and notify when:

- Production access is required.
- A secret is needed.
- Ownership is unclear.
- High-risk change lacks approval.
- Tests fail for unrelated reasons and block validation.
- Repository state is unsafe.
- Requirements conflict.
