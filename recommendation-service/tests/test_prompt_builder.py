from application.services.prompt_builder_service import (
    PromptBuilderService,
)


def main():

    service = PromptBuilderService()

    query = "عندي مشكلة في تراكم المياه في الأرض"

    context = """
[Context 1]
Source: test.pdf
Score: 0.83
Text:
Drainage problems can cause water accumulation.

[Context 2]
Source: test.pdf
Score: 0.67
Text:
Rainwater harvesting can reduce water waste.
"""

    prompt = service.build(
        query=query,
        context=context,
    )

    print("\nGenerated Prompt:\n")
    print(prompt)


if __name__ == "__main__":
    main()