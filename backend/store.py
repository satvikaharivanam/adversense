"""
backend/store.py
Single in-memory JOBS dict shared by the agent, tools, and routers.
Import JOBS from here — never define it in two places.
"""
from typing import Any, Dict

# job_id → {
#   endpoint, model_description, status, findings, log, report, agent
# }
JOBS: Dict[str, Dict[str, Any]] = {}