from __future__ import annotations

from typing import List

from fastapi import APIRouter

from app.schemas.clues import (
    StatsGroupItem,
    StatsSummaryResponse,
    StatsTrendResponse,
    StatsTrendSeriesItem,
)
from app.services import clue_repository

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/summary", response_model=StatsSummaryResponse)
def get_summary() -> StatsSummaryResponse:
    return StatsSummaryResponse(**clue_repository.summary_stats())


@router.get("/by-violation", response_model=List[StatsGroupItem])
def get_by_violation() -> List[StatsGroupItem]:
    rows = clue_repository.group_stats("违法类型")
    return [StatsGroupItem(**x) for x in rows]


@router.get("/by-location", response_model=List[StatsGroupItem])
def get_by_location() -> List[StatsGroupItem]:
    rows = clue_repository.group_stats("发生地点")
    return [StatsGroupItem(**x) for x in rows]


@router.get("/trend-by-violation", response_model=StatsTrendResponse)
def get_trend_by_violation() -> StatsTrendResponse:
    payload = clue_repository.trend_by_violation()
    return StatsTrendResponse(
        dates=payload["dates"],
        series=[StatsTrendSeriesItem(**s) for s in payload["series"]],
    )

