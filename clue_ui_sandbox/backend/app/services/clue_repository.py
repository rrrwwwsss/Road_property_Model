from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from app.db.schema_inspector import detect_schema
from app.db.sqlite_client import get_conn

LIST_EXCLUDE_COLUMNS = {"model_output", "OffsiteRule_id", "TJ_NAME"}


def _quote(name: str) -> str:
    return f"\"{name}\""


def _list_columns(schema_columns: List[str], image_field: str) -> List[str]:
    return [c for c in schema_columns if c not in LIST_EXCLUDE_COLUMNS and c != image_field]


def list_clues(
    limit: int = 20,
    offset: int = 0,
    only_uncommitted: bool = False,
    keyword: str = "",
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    schema = detect_schema()
    columns = _list_columns(schema.columns, schema.image_field)
    select_cols = ", ".join(_quote(c) for c in columns)
    where_parts: List[str] = []
    params: List[Any] = []
    if only_uncommitted:
        where_parts.append("\"is_committed\" = 0")
    if keyword.strip():
        kw = f"%{keyword.strip()}%"
        where_parts.append("(\"工单编号\" LIKE ? OR \"违法类型\" LIKE ? OR \"发生地点\" LIKE ?)")
        params.extend([kw, kw, kw])

    where_sql = f" WHERE {' AND '.join(where_parts)}" if where_parts else ""
    list_sql = (
        f"SELECT {select_cols} FROM \"{schema.table}\"{where_sql} "
        f"ORDER BY {_quote(schema.pk_field)} DESC LIMIT ? OFFSET ?"
    )
    count_sql = f"SELECT COUNT(*) AS cnt FROM \"{schema.table}\"{where_sql}"

    with get_conn() as conn:
        total = conn.execute(count_sql, params).fetchone()["cnt"]
        rows = conn.execute(list_sql, [*params, limit, offset]).fetchall()

    meta = {"total": int(total or 0)}
    return meta, [dict(row) for row in rows]


def get_clue_raw(clue_id: Any) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
    schema = detect_schema()
    sql = f"SELECT * FROM \"{schema.table}\" WHERE {_quote(schema.pk_field)} = ? LIMIT 1"
    with get_conn() as conn:
        row = conn.execute(sql, (clue_id,)).fetchone()
    meta = {"table": schema.table, "pk_field": schema.pk_field, "image_field": schema.image_field}
    return meta, (dict(row) if row else None)


def mark_committed(clue_id: Any, committed: int) -> None:
    schema = detect_schema()
    sql = f"UPDATE \"{schema.table}\" SET \"is_committed\" = ? WHERE {_quote(schema.pk_field)} = ?"
    with get_conn() as conn:
        conn.execute(sql, (committed, clue_id))
        conn.commit()


def summary_stats() -> Dict[str, Any]:
    schema = detect_schema()
    with get_conn() as conn:
        row = conn.execute(
            f"""
            SELECT
              COUNT(*) AS total,
              SUM(CASE WHEN is_committed = 0 THEN 1 ELSE 0 END) AS uncommitted,
              SUM(CASE WHEN is_committed = 1 THEN 1 ELSE 0 END) AS committed
            FROM "{schema.table}"
            """
        ).fetchone()
    total = int(row["total"] or 0)
    committed = int(row["committed"] or 0)
    uncommitted = int(row["uncommitted"] or 0)
    rate = round((committed / total) * 100, 1) if total else 0.0
    return {"total": total, "uncommitted": uncommitted, "committed": committed, "committed_rate": rate}


def group_stats(group_field: str) -> List[Dict[str, Any]]:
    schema = detect_schema()
    preferred_map = {
        "违法类型": ["违法类型", "WEIFA_TYPE"],
        "发生地点": ["发生地点", "LOCATION"],
    }
    actual_group_field = group_field
    if group_field in preferred_map:
        for candidate in preferred_map[group_field]:
            if candidate in schema.columns:
                actual_group_field = candidate
                break
    if actual_group_field not in schema.columns:
        return []
    sql = (
        f"SELECT COALESCE({_quote(actual_group_field)}, '未标注') AS group_key, "
        "COUNT(*) AS total, "
        "SUM(CASE WHEN is_committed = 0 THEN 1 ELSE 0 END) AS uncommitted, "
        "SUM(CASE WHEN is_committed = 1 THEN 1 ELSE 0 END) AS committed "
        f"FROM \"{schema.table}\" GROUP BY {_quote(actual_group_field)} "
        "ORDER BY uncommitted DESC, total DESC"
    )
    with get_conn() as conn:
        rows = conn.execute(sql).fetchall()
    result: List[Dict[str, Any]] = []
    for row in rows:
        total = int(row["total"] or 0)
        committed = int(row["committed"] or 0)
        rate = round((committed / total) * 100, 1) if total else 0.0
        result.append(
            {
                "group_key": str(row["group_key"]),
                "total": total,
                "uncommitted": int(row["uncommitted"] or 0),
                "committed": committed,
                "committed_rate": rate,
            }
        )
    return result


def trend_by_violation() -> Dict[str, Any]:
    schema = detect_schema()
    violation_col = "违法类型" if "违法类型" in schema.columns else None
    time_col = "发生时间" if "发生时间" in schema.columns else None
    if not violation_col or not time_col:
        return {"dates": [], "series": []}

    sql = (
        f"SELECT substr({_quote(time_col)}, 1, 8) AS day_key, "
        f"COALESCE({_quote(violation_col)}, '未标注') AS violation_type, "
        "COUNT(*) AS cnt "
        f"FROM \"{schema.table}\" "
        "GROUP BY day_key, violation_type "
        "ORDER BY day_key ASC"
    )
    with get_conn() as conn:
        rows = conn.execute(sql).fetchall()

    days = sorted({str(r["day_key"] or "") for r in rows if r["day_key"]})
    dates = [f"{d[0:4]}-{d[4:6]}-{d[6:8]}" if len(d) == 8 else d for d in days]
    types = sorted({str(r["violation_type"] or "未标注") for r in rows})
    day_index = {d: i for i, d in enumerate(days)}
    matrix = {t: [0] * len(days) for t in types}

    for r in rows:
        day_key = str(r["day_key"] or "")
        vtype = str(r["violation_type"] or "未标注")
        if day_key in day_index and vtype in matrix:
            matrix[vtype][day_index[day_key]] = int(r["cnt"] or 0)

    series = [{"name": t, "data": matrix[t]} for t in types]
    return {"dates": dates, "series": series}
