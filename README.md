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

.github/workflows/build-push.yml builds the image, scans it with Trivy, and pushes to Amazon ECR using GitHub OIDC, with no stored AWS keys. The IAM role is scoped to this repository and the main branch.

## What I would improve

- Add a database connection timeout so failures return quickly
- Add authentication, input validation, and automated tests
- Pin the Trivy image and GitHub Actions versions

## Clean up

    docker compose down -v