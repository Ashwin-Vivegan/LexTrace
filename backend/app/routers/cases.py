import random
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status
from app.services.storage import db
from app.schemas import CaseCreate, CaseUpdate, CaseResponse, CasesListResponse

router = APIRouter(prefix="/cases", tags=["Cases"])

@router.get("", response_model=CasesListResponse)
def get_cases(
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    riskLevel: Optional[str] = Query(None)
):
    filtered = list(db.cases)

    if search:
        q = search.lower()
        filtered = [
            c for c in filtered
            if q in c["id"].lower()
            or q in c["title"].lower()
            or q in c["client"].lower()
            or q in c["type"].lower()
        ]

    if status and status != "All":
        filtered = [c for c in filtered if c["status"] == status]

    if riskLevel and riskLevel != "All":
        filtered = [c for c in filtered if c["riskLevel"] == riskLevel]

    return {
        "success": True,
        "count": len(filtered),
        "data": filtered
    }

@router.get("/{case_id}")
def get_case_by_id(case_id: str):
    case_item = next((c for c in db.cases if c["id"] == case_id), None)
    if not case_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case with ID {case_id} not found"
        )
    return {"success": True, "data": case_item}

@router.post("", status_code=status.HTTP_201_CREATED)
def create_case(payload: CaseCreate):
    new_case = {
        "id": f"CASE-2026-{random.randint(1000, 9999)}",
        "title": payload.title,
        "client": payload.client,
        "court": payload.court or "Standard Jurisdiction",
        "type": payload.type or "General Legal Trace",
        "status": payload.status or "In Review",
        "riskLevel": payload.riskLevel or "Medium",
        "complianceScore": payload.complianceScore or random.randint(70, 95),
        "leadCounsel": payload.leadCounsel or "Unassigned",
        "lastUpdated": datetime.now().isoformat(),
        "auditCount": 1,
        "summary": payload.summary or "Newly registered legal trace file."
    }
    db.cases.insert(0, new_case)
    return {"success": True, "data": new_case}

@router.patch("/{case_id}")
def update_case(case_id: str, payload: CaseUpdate):
    case_idx = next((i for i, c in enumerate(db.cases) if c["id"] == case_id), -1)
    if case_idx == -1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case with ID {case_id} not found"
        )
    
    update_data = payload.model_dump(exclude_unset=True)
    update_data["lastUpdated"] = datetime.now().isoformat()
    db.cases[case_idx].update(update_data)
    
    return {"success": True, "data": db.cases[case_idx]}

@router.delete("/{case_id}")
def delete_case(case_id: str):
    case_idx = next((i for i, c in enumerate(db.cases) if c["id"] == case_id), -1)
    if case_idx == -1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case with ID {case_id} not found"
        )
    
    deleted = db.cases.pop(case_idx)
    return {
        "success": True,
        "data": deleted,
        "message": f"Case {case_id} successfully archived/removed"
    }
