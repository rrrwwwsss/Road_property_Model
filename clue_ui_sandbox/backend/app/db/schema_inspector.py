from __future__ import annotations

from dataclasses import dataclass
from typing import List

from app.core.config import get_config
from app.db.sqlite_client import get_conn


@dataclass(frozen=True)
class TableSchema:
    table: str
    columns: List[str]
    pk_field: str
    image_field: str


def detect_schema() -> TableSchema:
    cfg = get_config()
    table = cfg.sqlite.table
    with get_conn() as conn:
        rows = conn.execute(f"PRAGMA table_info('{table}')").fetchall()
    columns = [r["name"] for r in rows]
    if not columns:
        raise RuntimeError(f"数据表不存在或无字段: {table}")
    return TableSchema(
        table=table,
        columns=columns,
        pk_field=cfg.sqlite.pk_field,
        image_field=cfg.sqlite.image_field,
    )

