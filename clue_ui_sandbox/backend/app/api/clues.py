from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.schemas.clues import ClueDetailResponse, ClueListResponse, CommitResponse
from app.services import clue_repository, commit_service

router = APIRouter(prefix="/api/clues", tags=["clues"])


@router.get("", response_model=ClueListResponse)
def get_clues(
    limit: int = Query(default=20, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    only_uncommitted: bool = Query(default=False),
    keyword: str = Query(default=""),
) -> ClueListResponse:
    meta, items = clue_repository.list_clues(
        limit=limit,
        offset=offset,
        only_uncommitted=only_uncommitted,
        keyword=keyword,
    )
    return ClueListResponse(total=meta["total"], items=items)


@router.get("/{clue_id}", response_model=ClueDetailResponse)
def get_clue_detail(clue_id: str) -> ClueDetailResponse:
    meta, raw = clue_repository.get_clue_raw(clue_id)
    if not raw:
        raise HTTPException(status_code=404, detail="线索不存在")
    return ClueDetailResponse(
        id=raw.get(meta["pk_field"]),
        model_output=str(raw.get("model_output") or ""),
        image_url=str(raw.get(meta["image_field"]) or ""),
        raw=raw,
    )


@router.post("/{clue_id}/commit", response_model=CommitResponse)
def commit_clue(clue_id: str) -> CommitResponse:
    pk, committed = commit_service.commit_one(clue_id)
    return CommitResponse(id=pk, success=True, message="提交成功", is_committed=committed)

