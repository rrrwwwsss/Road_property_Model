from __future__ import annotations

from fastapi import APIRouter

from app.core.config import get_config
from app.db.schema_inspector import detect_schema
from app.schemas.clues import SchemaDetectResponse

router = APIRouter(prefix="/api/meta", tags=["meta"])


@router.get("/schema", response_model=SchemaDetectResponse)
def get_schema() -> SchemaDetectResponse:
    cfg = get_config()
    schema = detect_schema()
    return SchemaDetectResponse(
        db_path=cfg.sqlite.db_path,
        table=schema.table,
        pk_field=schema.pk_field,
        image_field=schema.image_field,
        columns=schema.columns,
    )
