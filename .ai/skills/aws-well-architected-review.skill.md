# Skill: AWS Well-Architected Review for Agent Changes

## Purpose

Apply AWS Well-Architected thinking when a change affects AWS infrastructure, cloud operations, workloads, or production architecture.

## When to use

Use this skill for changes touching:

- AWS resources.
- Infrastructure as code.
- Deployment pipelines.
- Observability.
- Reliability mechanisms.
- Scaling.
- Cost.
- Security.
- Data storage.
- Networking.
- Incident response.
- Operational runbooks.

## Pillar checklist

### Operational Excellence

- Is the change small and reversible?
- Is the operation defined as code?
- Are runbooks/playbooks updated?
- Is telemetry sufficient?
- Is the deployment risk reduced?

### Security

- Is least privilege preserved?
- Are secrets protected?
- Is data encrypted in transit/at rest where needed?
- Is traceability/auditability preserved?
- Is incident response affected?

### Reliability

- Can the workload recover?
- Are quotas/limits affected?
- Are retries/timeouts/idempotency considered?
- Are backups/migrations safe?
- Is rollback possible?

### Performance Efficiency

- Are resource choices appropriate?
- Are latency/throughput impacts measured?
- Are caching or async patterns considered where useful?
- Are performance tests needed?

### Cost Optimization

- Does the change increase spend?
- Are resources right-sized?
- Are unused resources avoided?
- Are cost allocation tags preserved?

### Sustainability

- Are idle resources minimized?
- Are managed services used where appropriate?
- Is storage/data lifecycle considered?
- Is build/test resource usage reasonable?

## Output

```md
AWS Well-Architected impact:
Operational excellence:
Security:
Reliability:
Performance:
Cost:
Sustainability:
Risks:
Required human review:
```
