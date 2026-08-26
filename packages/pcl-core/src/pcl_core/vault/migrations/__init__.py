"""Alembic placeholder — canonical DDL lives in engine.SCHEMA and is applied on connect."""

from pcl_core.vault.engine import SCHEMA


def upgrade(conn) -> None:
    conn.executescript(SCHEMA)
