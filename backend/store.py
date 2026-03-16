"""
backend/store.py
JOBS dict with file persistence so jobs survive Render restarts.
"""
import json
import os
from typing import Any, Dict

JOBS: Dict[str, Dict[str, Any]] = {}
_PERSIST_FILE = "/tmp/adversense_jobs.json"


def save_job(job_id: str) -> None:
    """Save a single job to disk (without the agent object)."""
    try:
        job = JOBS.get(job_id, {})
        serializable = {k: v for k, v in job.items() if k != "agent"}
        data = {}
        try:
            with open(_PERSIST_FILE, "r") as f:
                data = json.load(f)
        except Exception:
            pass
        data[job_id] = serializable
        with open(_PERSIST_FILE, "w") as f:
            json.dump(data, f, default=str)
    except Exception as e:
        print(f"[store] save failed: {e}")


def load_jobs() -> None:
    """Load persisted jobs from disk on startup."""
    try:
        with open(_PERSIST_FILE, "r") as f:
            data = json.load(f)
        for job_id, job in data.items():
            JOBS[job_id] = job
        print(f"[store] loaded {len(data)} jobs from disk")
    except Exception:
        pass