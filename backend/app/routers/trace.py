import uuid
import hashlib
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Query, status
from app.services.storage import db
from app.schemas import TraceLogCreate, TraceLogListResponse

router = APIRouter(prefix="/trace", tags=["Trace Audit Logs"])

@router.get("", response_model=TraceLogListResponse)
def get_trace_logs(caseId: Optional[str] = Query(None)):
    logs = list(db.trace_logs)
    if caseId:
        logs = [l for l in logs if l.get("caseId") == caseId]
        
    return {
        "success": True,
        "count": len(logs),
        "data": logs
    }

@router.post("/log", status_code=status.HTTP_201_CREATED)
def create_trace_log(payload: TraceLogCreate):
    log_id = f"TRC-{uuid.uuid4().hex[:4].upper()}"
    log_hash = payload.hash or hashlib.sha256(f"{payload.action}{datetime.now()}".encode()).hexdigest()
    
    new_log = {
        "id": log_id,
        "timestamp": datetime.now().isoformat(),
        "action": payload.action,
        "caseId": payload.caseId,
        "caseTitle": payload.caseTitle or "Associated Case",
        "actor": payload.actor or "System AI Worker",
        "details": payload.details or "Trace log entry generated.",
        "hash": log_hash,
        "status": payload.status or "VERIFIED"
    }
    
    db.trace_logs.insert(0, new_log)
    return {"success": True, "data": new_log}
