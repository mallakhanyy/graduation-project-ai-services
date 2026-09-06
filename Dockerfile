# ============================================
# Stage 1: Build Stage
# ============================================
FROM python:3.12-slim AS builder

# Set working directory
WORKDIR /app

# Install system dependencies required for Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ============================================
# Stage 2: Final Stage
# ============================================
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Create a non-root user for security
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/logs && \
    chown -R appuser:appuser /app

# Copy application code
# ========== CHANGE THIS ==========
COPY --chown=appuser:appuser moderation_service/ ./moderation_service/
# ========== INSTEAD OF ==========
# COPY --chown=appuser:appuser app/ ./app/

COPY --chown=appuser:appuser .env .env

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Expose port
EXPOSE 8000

# Default command (will be overridden for worker)
# ========== CHANGE THIS ==========
CMD ["uvicorn", "moderation_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
# ========== INSTEAD OF ==========
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]