"""OpenAI / Claude API abstraction. Returns 3 rephrased variants as a dict."""
import json
import re

SYSTEM_PROMPT = """You are a professional communication editor.

RULES:
1. Apply all 7 Cs: Clear, Concise, Concrete, Correct, Coherent, Complete, Courteous.
2. NEVER be verbose. Cut every filler word. If in doubt, cut it.
3. Preserve the original meaning exactly. Do not add information.
4. No emojis, hashtags, or informal punctuation.
5. Output ONLY valid JSON. No markdown fences, no commentary.

OUTPUT FORMAT (strict JSON, nothing else):
{"friendly": "...", "direct": "...", "business": "..."}

TONE DEFINITIONS:
- friendly: Warm, approachable, professional. Contractions are fine.
- direct: Blunt, no filler, action-first. Shortest of the three.
- business: Formal register, suitable for corporate email."""


class APIError(Exception):
    pass


def _parse(raw: str) -> dict:
    cleaned = re.sub(r"```(?:json)?\s*|\s*```", "", raw).strip()
    data = json.loads(cleaned)
    if not {"friendly", "direct", "business"}.issubset(data.keys()):
        raise ValueError("Missing required keys in API response")
    return {k: str(data[k]).strip() for k in ("friendly", "direct", "business")}


def get_rephrased(text: str, settings: dict) -> dict:
    """Call the configured API and return {'friendly': ..., 'direct': ..., 'business': ...}."""
    provider = settings.get("api_provider", "openai")
    user_message = f'Rephrase:\n"""\n{text}\n"""'

    try:
        if provider == "openai":
            return _call_openai(user_message, settings)
        else:
            return _call_claude(user_message, settings)
    except APIError:
        raise
    except Exception as e:
        raise APIError(str(e)) from e


def _call_openai(user_message: str, settings: dict) -> dict:
    import openai

    key = settings.get("openai_api_key", "").strip()
    if not key:
        raise APIError("no_key")

    client = openai.OpenAI(api_key=key, timeout=20)
    try:
        response = client.chat.completions.create(
            model=settings.get("openai_model", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            max_tokens=400,
            temperature=0.4,
        )
        raw = response.choices[0].message.content or ""
        return _parse(raw)
    except openai.AuthenticationError:
        raise APIError("invalid_key")
    except openai.RateLimitError as e:
        # OpenAI returns 429 for both rate limits AND insufficient credits
        body = getattr(e, "body", None) or {}
        code = (body.get("error") or {}).get("code", "") if isinstance(body, dict) else ""
        if code == "insufficient_quota" or "quota" in str(e).lower():
            raise APIError("no_credits")
        raise APIError("rate_limit")
    except openai.APITimeoutError:
        raise APIError("timeout")
    except (json.JSONDecodeError, ValueError):
        raise APIError("bad_response")


def _call_claude(user_message: str, settings: dict) -> dict:
    import anthropic

    key = settings.get("claude_api_key", "").strip()
    if not key:
        raise APIError("no_key")

    client = anthropic.Anthropic(api_key=key, timeout=20)
    try:
        response = client.messages.create(
            model=settings.get("claude_model", "claude-haiku-4-5-20251001"),
            max_tokens=400,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
        raw = response.content[0].text if response.content else ""
        return _parse(raw)
    except anthropic.AuthenticationError:
        raise APIError("invalid_key")
    except anthropic.RateLimitError:
        raise APIError("rate_limit")
    except anthropic.APITimeoutError:
        raise APIError("timeout")
    except (json.JSONDecodeError, ValueError):
        raise APIError("bad_response")
