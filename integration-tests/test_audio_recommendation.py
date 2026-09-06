import sys
import time
from uuid import uuid4

import httpx


ASR_URL = "http://127.0.0.1:8001/api/v1/transcriptions"
RECOMMENDATION_URL = "http://127.0.0.1:8000/recommendations"


def main():
    # Replace this with a real MinIO audio URL
    audio_url = "http://localhost:9000/asr-audio/Test.ogg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=minioadmin%2F20260817%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20260817T152100Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=081f302ee68b04ad6dd28cdc5fbca461209334e967c0370670db5e70e0f5151a"
    extension = "ogg"

    request_id = str(uuid4())

    print("=" * 60)
    print("AUDIO → ASR → RECOMMENDATION INTEGRATION TEST")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. Send audio to ASR
    # ---------------------------------------------------------

    print("\n[1] Sending audio to ASR...")
    print(f"Request ID: {request_id}")
    print(f"Audio URL: {audio_url}")

    start = time.perf_counter()

    with httpx.Client(timeout=300.0) as client:
        response = client.post(
            ASR_URL,
            json={
                "request_id": request_id,
                "audio_url": audio_url,
                "extension": extension,
            },
        )

    asr_time = time.perf_counter() - start

    print(f"ASR HTTP status: {response.status_code}")
    print(f"ASR request time: {asr_time:.2f}s")

    response.raise_for_status()

    transcription = response.json()

    print("\nASR response:")
    print(transcription)

    # ---------------------------------------------------------
    # 2. Validate transcription
    # ---------------------------------------------------------

    if transcription.get("status") != "completed":
        raise RuntimeError(
            f"ASR failed: {transcription}"
        )

    text = transcription.get("text")

    if not text:
        raise RuntimeError(
            "ASR completed but returned empty transcription."
        )

    print("\nTranscription:")
    print(text)

    # ---------------------------------------------------------
    # 3. Send transcription to Recommendation Service
    # ---------------------------------------------------------

    print("\n[2] Sending transcription to Recommendation...")

    start = time.perf_counter()

    with httpx.Client(timeout=300.0) as client:
        response = client.post(
            RECOMMENDATION_URL,
            json={
                "query": text,
                "top_k": 5,
            },
        )

    recommendation_time = time.perf_counter() - start

    print(
        f"Recommendation HTTP status: "
        f"{response.status_code}"
    )

    print(
        f"Recommendation request time: "
        f"{recommendation_time:.2f}s"
    )

    response.raise_for_status()

    recommendations = response.json()

    # ---------------------------------------------------------
    # 4. Final result
    # ---------------------------------------------------------

    print("\n" + "=" * 60)
    print("FINAL RECOMMENDATION")
    print("=" * 60)

    print(recommendations)

    print("\n" + "=" * 60)
    print("INTEGRATION TEST PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()