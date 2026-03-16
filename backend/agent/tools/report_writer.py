"""
Tool: append_finding
Logs a confirmed failure into the JOBS store.
Also exposes get_all_findings() and get_probe_count() for the agent and router.
"""
from __future__ import annotations

import json
import uuid
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List

from backend.store import JOBS

# per-job probe counter
_probe_counter: Dict[str, int] = defaultdict(int)
_active_job_id: str = ""


def set_active_job(job_id: str) -> None:
    global _active_job_id
    _active_job_id = job_id
    if job_id not in JOBS:
        JOBS[job_id] = {"findings": [], "log": [], "status": "running"}
    elif "findings" not in JOBS[job_id]:
        JOBS[job_id]["findings"] = []


def increment_probe_count(job_id: str, n: int = 1) -> None:
    _probe_counter[job_id] += n


def get_all_findings(job_id: str) -> List[Dict[str, Any]]:
    return JOBS.get(job_id, {}).get("findings", [])


def get_probe_count(job_id: str) -> int:
    return _probe_counter.get(job_id, 0)


def append_finding(
    probe: str,
    response: str,
    severity: str,
    reason: str,
    category: str = "unknown",
) -> str:
    """
    Log a confirmed failure finding for inclusion in the final audit report.

    Args:
        probe: The adversarial input that caused the failure.
        response: The raw model output.
        severity: critical, high, medium, or low.
        reason: Why this is a failure mode.
        category: The attack category that produced this finding.

    Returns:
        Confirmation string with finding ID.
    """
    finding_id = str(uuid.uuid4())[:8]
    finding = {
        "id": finding_id,
        "probe": probe,
        "response": response,
        "severity": severity.lower(),
        "reason": reason,
        "category": category,
        "timestamp": datetime.utcnow().isoformat(),
    }
    if _active_job_id and _active_job_id in JOBS:
        JOBS[_active_job_id]["findings"].append(finding)
    return f"Finding {finding_id} logged ({severity.upper()}) — category: {category}"


def get_findings_summary() -> str:
    """
    Return a JSON summary of all findings so far.
    Used by the agent to inform its next iteration strategy.
    """
    findings = get_all_findings(_active_job_id)
    by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    by_category: Dict[str, int] = {}

    for f in findings:
        sev = f.get("severity", "low")
        if sev in by_severity:
            by_severity[sev] += 1
        cat = f.get("category", "unknown")
        by_category[cat] = by_category.get(cat, 0) + 1

    return json.dumps({
        "total_findings": len(findings),
        "total_probes_sent": _probe_counter.get(_active_job_id, 0),
        "by_severity": by_severity,
        "by_category": by_category,
        "recent_findings": findings[-3:] if findings else [],
    }, default=str)