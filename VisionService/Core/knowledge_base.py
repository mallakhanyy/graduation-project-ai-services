"""
Knowledge base for recommendations.

The problem type is already known (from the model), so we simply look it up
directly in PROBLEM_INFO. No fuzzy search is required.
"""

from typing import Any, Dict, Optional

from .problem_info import PROBLEM_INFO


def get_knowledge_recommendation(
    problem_type: str,
    confidence: float,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Return the recommendation for a problem type.

    Args:
        problem_type: One of "Pipe_Damage", "Overflow", "Blockage"
        confidence: Model confidence (0-100). Currently unused, kept for
                    API compatibility with callers.
        context: Optional context (weather, location, ...). Currently
                 unused — the pipeline defaults are applied elsewhere.

    Returns:
        {
            "arabic":         str,   # Arabic display name
            "recommendation": str,   # Short recommendation paragraph
            "explanation":    str,   # Explanation paragraph
            "steps":          list,  # Ordered repair steps
            "sources":        list,  # Empty (kept for API compatibility)
            "generated":      bool,  # Always False — no LLM used
        }
    """
    info = PROBLEM_INFO.get(problem_type, {})
    return {
        "arabic": info.get("arabic", problem_type),
        "recommendation": info.get("recommendation", ""),
        "explanation": info.get("explanation", "").strip(),
        "steps": info.get("steps", []),
        "sources": [],
        "generated": False,
    }