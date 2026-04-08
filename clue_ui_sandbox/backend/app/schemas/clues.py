from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel


class ClueListResponse(BaseModel):
    total: int
    items: List[Dict[str, Any]]


class ClueDetailResponse(BaseModel):
    id: Any
    model_output: str = ""
    image_url: str = ""
    raw: Dict[str, Any]


class CommitResponse(BaseModel):
    id: Any
    success: bool
    message: str
    is_committed: int


class StatsSummaryResponse(BaseModel):
    total: int
    uncommitted: int
    committed: int
    committed_rate: float


class StatsGroupItem(BaseModel):
    group_key: str
    total: int
    uncommitted: int
    committed: int
    committed_rate: float


class StatsTrendSeriesItem(BaseModel):
    name: str
    data: List[int]


class StatsTrendResponse(BaseModel):
    dates: List[str]
    series: List[StatsTrendSeriesItem]


class SchemaDetectResponse(BaseModel):
    db_path: str
    table: str
    pk_field: str
    image_field: str
    columns: List[str]
