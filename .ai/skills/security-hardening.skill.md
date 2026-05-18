# Skill: Security Hardening

## Purpose

Make security a default part of coding, not a final audit.

## Checklist

- Validate and normalize input.
- Enforce authorization at the server/service boundary.
- Do not trust client-side checks.
- Avoid unsafe deserialization, eval, shell interpolation, and raw SQL string concatenation.
- Do not log secrets, tokens, PII, or sensitive payloads.
- Use parameterized queries.
- Use least privilege.
- Protect data in transit and at rest where applicable.
- Use secure defaults.
- Add tests for forbidden access when auth changes.

## Escalate immediately

- Secrets are found.
- Production data is needed.
- Access control behavior changes.
- Encryption or key management changes.
- A dependency appears malicious or abandoned.
