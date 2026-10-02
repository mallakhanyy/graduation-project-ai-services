# ASR AI Service - Integration Guide

## Overview

This service is responsible for Automatic Speech Recognition (ASR).

The service communicates with the .NET Backend through RabbitMQ.

Communication is completely asynchronous.

Flow:

Client
    │
    ▼
.NET Backend
    │
    ▼
RabbitMQ
(asr.transcription.requests)
    │
    ▼
ASR AI Service
    │
    ▼
RabbitMQ
(asr.transcription.results)
    │
    ▼
.NET Backend
    │
    ▼
Client



---

# Requirements

- Docker
- RabbitMQ
- Python 3.11+

---

# RabbitMQ

Default configuration

Host

localhost

Port

5672

User

guest

Password

guest

Virtual Host

/

Queues

asr.transcription.requests

asr.transcription.results

---

# Request Queue

Queue

asr.transcription.requests

The backend publishes one message per transcription request.

Body

Raw audio bytes

Headers

extension

Example

flac

wav

mp3

CorrelationId

The backend MUST generate a unique Guid.

Example

6f43a87f-c4fc-4d84-8d40-c998742df55e

This value will be returned unchanged.

---

# Result Queue

Queue

asr.transcription.results

Message Body

{
    "request_id": "...",
    "status": "completed",
    "text": "...",
    "processing_time": 3.42,
    "error": null
}

Status values

processing

completed

failed

---

# Startup

Start RabbitMQ

docker start rabbitmq

Run the service

python main.py

The service will wait for incoming requests.

---

# Expected Backend Flow

1. Receive audio from client.

2. Convert audio to bytes.

3. Publish bytes to

asr.transcription.requests

4. Set

CorrelationId

5. Set

extension

header

6. Wait for message from

asr.transcription.results

7. Match

request_id

with the original request.

8. Return transcription to client.

---

# Error Handling

If transcription fails

Status

failed

Example

{
    "request_id":"...",
    "status":"failed",
    "text":null,
    "processing_time":0.0,
    "error":"Unsupported audio format."
}

---

# Supported Audio Formats

wav

flac

mp3

ogg

m4a

---

# Maximum Upload Size

25 MB

---

# Notes

The service is completely stateless.

No audio files are stored permanently.

Temporary audio files are automatically deleted after processing.

Each request is processed independently.

The service is designed to support multiple AI services following the same architecture.