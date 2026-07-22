"""
services/ai_client.py
Shared helper for every AI-powered feature (AI Project Assistant, AI Book
Recommendation, AI Review Grammar Improvement). Centralizes:
  - Reading each provider's API key/model from a .env file at the project root
  - A single ask_ai() call that tries multiple free-tier AI providers in a
    fixed priority order, automatically moving to the next provider whenever
    the current one is unavailable, rate-limited, or out of quota:
        1. Gemini (Google)
        2. Groq
        3. OpenRouter
        4. Cerebras
    so ai_chatbot.py / ai_recommendation.py / ai_review.py never duplicate
    this plumbing and the app keeps working even if one or more providers
    have hit their free-tier limits for the day.

Every AI feature in this project is a convenience layer on top of the CLI,
never a hard requirement - so ask_ai() always returns None (instead of
raising) once ALL providers have failed, and every caller falls back to a
safe, non-AI behaviour.
"""

import os

import requests
from dotenv import load_dotenv

load_dotenv()  # loads every *_API_KEY below from a .env file at the project root

# ==================== PROVIDER CONFIGURATION ====================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")

# Model names are configurable via .env since free-tier model availability
# changes over time on each provider's side - update these if a default
# model is ever retired.
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.1-8b-instruct:free")
CEREBRAS_MODEL = os.getenv("CEREBRAS_MODEL", "llama3.1-8b")

AI_TIMEOUT_SECONDS = float(os.getenv("AI_TIMEOUT_SECONDS", "20"))

FALLBACK_MESSAGE = (
    "AI features are temporarily unavailable right now (all configured AI "
    "providers failed or are out of quota). Please try again later - you "
    "can keep using the rest of the system normally."
)


class ProviderError(Exception):
    """Raised internally when a single provider call fails for any reason -
    missing/invalid API key, HTTP 429 (rate limit / quota exceeded), any
    other HTTP error, or an unexpected response shape - so ask_ai() knows to
    move on to the next provider in the chain instead of giving up."""


# ==================== INDIVIDUAL PROVIDER CALLS ====================
def _raise_for_provider_status(response, provider_name):
    """Turns a non-2xx HTTP response into a ProviderError, calling out rate
    limit / quota errors (429) specifically since that's the main trigger
    for falling back to the next provider."""
    if response.status_code == 429:
        raise ProviderError()#f"{provider_name} rate limit / quota exceeded (HTTP 429)."
    if response.status_code >= 400:
        raise ProviderError(
            f"{provider_name} returned HTTP {response.status_code}: {response.text[:200]}"
        )


def _call_gemini(system_prompt, user_prompt, max_tokens):
    """Google Gemini via the plain REST API (no extra SDK dependency)."""
    if not GEMINI_API_KEY:
        raise ProviderError("GEMINI_API_KEY is not configured.")

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    )
    payload = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
        "generationConfig": {"maxOutputTokens": max_tokens},
    }

    response = requests.post(url, json=payload, timeout=AI_TIMEOUT_SECONDS)
    _raise_for_provider_status(response, "Gemini")

    try:
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError, ValueError) as e:
        raise ProviderError(f"Unexpected Gemini response shape: {e}")


def _call_openai_compatible(provider_name, base_url, api_key, model,
                             system_prompt, user_prompt, max_tokens, extra_headers=None):
    """Groq, OpenRouter, and Cerebras all expose an OpenAI-compatible
    /chat/completions endpoint, so one helper covers all three."""
    if not api_key:
        raise ProviderError(f"{provider_name} API key is not configured.")

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    if extra_headers:
        headers.update(extra_headers)

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": max_tokens,
    }

    response = requests.post(
        f"{base_url}/chat/completions", json=payload, headers=headers, timeout=AI_TIMEOUT_SECONDS,
    )
    _raise_for_provider_status(response, provider_name)

    try:
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, ValueError) as e:
        raise ProviderError(f"Unexpected {provider_name} response shape: {e}")


def _call_groq(system_prompt, user_prompt, max_tokens):
    return _call_openai_compatible(
        "Groq", "https://api.groq.com/openai/v1", GROQ_API_KEY, GROQ_MODEL,
        system_prompt, user_prompt, max_tokens,
    )


def _call_openrouter(system_prompt, user_prompt, max_tokens):
    return _call_openai_compatible(
        "OpenRouter", "https://openrouter.ai/api/v1", OPENROUTER_API_KEY, OPENROUTER_MODEL,
        system_prompt, user_prompt, max_tokens,
        # OpenRouter asks for these two optional headers to identify the app.
        extra_headers={
            "HTTP-Referer": "https://localhost/bookbridge",
            "X-Title": "BookBridge",
        },
    )


def _call_cerebras(system_prompt, user_prompt, max_tokens):
    return _call_openai_compatible(
        "Cerebras", "https://api.cerebras.ai/v1", CEREBRAS_API_KEY, CEREBRAS_MODEL,
        system_prompt, user_prompt, max_tokens,
    )


# Priority order for the fallback chain: Gemini -> Groq -> OpenRouter -> Cerebras.
PROVIDERS = [
    ("Gemini", _call_gemini),
    ("Groq", _call_groq),
    ("OpenRouter", _call_openrouter),
    ("Cerebras", _call_cerebras),
]


# ==================== PUBLIC ENTRY POINT ====================
def ask_ai(system_prompt: str, user_prompt: str, max_tokens: int = 400):
    """
    Tries each configured AI provider in priority order - Gemini, then Groq,
    then OpenRouter, then Cerebras - and returns the first successful reply.
    Whenever a provider is not configured, rate-limited/out of quota, times
    out, or errors in any other way, it is skipped and the next one in the
    chain is tried automatically. Returns None only if every single provider
    fails, in which case callers must fall back to their own non-AI
    behaviour (see FALLBACK_MESSAGE above).
    """
    for name, call_fn in PROVIDERS:
        try:
            reply = call_fn(system_prompt, user_prompt, max_tokens)
            if reply:
                return reply
        except ProviderError as e:
            pass  # print(f"[AI WARNING] {name} unavailable, trying next provider: {e}")
        except requests.exceptions.Timeout:
            pass  # print(f"[AI WARNING] {name} request timed out, trying next provider.")
        except requests.exceptions.RequestException as e:
            pass  # print(f"[AI WARNING] {name} network error, trying next provider: {e}")
        except Exception as e:
            pass  # print(f"[AI WARNING] Unexpected error from {name}, trying next provider: {e}")

    # print("[AI WARNING] All configured AI providers are unavailable.")
    return None
