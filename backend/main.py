from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from backend.routers.audit import router as audit_router
from backend.routers.ws import router as ws_router

load_dotenv()

app = FastAPI(title="AdverSense")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(audit_router)
app.include_router(ws_router)


@app.get("/")
def health():
    return {"status": "AdverSense backend ready – powered by Nova 2 Lite + Strands Agents"}