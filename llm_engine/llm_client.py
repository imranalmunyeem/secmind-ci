import os
import json
import urllib.request

class LLMError(Exception):
    pass

def call_llm(prompt: str) -> str:
    """
    Minimal LLM call wrapper.
    You must set LLM_API_KEY in environment.
    Replace API_URL / payload format for your provider.
    """
    api_key = os.environ.get("LLM_API_KEY")
    if not api_key:
        raise LLMError("Missing LLM_API_KEY env var (set it in GitHub Secrets).")

    # ---- IMPORTANT ----
    # This is a TEMPLATE. Different providers have different endpoints/payloads.
    # If you're using OpenAI, tell me which API style you're using and I'll paste
    # the exact working code for it.
    # -------------------
    api_url = os.environ.get("LLM_API_URL")
    if not api_url:
        raise LLMError("Missing LLM_API_URL env var. Set it in workflow env (provider endpoint).")

    payload = {
        "prompt": prompt,
        "max_tokens": 700
    }

    req = urllib.request.Request(
        api_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        raise LLMError(f"LLM request failed: {e}")

    # Provider-specific parsing:
    # For a generic service, we expect {"text": "...python..."}
    try:
        data = json.loads(body)
        text = data.get("text")
        if not text:
            raise LLMError(f"Unexpected LLM response: {body[:300]}")
        return text
    except json.JSONDecodeError:
        raise LLMError(f"Non-JSON response from LLM: {body[:300]}")
