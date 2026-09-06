# ASR AI Service

A production-ready Automatic Speech Recognition (ASR) microservice built with Python using **Clean Architecture**.

The service consumes audio requests from RabbitMQ, transcribes them using **QwenCleo-ASR**, and publishes transcription results back to RabbitMQ.

---

# Features

- Clean Architecture
- RabbitMQ message-based communication
- QwenCleo-ASR inference
- Automatic audio validation
- Temporary file storage
- Docker support
- Environment-based configuration
- Structured logging
- Production-ready messaging pipeline

---

# Architecture

```
                RabbitMQ

      asr.transcription.requests
                  │
                  ▼
          RabbitMQ Consumer
                  │
                  ▼
          Audio Validation
                  │
                  ▼
         Temporary Audio File
                  │
                  ▼
      Transcription Service
                  │
                  ▼
            Qwen ASR Model
                  │
                  ▼
         Transcription Entity
                  │
                  ▼
         RabbitMQ Publisher
                  │
                  ▼
      asr.transcription.results
```

---

# Project Structure

```
asr-service/

├── application/
│   └── services/
│       └── transcription_service.py
│
├── core/
│   ├── entities/
│   ├── interfaces/
│   ├── enums/
│   └── value_objects/
│
├── infrastructure/
│   ├── messaging/
│   │   ├── rabbitmq_consumer.py
│   │   └── rabbitmq_publisher.py
│   │
│   └── models/
│       └── qwen_asr.py
│
├── shared/
│   ├── config.py
│   ├── logger.py
│   ├── audio_validator.py
│   └── file_storage.py
│
├── tests/
│
├── Dockerfile
├── requirements.txt
├── .env
├── main.py
└── README.md
```

---

# Requirements

- Python 3.12+
- RabbitMQ
- Docker (optional)
- QwenCleo-ASR dependencies

---

# Installation

Create a virtual environment

```bash
python -m venv .venv
```

Activate

Linux

```bash
source .venv/bin/activate
```

Windows

```powershell
.venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file.

Example:

```env
SERVICE_NAME=ASR AI Service
SERVICE_VERSION=1.0.0

MODEL_NAME=mohammedaly22/QwenCleo-ASR

RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest

RABBITMQ_REQUESTS_QUEUE=asr.transcription.requests
RABBITMQ_RESULTS_QUEUE=asr.transcription.results
```

---

# Running RabbitMQ

```bash
docker start rabbitmq
```

RabbitMQ Management UI

```
http://localhost:15672
```

Default credentials

```
guest
guest
```

---

# Running the Service

```bash
python main.py
```

Expected startup

```
Loading Qwen ASR model...
Connecting to RabbitMQ...
RabbitMQ connected successfully.
Starting RabbitMQ consumer...
```

---

# Docker

Build

```bash
docker build -t asr-service .
```

Run

```bash
docker run \
    --network host \
    --env-file .env \
    asr-service
```

---

# Message Format

## Request Queue

Queue

```
asr.transcription.requests
```

Body

```
Raw audio bytes
```

Headers

```json
{
    "extension": "wav"
}
```

Correlation ID

```
request_id
```

---

## Result Queue

Queue

```
asr.transcription.results
```

Example

```json
{
    "request_id": "...",
    "status": "completed",
    "text": "مرحبا",
    "processing_time": 2.31,
    "error": null
}
```

---

# Processing Flow

1. Receive audio from RabbitMQ.
2. Validate audio format and size.
3. Save temporary audio file.
4. Run ASR inference.
5. Build Transcription entity.
6. Publish result to RabbitMQ.
7. Delete temporary file.

---

# Testing

Run the pipeline test

```bash
python -m tests.test_rabbitmq_pipeline
```

---

# Logging

The service logs:

- Model loading
- RabbitMQ connection
- Audio saving
- Audio deletion
- Transcription start
- Transcription completion
- Publishing results
- Errors

---

# Future Improvements

- Health check endpoint
- Prometheus metrics
- Retry mechanism
- Dead Letter Queue (DLQ)
- Multiple ASR model support
- Streaming transcription
- Kubernetes deployment

---

# License

Graduation Project — Helwan University