FROM python:3.12-slim

# libsndfile is required by soundfile; ffmpeg covers the odd audio format
# the client sends despite the extension whitelist.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# NOTE — GPU deployment:
# The line below installs the CPU build of torch. For a CUDA box, replace
# it with (matching your driver, check with `nvidia-smi`):
#   RUN pip install --no-cache-dir torch==2.5.1 torchaudio==2.5.1 \
#       --index-url https://download.pytorch.org/whl/cu121
#   RUN pip install --no-cache-dir -r requirements.txt --no-deps
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]