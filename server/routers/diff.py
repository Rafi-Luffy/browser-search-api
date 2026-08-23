from typing import Any, Dict, List, Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field

from server.services.diff_service import diff_service

router = APIRouter(tags=["Change Tracking"])


class DiffRequest(BaseModel):
    previous: Dict[str, Any]
    current: Dict[str, Any]
    modes: Optional[List[str]] = Field(default_factory=lambda: ["gitDiff"])


@router.post("/v1/change-tracking/diff")
@router.post("/v1/diff")
@router.post("/diff")
async def change_tracking_diff(req: DiffRequest):
    return diff_service.compute_diff(
        previous=req.previous,
        current=req.current,
        modes=req.modes,
    )
