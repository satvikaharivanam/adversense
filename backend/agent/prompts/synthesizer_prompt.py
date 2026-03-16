"""
Synthesizer prompt — fed to Nova 2 Lite after all probing is done.
"""
import json
from typing import Any, Dict, List


def build_synthesizer_prompt(
    model_description: str,
    total_probes: int,
    findings: List[Dict[str, Any]],
) -> str:
    findings_json = json.dumps(findings, indent=2, default=str)

    return f"""You are writing a robustness audit report. Return ONLY a JSON object, nothing else.

Model audited: {model_description}
Total probes sent: {total_probes}
Findings: {findings_json}

Return this exact JSON structure filled in with real content based on the findings above:

{{
  "executive_summary": "Write 2-3 sentences summarizing the audit results and overall risk level.",
  "attack_surface": [
    {{"category": "boundary_cases", "probes_sent": 3, "failures": 2}},
    {{"category": "negation", "probes_sent": 3, "failures": 1}},
    {{"category": "typos_noise", "probes_sent": 3, "failures": 2}},
    {{"category": "ood_inputs", "probes_sent": 3, "failures": 1}},
    {{"category": "empty_minimal", "probes_sent": 3, "failures": 3}}
  ],
  "severity_distribution": {{
    "critical": 0,
    "high": 0,
    "medium": 0,
    "low": 0
  }},
  "recommendations": [
    "First specific recommendation based on findings.",
    "Second specific recommendation based on findings.",
    "Third specific recommendation based on findings."
  ],
  "conclusion": "Write 1-2 sentences with overall robustness assessment.",
  "overall_grade": "C - Moderate Issues"
}}

Rules:
- Replace all placeholder values with real content based on the actual findings
- overall_grade must be one of: A - Robust, B - Mostly Robust, C - Moderate Issues, D - Significant Issues, F - Critical Failures
- severity_distribution counts must match the actual findings
- Return ONLY the JSON object, no markdown fences, no explanation
"""