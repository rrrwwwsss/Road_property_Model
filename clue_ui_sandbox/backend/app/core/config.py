from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


def _load_backend_dotenv() -> None:
    backend_root = Path(__file__).resolve().parents[2]
    env_path = backend_root / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path, override=False)


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


@dataclass(frozen=True)
class SqliteConfig:
    db_path: str
    table: str
    pk_field: str
    image_field: str


@dataclass(frozen=True)
class CommitConfig:
    gateway: str
    trade: str
    data_source: str
    yehu_name: str
    evidence_type: str
    level: str
    tj_check_result: str
    is_del: str


@dataclass(frozen=True)
class TaijiDbConfig:
    host: str
    port: int
    user: str
    password: str
    schema: str
    table_warns_hb: str
    table_errors_hb: str


@dataclass(frozen=True)
class AppConfig:
    sqlite: SqliteConfig
    commit: CommitConfig
    taiji: TaijiDbConfig


@lru_cache(maxsize=1)
def get_config() -> AppConfig:
    _load_backend_dotenv()
    repo_root = Path(__file__).resolve().parents[4]
    default_db = str(repo_root / "pic" / "database" / "wupin_tanwei_dabt.db")

    sqlite = SqliteConfig(
        db_path=os.getenv("CLUE_DB_PATH", default_db),
        table=os.getenv("CLUE_DB_TABLE", "results"),
        pk_field=os.getenv("CLUE_DB_PK_FIELD", "id"),
        image_field=os.getenv("CLUE_DB_IMAGE_FIELD", "图片路径"),
    )

    commit = CommitConfig(
        gateway=os.getenv("CLUE_COMMIT_GATEWAY", "mock").strip().lower(),
        trade=os.getenv("CLUE_TAIJI_TRADE", "36"),
        data_source=os.getenv("CLUE_TAIJI_DATA_SOURCE", "中路高科"),
        yehu_name=os.getenv("CLUE_TAIJI_YEHU_NAME", "无法确定当事人"),
        evidence_type=os.getenv("CLUE_TAIJI_EVIDENCE_TYPE", "YJ"),
        level=os.getenv("CLUE_TAIJI_LEVEL", "中"),
        tj_check_result=os.getenv("CLUE_TAIJI_TJ_CHECK_RESULT", "0"),
        is_del=os.getenv("CLUE_TAIJI_IS_DEL", "0"),
    )

    taiji = TaijiDbConfig(
        host=os.getenv("CLUE_TAIJI_DB_HOST", "172.26.76.79"),
        port=_get_int("CLUE_TAIJI_DB_PORT", 5236),
        user=os.getenv("CLUE_TAIJI_DB_USER", "sjtb"),
        password=os.getenv("CLUE_TAIJI_DB_PASSWORD", ""),
        schema=os.getenv("CLUE_TAIJI_DB_SCHEMA", "offsite"),
        table_warns_hb=os.getenv("CLUE_TAIJI_TABLE_WARNS", "OFFSITE_WARNS_HB"),
        table_errors_hb=os.getenv("CLUE_TAIJI_TABLE_ERRORS", "OFFSITE_INTELLECT_ERRORS_HB"),
    )

    return AppConfig(sqlite=sqlite, commit=commit, taiji=taiji)
