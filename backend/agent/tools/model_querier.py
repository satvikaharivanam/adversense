"""
Tool: query_model
Sends a probe to the target model and returns its response as a string.
"""
from __future__ import annotations

import json
from typing import Any, Dict, Optional

import httpx

TIMEOUT_SECONDS = 10

_model_url: str = ""
_auth_header: Optional[str] = None
_model_type: str = "text_classifier"


def configure(model_url: str, auth_header: Optional[str], model_type: str) -> None:
    global _model_url, _auth_header, _model_type
    _model_url = model_url
    _auth_header = auth_header
    _model_type = model_type


def _headers() -> Dict[str, str]:
    h = {"Content-Type": "application/json"}
    if _auth_header:
        h["Authorization"] = _auth_header
    return h


def _payload(input_text: str) -> Dict[str, Any]:
    if _model_type == "llm_chat":
        return {"messages": [{"role": "user", "content": input_text}]}
    elif _model_type == "text_classifier":
        return {"inputs": input_text}
    return {"input": input_text}


def _parse(raw: Any) -> str:
    if isinstance(raw, list) and raw:
        inner = raw[0]
        if isinstance(inner, list) and inner and "label" in inner[0]:
            top = max(inner, key=lambda x: x.get("score", 0))
            return f"{top['label']} ({top['score']:.4f})"
        if isinstance(inner, dict) and "label" in inner:
            top = max(raw, key=lambda x: x.get("score", 0))
            return f"{top['label']} ({top['score']:.4f})"
        return json.dumps(raw)
    if isinstance(raw, dict):
        if "choices" in raw:
            try:
                return raw["choices"][0]["message"]["content"]
            except (KeyError, IndexError):
                pass
        if "output" in raw:
            return str(raw["output"])
        if "generated_text" in raw:
            return str(raw["generated_text"])
        if "error" in raw:
            return f"MODEL_ERROR: {raw['error']}"
        return json.dumps(raw)
    return str(raw)


def query_model(input_text: str) -> str:
    """
    Send a probe input to the target model and return its response.

    Args:
        input_text: The adversarial probe string to send.

    Returns:
        The model's response as a human-readable string.
    """
    if not _model_url:
        return "ERROR: query_model not configured."
    try:
        with httpx.Client(timeout=TIMEOUT_SECONDS) as client:
            resp = client.post(_model_url, json=_payload(input_text), headers=_headers())
        if resp.status_code != 200:
            return f"ERROR: HTTP {resp.status_code}: {resp.text[:200]}"
        return _parse(resp.json())
    except httpx.TimeoutException:
        return f"ERROR: Timed out after {TIMEOUT_SECONDS}s"
    except Exception as exc:
        return f"ERROR: {exc}"