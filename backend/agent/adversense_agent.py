"""
AdverSense Agent — pure Bedrock Converse API tool-use loop.
No Strands dependency. Nova 2 Lite drives the entire audit autonomously.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List

import boto3

from backend.store import JOBS
from backend.agent.prompts.planner_prompt import PLANNER_SYSTEM_PROMPT
from backend.agent.prompts.synthesizer_prompt import build_synthesizer_prompt
from backend.agent.tools.model_querier import configure as configure_querier, query_model
from backend.agent.tools.probe_generator import generate_probes
from backend.agent.tools.response_scorer import score_response
from backend.agent.tools.report_writer import (
    append_finding,
    get_all_findings,
    get_findings_summary,
    get_probe_count,
    increment_probe_count,
    set_active_job,
)

logger = logging.getLogger(__name__)
MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0")
MAX_ITERATIONS = int(os.getenv("MAX_PROBE_ITERATIONS", "3"))

# ---------------------------------------------------------------------------
# Tool registry
# ---------------------------------------------------------------------------

TOOL_REGISTRY = {
    "generate_probes":      generate_probes,
    "query_model":          query_model,
    "score_response":       score_response,
    "append_finding":       append_finding,
    "get_findings_summary": get_findings_summary,
}

# ---------------------------------------------------------------------------
# Bedrock tool spec
# ---------------------------------------------------------------------------

TOOL_CONFIG = {
    "tools": [
        {
            "toolSpec": {
                "name": "generate_probes",
                "description": "Generate adversarial probe inputs for a given attack category.",
                "inputSchema": {"json": {
                    "type": "object",
                    "properties": {
                        "category":          {"type": "string", "description": "Attack category: boundary_cases, negation, typos_noise, semantic_shift, ood_inputs, adversarial_phrases, long_context, empty_minimal"},
                        "model_description": {"type": "string", "description": "What the target model does"},
                        "n":                 {"type": "integer", "description": "Number of probes to generate (default 5)"}
                    },
                    "required": ["category", "model_description"]
                }}
            }
        },
        {
            "toolSpec": {
                "name": "query_model",
                "description": "Send a probe input to the target model and return its response.",
                "inputSchema": {"json": {
                    "type": "object",
                    "properties": {
                        "input_text": {"type": "string", "description": "The probe text to send"}
                    },
                    "required": ["input_text"]
                }}
            }
        },
        {
            "toolSpec": {
                "name": "score_response",
                "description": "Evaluate whether a model response is a failure mode. Returns JSON with is_failure, severity, reason.",
                "inputSchema": {"json": {
                    "type": "object",
                    "properties": {
                        "probe":             {"type": "string", "description": "The input sent to the model"},
                        "model_response":    {"type": "string", "description": "What the model returned"},
                        "model_description": {"type": "string", "description": "What the target model does"}
                    },
                    "required": ["probe", "model_response", "model_description"]
                }}
            }
        },
        {
            "toolSpec": {
                "name": "append_finding",
                "description": "Log a confirmed failure finding for the audit report.",
                "inputSchema": {"json": {
                    "type": "object",
                    "properties": {
                        "probe":    {"type": "string", "description": "The adversarial input"},
                        "response": {"type": "string", "description": "The model output"},
                        "severity": {"type": "string", "description": "critical, high, medium, or low"},
                        "reason":   {"type": "string", "description": "Why this is a failure"},
                        "category": {"type": "string", "description": "Attack category"}
                    },
                    "required": ["probe", "response", "severity", "reason"]
                }}
            }
        },
        {
            "toolSpec": {
                "name": "get_findings_summary",
                "description": "Get a JSON summary of all findings so far. Call this to inform your next strategy.",
                "inputSchema": {"json": {"type": "object", "properties": {}}}
            }
        },
    ]
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _emit(job_id: str, payload: dict) -> None:
    payload.setdefault("ts", datetime.utcnow().isoformat())
    if job_id in JOBS:
        JOBS[job_id].setdefault("log", []).append(payload)


def _execute_tool(job_id: str, tool_name: str, tool_input: dict) -> str:
    _emit(job_id, {"type": "tool_call", "tool": tool_name, "input": tool_input})

    func = TOOL_REGISTRY.get(tool_name)
    if func is None:
        return f"ERROR: Unknown tool '{tool_name}'"
    try:
        result = func(**tool_input)
        if tool_name == "query_model":
            increment_probe_count(job_id)
        if tool_name == "append_finding":
            _emit(job_id, {"type": "finding", "text": str(result)})
    except Exception as exc:
        result = f"ERROR: {exc}"

    result_str = str(result) if not isinstance(result, str) else result
    _emit(job_id, {"type": "tool_result", "tool": tool_name, "result": result_str[:300]})
    return result_str


def _run_turn(
    job_id: str,
    bedrock: Any,
    messages: List[dict],
    system_prompt: str,
    max_tool_rounds: int = 40,
) -> List[dict]:
    for _ in range(max_tool_rounds):
        response = bedrock.converse(
            modelId=MODEL_ID,
            system=[{"text": system_prompt}],
            messages=messages,
            toolConfig=TOOL_CONFIG,
            inferenceConfig={"maxTokens": 4096, "temperature": 0.4},
        )

        output_message = response["output"]["message"]
        messages.append(output_message)
        stop_reason = response.get("stopReason", "")

        for block in output_message.get("content", []):
            if "text" in block:
                _emit(job_id, {"type": "reasoning", "text": block["text"]})

        if stop_reason != "tool_use":
            break

        tool_results = []
        for block in output_message.get("content", []):
            if "toolUse" in block:
                tu = block["toolUse"]
                result_str = _execute_tool(job_id, tu["name"], tu.get("input", {}))
                tool_results.append({
                    "toolResult": {
                        "toolUseId": tu["toolUseId"],
                        "content": [{"text": result_str}],
                    }
                })

        if tool_results:
            messages.append({"role": "user", "content": tool_results})

    return messages


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def create_audit_agent(job_id: str, endpoint: str, model_description: str) -> None:
    hf_token = os.getenv("HF_TOKEN", "")
    configure_querier(
        model_url=endpoint,
        auth_header=f"Bearer {hf_token}" if hf_token else None,
        model_type="text_classifier",
    )
    JOBS[job_id] = {
        "endpoint": endpoint,
        "model_description": model_description,
        "status": "queued",
        "findings": [],
        "log": [],
        "report": None,
    }


async def run_audit_job(job_id: str) -> None:
    job = JOBS.get(job_id)
    if not job:
        logger.error("run_audit_job: job %s not found", job_id)
        return

    model_description: str = job["model_description"]
    job["status"] = "running"
    set_active_job(job_id)

    _emit(job_id, {"type": "start", "text": f"Audit started — {model_description}"})

    system_prompt = PLANNER_SYSTEM_PROMPT.format(
        model_description=model_description,
        endpoint=job["endpoint"],
    )

    try:
        bedrock = boto3.client(
            "bedrock-runtime",
            region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
        )

        messages: List[dict] = []

        for i in range(MAX_ITERATIONS):
            iteration_num = i + 1
            _emit(job_id, {
                "type": "iteration_start",
                "text": f"Starting iteration {iteration_num}/{MAX_ITERATIONS}",
                "iteration": iteration_num,
            })

            summary = get_findings_summary()
            instruction = (
                f"Iteration {iteration_num}/{MAX_ITERATIONS}. "
                + ("Explore broadly — send 2-3 probes across ALL attack categories. "
                   if i == 0 else
                   "Focus on categories that produced failures. Go deeper. ")
                + f"Current findings: {summary}"
            )

            messages.append({"role": "user", "content": [{"text": instruction}]})

            loop = asyncio.get_event_loop()
            messages = await loop.run_in_executor(
                None,
                lambda m=messages: _run_turn(job_id, bedrock, m, system_prompt),
            )

            _emit(job_id, {
                "type": "iteration_complete",
                "text": f"Iteration {iteration_num} complete.",
                "iteration": iteration_num,
            })

        # Synthesis
        _emit(job_id, {"type": "reasoning", "text": "Synthesising findings into report…"})

        findings = get_all_findings(job_id)
        total_probes = get_probe_count(job_id)

        synth_response = bedrock.converse(
            modelId=MODEL_ID,
            messages=[{"role": "user", "content": [{"text": build_synthesizer_prompt(
                model_description=model_description,
                total_probes=total_probes,
                findings=findings,
            )}]}],
            inferenceConfig={"maxTokens": 2048, "temperature": 0.2},
        )
        raw = synth_response["output"]["message"]["content"][0]["text"].strip()

        if raw.startswith("```"):
            raw = "\n".join(l for l in raw.splitlines() if not l.strip().startswith("```")).strip()

        try:
            report = json.loads(raw)
        except json.JSONDecodeError:
            report = {
                "executive_summary": "Synthesis failed — see raw findings.",
                "findings": findings,
                "recommendations": [],
                "severity_distribution": {},
                "conclusion": "Synthesis error.",
                "overall_grade": "N/A",
            }

        report.update({
            "model_description": model_description,
            "model_url": job["endpoint"],
            "audit_date": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
            "total_probes": total_probes,
            "job_id": job_id,
        })

        job["report"] = report
        job["status"] = "completed"
        job["findings"] = findings
        print(f"[DONE] job {job_id} complete. report keys: {list(report.keys())}, findings: {len(findings)}")

        _emit(job_id, {
            "type": "complete",
            "text": f"Audit complete. {len(findings)} findings across {total_probes} probes.",
            "findings_count": len(findings),
            "overall_grade": report.get("overall_grade", "N/A"),
        })

    except Exception as exc:
        logger.exception("Audit %s failed: %s", job_id, exc)
        job["status"] = "failed"
        job["error"] = str(exc)
        _emit(job_id, {"type": "error", "text": f"Audit failed: {exc}"})