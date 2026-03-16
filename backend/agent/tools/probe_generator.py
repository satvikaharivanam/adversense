"""
Tool: generate_probes
Uses Nova 2 Lite to generate adversarial probe inputs for a given attack category.
"""
from __future__ import annotations

import json
import os

import boto3

_bedrock = None
_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0")

CATEGORY_DEFINITIONS = """
- boundary_cases: inputs right on the edge between two classes
- negation: logically negate clear-cut inputs (not, never, hardly, don't)
- typos_noise: realistic character-level errors — swaps, missing/extra letters
- semantic_shift: rephrase completely while preserving meaning
- ood_inputs: inputs outside training distribution — code, emojis, foreign text, math
- adversarial_phrases: append conjunctions like 'though'/'but' at end; passive voice
- long_context: pad with irrelevant filler, bury key content deep
- empty_minimal: empty string, single character, whitespace, single punctuation
""".strip()


def _get_bedrock():
    global _bedrock
    if _bedrock is None:
        _bedrock = boto3.client(
            "bedrock-runtime",
            region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
        )
    return _bedrock


def generate_probes(category: str, model_description: str, n: int = 5) -> str:
    """
    Generate adversarial probe inputs for a given attack category.

    Args:
        category: Attack category name (e.g. 'negation', 'typos_noise').
        model_description: What the target model does.
        n: Number of probes to generate.

    Returns:
        A JSON array string of probe strings.
    """
    prompt = f"""Generate {n} adversarial test inputs for an ML robustness audit.

Target model: {model_description}
Attack category: {category}

Category definitions:
{CATEGORY_DEFINITIONS}

Generate exactly {n} diverse probe strings for category "{category}".
Return ONLY a valid JSON array of {n} strings. No explanation, no markdown.
Example: ["probe one", "probe two", "probe three"]"""

    response = _get_bedrock().converse(
        modelId=_MODEL_ID,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": 512, "temperature": 0.9},
    )

    raw = response["output"]["message"]["content"][0]["text"].strip()

    # Strip markdown fences
    if raw.startswith("```"):
        raw = "\n".join(
            l for l in raw.splitlines() if not l.strip().startswith("```")
        ).strip()

    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return json.dumps(parsed)
    except json.JSONDecodeError:
        pass

    return raw