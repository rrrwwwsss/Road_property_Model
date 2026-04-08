from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from typing import Iterator

from app.core.config import get_config


@contextmanager
def get_conn() -> Iterator[sqlite3.Connection]:
    cfg = get_config()
    conn = sqlite3.connect(cfg.sqlite.db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
