# AI Services — Graduation Project

A collection of independent AI microservices, each exposing one machine
learning capability over a REST API, following the platform's shared
architecture spec (see `docs/AI_Platform_Specification_Explained.html`).

Services communicate only with the ASP.NET Core backend — never directly
with each other or the mobile app.

## Services

| Service | Status | Description |
|---|---|---|
| [`asr-service`](./asr-service) | ✅ Working (CPU-tested) | Speech-to-text, Egyptian Arabic + code-switching |

## Documentation

- [`docs/AI_Platform_Specification_Explained.html`](./docs/AI_Platform_Specification_Explained.html) — architecture spec, plain-English + technical
- [`docs/ASR_Service_NET_Integration_Contract.html`](./docs/ASR_Service_NET_Integration_Contract.html) — everything the .NET backend needs to integrate with the ASR service

## Adding a new service

Each service is self-contained in its own folder and follows the same
structure: `app.py`, `routes.py`, `model.py`, `schemas.py`, `config.py`,
`logger.py`, `requirements.txt`, `Dockerfile` — plus `worker.py` and
`queue_broker.py` for any service that processes jobs asynchronously via
RabbitMQ (see the ASR service for a working example of that pattern).
