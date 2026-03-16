import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.store import JOBS

router = APIRouter()


@router.websocket("/ws/audit/{job_id}/stream")
async def audit_stream(websocket: WebSocket, job_id: str):
    await websocket.accept()
    cursor = 0

    try:
        # Replay any events that happened before the WS connected
        job = JOBS.get(job_id, {})
        existing = job.get("log", [])
        for event in existing:
            await websocket.send_json(event)
        cursor = len(existing)

        # Stream new events as they arrive
        while True:
            job = JOBS.get(job_id, {})
            log = job.get("log", [])

            if len(log) > cursor:
                for event in log[cursor:]:
                    await websocket.send_json(event)
                cursor = len(log)

            status = job.get("status", "")
            if status in ("completed", "failed"):
                break

            await asyncio.sleep(0.5)

    except WebSocketDisconnect:
        pass