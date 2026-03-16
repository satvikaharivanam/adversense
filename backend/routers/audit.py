from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import uuid

from backend.store import JOBS
from backend.agent.adversense_agent import create_audit_agent, run_audit_job
from backend.report.generator import generate_pdf_report

router = APIRouter(prefix="/audit")


class StartAuditRequest(BaseModel):
    model_url: str
    model_description: str
    model_type: str = "text_classifier"
    probe_depth: int = 2
    auth_header: Optional[str] = None

    model_config = {"protected_namespaces": ()}


@router.post("/")
async def start_audit(req: StartAuditRequest, bg: BackgroundTasks):
    job_id = str(uuid.uuid4())

    create_audit_agent(
        job_id=job_id,
        endpoint=req.model_url,
        model_description=req.model_description,
    )

    bg.add_task(run_audit_job, job_id)

    return {"job_id": job_id, "status": "queued", "message": "Audit started."}


@router.get("/{job_id}/status")
async def get_status(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found.")
    return {
        "job_id": job_id,
        "status": job.get("status", "unknown"),
        "findings_count": len(job.get("findings", [])),
        "error": job.get("error"),
    }


@router.get("/{job_id}/findings")
async def get_findings(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found.")
    return job.get("findings", [])


@router.get("/{job_id}/report")
async def get_report(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found.")
    if job.get("status") != "completed":
        raise HTTPException(status_code=202, detail="Audit not yet complete.")
    return job.get("report", {})


@router.get("/{job_id}/report/pdf")
async def get_report_pdf(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found.")
    if job.get("status") != "completed":
        raise HTTPException(status_code=202, detail="Audit not yet complete.")

    output_path = f"/tmp/adversense_{job_id}.pdf"
    generate_pdf_report(job.get("report", {}), output_path)

    return FileResponse(
        path=output_path,
        media_type="application/pdf",
        filename=f"adversense_report_{job_id}.pdf",
    )


@router.get("/{job_id}/log")
async def get_log(job_id: str, since: int = 0):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found.")
    log = job.get("log", [])
    return {"events": log[since:], "total": len(log)}