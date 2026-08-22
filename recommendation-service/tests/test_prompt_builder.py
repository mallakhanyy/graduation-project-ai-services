from application.services.prompt_builder_service import PromptBuilderService


def test_prompt_builder_contains_required_information():

    service = PromptBuilderService()

    query = "عندي مشكلة في تراكم المياه في الأرض"

    context = """
[Context 1]
Source: test.pdf
Page: 1
Text:
Drainage problems can cause water accumulation.
"""

    prompt = service.build(
        query=query,
        context=context,
        max_recommendations=3,
    )

    assert query in prompt

    assert "[Context 1]" in prompt
    assert "Source: test.pdf" in prompt
    assert "Page: 1" in prompt
    assert "Drainage problems can cause water accumulation." in prompt

    assert "ONLY valid JSON" in prompt
    assert "recommendation" in prompt
    assert "reasoning" in prompt
    assert "priority" in prompt
    assert "category" in prompt
    assert "confidence" in prompt

    assert "irrigation" in prompt
    assert "drainage" in prompt
    assert "water_quality" in prompt


def test_prompt_builder_respects_max_recommendations():

    service = PromptBuilderService()

    prompt = service.build(
        query="مشكلة في المياه",
        context="Some relevant agricultural context.",
        max_recommendations=2,
    )

    assert "at most 2" in prompt