#  Arabic Comment Moderation Service

A production-ready microservice for moderating Arabic comments using a fine-tuned **AraBERT** model with **async processing** via RabbitMQ.

---

## 📋 **Table of Contents**
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Running the Project](#-running-the-project)
- [API Endpoints](#-api-endpoints)
- [Testing the API](#-testing-the-api)
- [Async Moderation Flow](#-async-moderation-flow)
- [Docker Deployment](#-docker-deployment)
- [Environment Variables](#-environment-variables)
- [Monitoring](#-monitoring)
- [License](#-license)

---

## ✨ **Features**

- 🤖 **Arabic Text Classification** - Fine-tuned AraBERT model (4 labels: Relevant, Spam, Offensive, Irrelevant)
- ⚡ **Async Processing** - RabbitMQ for background task processing
- 🚀 **FastAPI** - High-performance REST API with automatic Swagger documentation
- 📦 **Docker Support** - Easy deployment with Docker Compose
- 🔍 **Health Checks** - Kubernetes-ready health, readiness, and liveness probes
- 📊 **Queue Monitoring** - RabbitMQ management UI for monitoring
- 🔄 **Async & Sync Support** - Both synchronous and asynchronous endpoints available

---

## 🛠️ **Tech Stack**

| Component | Technology |
|-----------|------------|
| **API Framework** | FastAPI 0.104.1 |
| **ML Model** | AraBERT (aubmindlab/bert-base-arabertv02) |
| **Message Queue** | RabbitMQ 3.12 |
| **Async Worker** | Python (pika 1.3.2) |
| **Containerization** | Docker & Docker Compose |
| **Python Version** | 3.12+ |
| **ML Framework** | PyTorch 2.0.1, Transformers 4.36.0 |

---

## 📁 **Project Structure**
moderation-service/
├── moderation_service/ # Main application package
│ ├── api/v1/ # API routes
│ │ ├── dependencies.py # Dependency injection
│ │ └── routes.py # Endpoints
│ ├── core/ # Core configuration
│ │ ├── config.py # Settings
│ │ ├── exceptions.py # Custom exceptions
│ │ └── logger.py # Logging
│ ├── domain/ # Domain models
│ │ ├── entities.py # Entities
│ │ └── value_objects.py # Value objects
│ ├── infrastructure/ # External services
│ │ ├── model/ # AraBERT model files
│ │ │ └── WAHA_KUN_AraBERT/
│ │ └── rabbitmq/ # RabbitMQ client
│ │ ├── producer.py # Sends messages
│ │ ├── consumer.py # Receives messages
│ │ └── result_producer.py # Sends results
│ ├── schemas/ # Pydantic schemas
│ │ ├── request.py
│ │ └── response.py
│ ├── services/ # Business logic
│ │ ├── moderation_service.py
│ │ └── interfaces/
│ └── workers/ # Async workers
│ └── moderation_worker.py
├── tests/ # Unit tests
├── .env.example # Environment variables template
├── docker-compose.yml # Docker services
├── Dockerfile # Docker image
├── requirements.txt # Python dependencies
└── README.md # This file

text

---

## 📋 **Prerequisites**

- **Python 3.12+**
- **Docker** and **Docker Compose** (for containerized deployment)
- **Git** (for cloning)
- **At least 4GB RAM** (8GB recommended)

---

## 🚀 **Installation**

### **1. Clone the Repository**
```bash
git clone https://github.com/mallakhanyy/graduation-project-ai-services.git
cd graduation-project-ai-services/moderation-service
2. Create Virtual Environment
bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
3. Install Dependencies
bash
pip install -r requirements.txt
4. Set Up Environment Variables
bash
cp .env.example .env
# Edit .env with your configuration
5. Download the Model
Place your fine-tuned AraBERT model in:

text
moderation_service/infrastructure/model/WAHA_KUN_AraBERT/
Required files:

config.json

model.safetensors

tokenizer.json

tokenizer_config.json

special_tokens_map.json

🏃 Running the Project
Method 1: Using Docker (Recommended)
Step 1: Start RabbitMQ
bash
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
Step 2: Build and Run with Docker Compose
bash
docker-compose up -d --build
Step 3: Check Services
bash
docker-compose ps
Method 2: Running Locally
Terminal 1: Start RabbitMQ
bash
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
Terminal 2: Start the Worker
bash
cd /path/to/moderation-service
venv\Scripts\activate
python -m moderation_service.workers.moderation_worker
Terminal 3: Start the API Server
bash
cd /path/to/moderation-service
venv\Scripts\activate
uvicorn moderation_service.main:app --reload --host 0.0.0.0 --port 8000
Expected Output:

text
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
🌐 API Endpoints
Base URL
text
http://localhost:8000
Endpoints Table
Method	Endpoint	Description	Response Time
GET	/	Root endpoint	~5ms
GET	/docs	Swagger UI Documentation	N/A
GET	/api/v1/health	Health check	~5ms
GET	/api/v1/ready	Readiness probe	~5ms
GET	/api/v1/live	Liveness probe	~5ms
POST	/api/v1/moderate	Sync comment moderation	~1-3s
POST	/api/v1/moderate/async	Async comment moderation	~10ms
1. Health Check
GET /api/v1/health

Response:

json
{
  "status": "healthy",
  "version": "1.0.0",
  "model_loaded": true,
  "rabbitmq_connected": true,
  "uptime_seconds": 45.6
}
2. Sync Moderation
POST /api/v1/moderate

Request Body:

json
{
  "comment_id": "test_1",
  "text": "يوجد تسرب كبير في الماسورة"
}
Response:

json
{
  "comment_id": "test_1",
  "text": "يوجد تسرب كبير في الماسورة",
  "label": "Relevant",
  "confidence": 0.9974,
  "is_flagged": false,
  "processing_time_ms": 45.6,
  "timestamp": "2026-08-06T10:00:00.000000"
}
3. Async Moderation ⚡
POST /api/v1/moderate/async

Request Body:

json
{
  "comment_id": "test_2",
  "text": "اشترك في قناتي على يوتيوب"
}
Response (Immediate - ~10ms):

json
{
  "comment_id": "test_2",
  "status": "accepted",
  "message": "Comment submitted for async moderation"
}
The result will be available in results_queue after the worker processes it.

🔄 Async Moderation Flow
text
┌─────────────────────────────────────────────────────────────────────────────┐
│                           1. YOU SEND REQUEST                              │
│                    POST /api/v1/moderate/async                            │
│                    { "text": "يوجد تسرب كبير" }                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        2. API RETURNS IMMEDIATELY                         │
│                    { "status": "accepted",                                │
│                      "message": "Comment submitted" }                    │
│                    ⏱️ Response time: ~10ms                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        3. REQUEST GOES TO QUEUE                           │
│                    moderation_queue (RabbitMQ)                            │
│                    📥 Message: { "comment_id": "...", "text": "..." }     │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        4. WORKER PROCESSES                                │
│                    python -m moderation_service.workers.moderation_worker │
│                    🔄 Pops message from queue                             │
│                    🤖 Runs ML model (1-2 seconds)                        │
│                    📤 Pushes result to results_queue                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        5. RESULT IN RESULTS QUEUE                        │
│                    results_queue                                          │
│                    📤 Message: { "label": "Relevant", ... }              │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        6. YOU GET RESULT (Later)                         │
│                    Poll results_queue or use webhook                     │
│                    ✅ { "label": "Relevant", "confidence": 0.95 }        │
└─────────────────────────────────────────────────────────────────────────────┘
🧪 Testing the API
Using curl
1. Health Check
bash
curl http://localhost:8000/api/v1/health
2. Sync Moderation
bash
curl -X POST http://localhost:8000/api/v1/moderate \
  -H "Content-Type: application/json" \
  -d '{"comment_id": "test_1", "text": "يوجد تسرب كبير في الماسورة"}'
3. Async Moderation
bash
curl -X POST http://localhost:8000/api/v1/moderate/async \
  -H "Content-Type: application/json" \
  -d '{"comment_id": "test_2", "text": "اشترك في قناتي على يوتيوب"}'
Using PowerShell (Windows)
powershell
# Health Check
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/health"

# Sync Moderation
$body = '{"comment_id": "test_1", "text": "يوجد تسرب كبير في الماسورة"}'
Invoke-RestMethod -Method POST -Uri "http://localhost:8000/api/v1/moderate" -ContentType "application/json" -Body $body

# Async Moderation
$body = '{"comment_id": "test_2", "text": "اشترك في قناتي على يوتيوب"}'
Invoke-RestMethod -Method POST -Uri "http://localhost:8000/api/v1/moderate/async" -ContentType "application/json" -Body $body
Using Swagger UI
Open your browser: http://localhost:8000/docs

Find the endpoint you want to test

Click "Try it out"

Fill in the request body

Click "Execute"

Async vs Sync Comparison
Feature	Sync (/moderate)	Async (/moderate/async)
Response Time	~1-2 seconds	~10ms
Waits for Model	✅ Yes	❌ No
Returns Label	✅ Immediately	❌ Later
Best For	Real-time needs	High volume, background tasks
Scalability	Limited	✅ Highly scalable
🐳 Docker Deployment
Using Docker Compose
bash
# Build and start all services
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
Services
Service	Port	Description
RabbitMQ	5672	AMQP protocol
RabbitMQ UI	15672	Management UI
API Server	8000	FastAPI application
⚙️ Environment Variables
Variable	Description	Default
DEBUG	Enable debug mode	false
HOST	API host	0.0.0.0
PORT	API port	8000
MODEL_PATH	Path to model files	moderation_service/infrastructure/model/WAHA_KUN_AraBERT
MAX_SEQUENCE_LENGTH	Max tokens for model	128
DEVICE	CPU or CUDA	cpu
CONFIDENCE_THRESHOLD	Minimum confidence to flag	0.7
RABBITMQ_HOST	RabbitMQ host	localhost
RABBITMQ_PORT	RabbitMQ port	5672
RABBITMQ_USER	RabbitMQ username	guest
RABBITMQ_PASSWORD	RabbitMQ password	guest
RABBITMQ_QUEUE	Request queue name	moderation_queue
RABBITMQ_RESULTS_QUEUE	Results queue name	results_queue
LOG_LEVEL	Logging level	INFO
🔍 Monitoring
RabbitMQ Management UI
text
http://localhost:15672
Username: guest

Password: guest

Check Queues
bash
docker exec rabbitmq rabbitmqctl list_queues name messages_ready consumers
Check Queue Status
bash
docker exec rabbitmq rabbitmqctl list_queues
Expected Output:

text
moderation_queue    0    0    1
results_queue       1    0    0
📊 Supported Labels
Label	Description	Example
Relevant	Comments related to the topic	"يوجد تسرب كبير في الماسورة"
Spam	Promotional or misleading content	"اشترك في قناتي على يوتيوب"
Offensive	Insulting or aggressive language	"أنت غبي"
Irrelevant	Off-topic comments	"الجو جميل اليوم"
🧪 Sample Test Cases
bash
# Test 1: Relevant
curl -X POST http://localhost:8000/api/v1/moderate \
  -H "Content-Type: application/json" \
  -d '{"comment_id": "test_1", "text": "يوجد تسرب كبير في الماسورة"}'

# Test 2: Spam
curl -X POST http://localhost:8000/api/v1/moderate \
  -H "Content-Type: application/json" \
  -d '{"comment_id": "test_2", "text": "اشترك في قناتي على يوتيوب"}'

# Test 3: Offensive
curl -X POST http://localhost:8000/api/v1/moderate \
  -H "Content-Type: application/json" \
  -d '{"comment_id": "test_3", "text": "أنت غبي"}'

# Test 4: Irrelevant
curl -X POST http://localhost:8000/api/v1/moderate \
  -H "Content-Type": "application/json" \
  -d '{"comment_id": "test_4", "text": "الجو جميل اليوم"}'
📝 License
This project is licensed under the MIT License.

📧 Contact
Repository: graduation-project-ai-services

Branch: malak_ragab_dev

🙏 Acknowledgments
AraBERT - Arabic BERT model

FastAPI - Web framework

RabbitMQ - Message broker

Hugging Face Transformers - ML library

Happy Moderation! 🚀

text

---

## 📋 **Key Changes Made**

| Section | Before | After |
|---------|--------|-------|
| **Project Structure** | `app/` | `moderation_service/` |
| **Worker Command** | `python -m app.workers.moderation_worker` | `python -m moderation_service.workers.moderation_worker` |
| **API Command** | `uvicorn app.main:app` | `uvicorn moderation_service.main:app` |
| **Model Path** | `app/infrastructure/model/` | `moderation_service/infrastructure/model/` |
| **All Imports** | `from app.xxx` | `from moderation_service.xxx` |

---
