from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


@dataclass(frozen=True)
class AnalyticsConfig:
    supabase_db_url: str | None
    supabase_db_schema: str
    warehouse_path: Path
    timezone: str


def load_config(env_file: Path | None = None) -> AnalyticsConfig:
    load_dotenv(env_file)

    schema = os.getenv("SUPABASE_DB_SCHEMA", "public").strip() or "public"
    if not IDENTIFIER_RE.match(schema):
        raise ValueError(f"Invalid SUPABASE_DB_SCHEMA: {schema!r}")

    warehouse_path = Path(os.getenv("WAREHOUSE_PATH", "data/warehouse/fdf.duckdb"))

    return AnalyticsConfig(
        supabase_db_url=os.getenv("SUPABASE_DB_URL"),
        supabase_db_schema=schema,
        warehouse_path=warehouse_path,
        timezone=os.getenv("TIMEZONE", "America/Buenos_Aires"),
    )


def quote_identifier(identifier: str) -> str:
    if not IDENTIFIER_RE.match(identifier):
        raise ValueError(f"Invalid SQL identifier: {identifier!r}")
    return f'"{identifier}"'

