# Task-Scoped Virtual Environment Policy

Agents must create isolated environments per task when the repository language or toolchain benefits from it.

## Environment location

Default ignored path:

```text
.agent/envs/<task-id>/
.agent/cache/
.agent/reports/
```

These paths must not be committed.

## Python

Use:

```bash
python3 -m venv .agent/envs/<task-id>/python
. .agent/envs/<task-id>/python/bin/activate
python -m pip install --upgrade pip
```

Then install using the repository convention:

- `requirements.txt` -> `pip install -r requirements.txt`
- `pyproject.toml` -> `pip install -e .` or `pip install -e ".[dev]"` if supported
- `poetry.lock` -> use `poetry install` only if Poetry is already available
- `Pipfile.lock` -> use `pipenv sync` only if Pipenv is already available

Do not commit `.venv`, `.agent`, or virtual environment files.

## Node.js

Use lockfile-based installs:

- `pnpm-lock.yaml` -> `pnpm install --frozen-lockfile`
- `package-lock.json` -> `npm ci`
- `yarn.lock` -> `yarn install --frozen-lockfile`

Do not change lockfiles unless the task explicitly includes dependency changes.

## Go

Use:

```bash
go mod download
```

Do not edit `go.mod` or `go.sum` unless dependencies are intentionally changed.

## Rust

Use:

```bash
cargo fetch
```

Do not edit `Cargo.lock` unless dependencies are intentionally changed.

## Java

Prefer repository wrappers:

```bash
./mvnw -q -DskipTests dependency:go-offline
./gradlew --no-daemon dependencies
```

## .NET

Use:

```bash
dotnet restore
```

## Ruby

Use a local bundle path:

```bash
bundle config set path .agent/vendor/bundle
bundle install
```

## Escalate when

- System packages are required.
- A dependency install modifies lockfiles unexpectedly.
- Network access is unavailable and dependencies are missing.
- Tests require external credentials or services.
- The repository lacks any reproducible setup path.
