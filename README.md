# Inventory API (Docker Compose)

A small internal inventory service built to practice container fundamentals: an API, a database that keeps its data, and an admin UI, all started with one command.

## What it demonstrates

- Multi-container design with service-name networking (Flask API, Postgres 16, Adminer)
- Multi-stage Dockerfile and a non-root runtime user
- Health checks and startup ordering (depends_on with service_healthy)
- Configuration kept out of code (.env, never committed)
- Data persistence with a named volume

## Run it

    git clone https://github.com/fiehna-hue/inventory-app.git
    cd inventory-app
    cp .env.example .env
    docker compose up -d --build

## Try it

    curl -s localhost:8000/health
    curl -s -X POST localhost:8000/items -H 'Content-Type: application/json' -d '{"name":"laptop","quantity":5}'
    curl -s localhost:8000/items

Adminer: http://localhost:8082 (System: PostgreSQL, Server: db)

## CI pipeline

`.github/workflows/build-push.yml` builds the image, scans it with Trivy, and pushes it to Amazon ECR tagged with the commit SHA. It authenticates with GitHub OIDC, so no AWS keys are stored anywhere: the IAM role trusts only this repository and the `main` branch. The pipeline runs green end to end, and the image tag in ECR matches the commit.

Debugging note: the first runs failed with AccessDenied because the role's trust policy did not match GitHub's current OIDC subject, which now includes numeric owner and repository IDs. I found the real subject in CloudTrail (`AssumeRoleWithWebIdentity` events) and updated the trust policy.

## What I would improve

- Add a database connection timeout so failures return quickly
- Add authentication, input validation, and automated tests
- Pin the Trivy image and GitHub Actions versions

## Clean up

    docker compose down -v

## Related

- [inventory-infra](https://github.com/fiehna-hue/inventory-infra): the same API deployed on ECS Fargate with Terraform.
- [aws-platform-as-code](https://github.com/fiehna-hue/aws-platform-as-code): a full platform shipped through a plan-on-PR, apply-on-merge pipeline.

## CI pipeline

Every pull request and every push to `main` runs the `build-scan-push` workflow:

1. **test**: starts a Postgres service container and runs the pytest integration tests against the real API.
2. **build**: runs only if the tests pass. It builds the multi-stage, non-root Docker image.
3. **scan**: Trivy scans the image and fails the build on fixable HIGH or CRITICAL vulnerabilities.
4. **push** (only on `main`): authenticates to AWS with GitHub OIDC (no stored access keys) and pushes the image to ECR tagged with the commit SHA.

### What broke while building it

The first run of the test job failed with `ModuleNotFoundError: No module named 'app'`. The tests live in `tests/`, and pytest did not have the repo root on its import path. Fix: a `pytest.ini` with `pythonpath = .`. The failure also showed the gate working, because the image build was skipped when the tests failed.
