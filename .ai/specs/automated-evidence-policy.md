# Automated Evidence Policy

Agents should attach evidence to work rather than relying on claims.

## Evidence types

- Test command output
- Unit/component/integration/E2E results
- Screenshots and annotations
- QA checklist
- PM checklist
- Logs
- Performance report
- Security scan result
- Cloud readiness report
- Release readiness report

## Evidence storage

Use `.agent/stories/<story-id>/` for story-level evidence. Use `.agent/reports/` for repo-level summaries. These files are normally artifacts and may not all be committed unless the repo policy allows it. The PR should link or summarize them.

## Failed evidence

Failed evidence must be retained in the agent log and reports. Agents should not hide failed iterations because failed iterations show the review and improvement loop.
