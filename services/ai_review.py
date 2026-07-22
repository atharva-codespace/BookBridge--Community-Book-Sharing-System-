"""
services/ai_review.py
Feature 3: AI Review Grammar Improvement. services/review_service.py calls
improve_review() on a user's raw review text before it is saved. The AI
(via the Gemini -> Groq -> OpenRouter -> Cerebras fallback chain in
ai_client.py) corrects grammar and spelling only - it must keep the
original meaning and sentiment, never exaggerate, never add compliments/
complaints that weren't there, and stay within 70 words. If every provider
is unavailable, the original review text is stored unchanged rather than
blocking the submission.
"""

from services.ai_client import ask_ai
from utils import ui

MAX_WORDS = 70

SYSTEM_PROMPT = f"""
You proofread a single book review for BookBridge.
Correct grammar and spelling only. Keep the original meaning and the exact
same sentiment (positive stays positive, negative stays negative, mixed
stays mixed) - do not exaggerate, do not add compliments or complaints that
weren't in the original, do not add new information. Keep the result to
{MAX_WORDS} words or fewer. Reply with ONLY the improved review text - no
quotes, no labels, no preamble.
""".strip()


def improve_review(raw_review: str) -> str:
    """
    Returns a grammar/spelling-corrected version of `raw_review`, preserving
    its original meaning and sentiment. Falls back to the original text
    unchanged if every AI provider is unavailable (missing API keys,
    timeouts, rate limits, network errors, etc.) so a review can always
    still be submitted.
    """
    if not raw_review or not raw_review.strip():
        return raw_review

    try:
        improved = ask_ai(SYSTEM_PROMPT, raw_review.strip(), max_tokens=150)
    except Exception as e:
        ui.warning(f"AI review improvement skipped: {e}")
        return raw_review

    if improved is None:
        return raw_review  # every provider unavailable - store the original text as-is

    # Safety net in case the AI doesn't fully honour the word-limit instruction.
    words = improved.split()
    if len(words) > MAX_WORDS:
        improved = " ".join(words[:MAX_WORDS])

    return improved
