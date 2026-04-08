from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Any, Dict, Tuple

from fastapi import HTTPException

from app.core.config import get_config
from app.services import clue_repository


def _format_time(raw_time: str) -> str:
    try:
        return datetime.strptime(raw_time, "%Y%m%d_%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return str(raw_time or "")


def _build_submit_payload(raw: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    cfg = get_config()
    now = datetime.now()
    error_hb_id = uuid.uuid4().hex
    yehu_id = uuid.uuid4().hex
    question_data = [
        {
            "TJ_NAME": raw.get("TJ_NAME", ""),
            "TJ_CHECK_RESULT": cfg.commit.tj_check_result,
            "TJ_ID": "",
            "NEXT_LEVEL": [
                {
                    "VIOLATION_TYPE": raw.get("违法类型", ""),
                    "LOCATION": raw.get("发生地点", ""),
                    "VIOLATION_TIME": _format_time(str(raw.get("发生时间", ""))),
                    "IMAGE_PATH": raw.get("图片路径", ""),
                    "LEVEL": cfg.commit.level,
                }
            ],
        }
    ]
    return {
        "warns": {
            "ID": uuid.uuid4().hex,
            "ERROR_HB_ID": error_hb_id,
            "RULE_ID": raw.get("OffsiteRule_id", ""),
            "UNIT_CODE": raw.get("UNIT_CODE", ""),
            "TRADE": cfg.commit.trade,
            "DATA_SOURCE": cfg.commit.data_source,
            "YEHU_ID": yehu_id,
            "YEHU_NAME": cfg.commit.yehu_name,
            "FIND_TIME": now,
            "CREATE_TIME": now,
            "UPDATE_TIME": now,
            "IS_DEL": cfg.commit.is_del,
            "ERROR_NUM": 1,
        },
        "errors": {
            "ID": error_hb_id,
            "QUESTION_DATA": json.dumps(question_data, ensure_ascii=False),
            "EVIDENCE_TYPE": cfg.commit.evidence_type,
            "QUESTION_ID": raw.get("OffsiteRule_id", ""),
            "YEHU_ID": yehu_id,
            "CREATE_TIME": now,
            "UPDATE_TIME": now,
            "IS_DEL": cfg.commit.is_del,
        },
    }


def _insert_row(cursor: Any, schema: str, table: str, row: Dict[str, Any]) -> None:
    columns = list(row.keys())
    placeholders = ", ".join(["?"] * len(columns))
    sql = "INSERT INTO {schema}.{table} ({columns}) VALUES ({placeholders})".format(
        schema=schema,
        table=table,
        columns=", ".join(columns),
        placeholders=placeholders,
    )
    cursor.execute(sql, [row[c] for c in columns])


def _submit_to_dm(raw: Dict[str, Any]) -> None:
    cfg = get_config()
    try:
        import dmPython  # type: ignore
    except ImportError as exc:
        raise RuntimeError("未安装 dmPython，无法提交太极数据库") from exc

    if not cfg.taiji.password:
        raise RuntimeError("未配置 CLUE_TAIJI_DB_PASSWORD")

    payload = _build_submit_payload(raw)
    conn = dmPython.connect(
        user=cfg.taiji.user,
        password=cfg.taiji.password,
        server=cfg.taiji.host,
        port=cfg.taiji.port,
    )
    cursor = conn.cursor()
    try:
        _insert_row(cursor, cfg.taiji.schema, cfg.taiji.table_warns_hb, payload["warns"])
        _insert_row(cursor, cfg.taiji.schema, cfg.taiji.table_errors_hb, payload["errors"])
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def commit_one(clue_id: Any) -> Tuple[Any, int]:
    meta, raw = clue_repository.get_clue_raw(clue_id)
    if not raw:
        raise HTTPException(status_code=404, detail="线索不存在")
    if "is_committed" not in raw:
        raise HTTPException(status_code=400, detail="当前表缺少 is_committed 字段")
    if int(raw.get("is_committed") or 0) == 1:
        return raw.get(meta["pk_field"]), 1

    try:
        if get_config().commit.gateway == "dm":
            _submit_to_dm(raw)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"提交失败: {exc}") from exc

    clue_repository.mark_committed(clue_id, 1)
    return raw.get(meta["pk_field"]), 1

