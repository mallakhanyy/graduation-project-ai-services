def validate_caption(caption: str | None, min_words: int = 3, max_words: int = 60) -> str | None:
    """Return the cleaned caption, or None if it is empty, too short/long or degenerate."""
    if not caption:
        return None
    text = " ".join(caption.split())
    words = text.lower().split()
    if not (min_words <= len(words) <= max_words):
        return None
    # Reject repetitive generations such as "a plant plant plant plant".
    if len(set(words)) / len(words) < 0.5:
        return None
    return text
