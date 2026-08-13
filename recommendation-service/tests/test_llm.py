import asyncio

from infrastructure.llm.qwen3_llm_service import Qwen3LLMService


async def main():

    llm_service = Qwen3LLMService()

    prompt = """
    عندي مشكلة في تراكم المياه في الأرض.

    أجب بالعربية في نقاط واضحة.
    لكل خطوة اشرح لماذا هي مهمة.
    """

    response = await llm_service.generate(prompt)

    print("\nGenerated Response:\n")
    print(response)


if __name__ == "__main__":
    asyncio.run(main())