# Skill: Safe File Operations

## Purpose

Prevent accidental deletion or damage to important files, data, infrastructure, or history.

## Default prohibited operations

Do not run:

```bash
rm -rf
git reset --hard
git clean -fdx
git push --force
git branch -D
dropdb
terraform destroy
kubectl delete
aws s3 rm --recursive
```

Do not execute destructive database commands:

```sql
DROP TABLE
DROP DATABASE
TRUNCATE TABLE
DELETE FROM <table>;
```

A `DELETE` with a safe `WHERE` clause in application code may still be high risk and requires review if it affects user data.

## Protected paths

Default protected paths:

```text
.github/
.ai/
infra/
infrastructure/
terraform/
cloudformation/
cdk/
k8s/
kubernetes/
helm/
migrations/
database/migrations/
db/migrations/
secrets/
certs/
.env
.env.*
Dockerfile
docker-compose.yml
package-lock.json
yarn.lock
pnpm-lock.yaml
poetry.lock
requirements.txt
pom.xml
build.gradle
gradle.lockfile
```

Lockfiles can be changed when dependency work is explicitly in scope.

## Deletion policy

File deletion is allowed only when all are true:

- The task explicitly requires deletion.
- The file is not protected.
- The deletion is documented in PR.
- Tests validate behavior.
- Rollback is clear.

## Before deleting or renaming

Ask:

- Is this file generated?
- Is it referenced by build/deploy/runtime?
- Is it part of public API?
- Is it owned by another team?
- Is it used by docs or examples?
- Can this be deprecated first instead?

## Output when deletion is needed

```md
Deletion request:
File/path:
Reason:
Owner:
Impact:
Rollback:
Validation:
Approval needed:
```
