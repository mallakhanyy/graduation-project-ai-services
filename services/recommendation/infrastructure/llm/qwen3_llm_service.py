import json

import httpx

from core.interfaces.llm_service import LLMService
from core.schemas.llm_recommendation_response import LLMRecommendationResponse
from shared.config import get_settings


class Qwen3LLMService(LLMService):

    def __init__(self):
        self.settings = get_settings()

    async def generate(
        self,
        prompt: str,
    ) -> LLMRecommendationResponse:

        payload = {
            "model": self.settings.LLM_MODEL_NAME,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "stream": False,
            "think": False,
            "options": {
                "temperature": self.settings.LLM_TEMPERATURE,
                "num_predict": self.settings.LLM_MAX_TOKENS,
            },
        }

        timeout = httpx.Timeout(
            connect=10.0,
            read=self.settings.LLM_TIMEOUT,
            write=10.0,
            pool=10.0,
        )

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{self.settings.LLM_BASE_URL}/api/chat",
                json=payload,
            )

            response.raise_for_status()

            data = response.json()

        content = data["message"]["content"]

        print("\n===== RAW LLM CONTENT =====")
        print(repr(content))
        print("============================\n")

        try:
            parsed_content = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "LLM returned invalid JSON"
            ) from exc

        return LLMRecommendationResponse.model_validate(parsed_content)