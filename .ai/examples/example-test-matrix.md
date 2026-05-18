# Example Test Matrix

| AC ID | Requirement | Unit | Component | Integration | Contract | E2E | Dev/QA | Evidence | Status |
|---|---|---|---|---|---|---|---|---|---|
| AC-001 | Admin can export CSV | formatter test | endpoint test | auth+db export | OpenAPI response | critical flow smoke | QA download | command output | passed |
| AC-002 | Non-admin denied | permission rule | endpoint 403 | auth integration | OpenAPI 403 | negative smoke | QA role test | command output | passed |
| AC-003 | Large export is bounded | pagination test | service test | large fixture | N/A | N/A | QA fixture | memory notes | passed |
