# syntax=docker/dockerfile:1.6
FROM python:3.10-slim

WORKDIR /app

# ---- System dependencies -------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        curl \
        tini \
        libglib2.0-0 \
        libgl1 \
        libsm6 \
        libxext6 \
        libxrender1 \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# ---- Python dependencies (cached layer) ---------------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# ---- Application code ---------------------------------------------------
COPY . .

# ---- Runtime directories ------------------------------------------------
RUN mkdir -p uploads logs models

# ---- Entrypoint script must be executable -------------------------------
RUN chmod +x /app/docker/entrypoint.sh

# ---- Environment --------------------------------------------------------
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TF_CPP_MIN_LOG_LEVEL=2

# ---- Ports --------------------------------------------------------------
EXPOSE 8001 50051

# ---- Entrypoint ---------------------------------------------------------
# tini reaps zombies and forwards SIGTERM to the child processes.
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["sh", "/app/docker/entrypoint.sh"]