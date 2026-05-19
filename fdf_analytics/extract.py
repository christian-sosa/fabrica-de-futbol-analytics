from __future__ import annotations

import argparse
import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd
import psycopg

from fdf_analytics.config import load_config, quote_identifier
from fdf_analytics.sample_data import load_sample_frames
from fdf_analytics.schemas import SOURCE_TABLES, TableSpec


def empty_frame(spec: TableSpec) -> pd.DataFrame:
    return pd.DataFrame(columns=list(spec.columns))


def normalize_frame(table: str, frame: pd.DataFrame) -> pd.DataFrame:
    spec = SOURCE_TABLES[table]
    normalized = frame.copy()

    for column in spec.columns:
        if column not in normalized.columns:
            normalized[column] = None

    normalized = normalized.loc[:, list(spec.columns)]

    for column in spec.json_columns:
        normalized[column] = normalized[column].map(to_json_text)

    return normalized


def to_json_text(value: Any) -> str:
    if value is None:
        return "{}"
    if isinstance(value, str):
        return value
    return json.dumps(value, sort_keys=True, default=str)


def get_existing_columns(conn: psycopg.Connection[Any], schema: str, table: str) -> set[str]:
    query = """
        select column_name
        from information_schema.columns
        where table_schema = %s and table_name = %s
    """
    with conn.cursor() as cur:
        cur.execute(query, (schema, table))
        return {row[0] for row in cur.fetchall()}


def extract_table(conn: psycopg.Connection[Any], schema: str, spec: TableSpec) -> pd.DataFrame:
    existing_columns = get_existing_columns(conn, schema, spec.name)
    selected_columns = [column for column in spec.columns if column in existing_columns]
    if not selected_columns:
        return empty_frame(spec)

    column_sql = ", ".join(quote_identifier(column) for column in selected_columns)
    table_sql = f"{quote_identifier(schema)}.{quote_identifier(spec.name)}"
    query = f"select {column_sql} from {table_sql}"
    frame = pd.read_sql_query(query, conn)
    return normalize_frame(spec.name, frame)


def extract_from_postgres(
    db_url: str,
    schema: str,
    tables: Iterable[str] | None = None,
) -> dict[str, pd.DataFrame]:
    selected_tables = list(tables or SOURCE_TABLES.keys())
    frames: dict[str, pd.DataFrame] = {}

    with psycopg.connect(db_url) as conn:
        conn.execute("set statement_timeout = '60s'")
        for table in selected_tables:
            spec = SOURCE_TABLES[table]
            frames[table] = extract_table(conn, schema, spec)

    return frames


def write_dataframes_to_warehouse(
    frames: dict[str, pd.DataFrame],
    warehouse_path: Path,
) -> list[str]:
    warehouse_path.parent.mkdir(parents=True, exist_ok=True)
    written: list[str] = []

    with duckdb.connect(str(warehouse_path)) as con:
        for table, spec in SOURCE_TABLES.items():
            frame = normalize_frame(table, frames.get(table, empty_frame(spec)))
            con.register("_source_frame", frame)
            con.execute(f"create or replace table raw_{table} as select * from _source_frame")
            con.unregister("_source_frame")
            written.append(f"raw_{table}")

        con.execute(
            """
            create or replace table etl_runs as
            select current_timestamp as loaded_at, ? as table_count
            """,
            [len(written)],
        )

    return written


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extract Supabase/Postgres data into DuckDB raw tables.")
    parser.add_argument("--full-refresh", action="store_true", help="Refresh all raw tables.")
    parser.add_argument("--sample", action="store_true", help="Use sanitized sample data.")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    config = load_config()

    if args.sample:
        frames = load_sample_frames()
    else:
        if not config.supabase_db_url:
            raise SystemExit("SUPABASE_DB_URL is required. Use --sample for the portfolio demo.")
        frames = extract_from_postgres(config.supabase_db_url, config.supabase_db_schema)

    written = write_dataframes_to_warehouse(frames, config.warehouse_path)
    print(f"Wrote {len(written)} raw tables to {config.warehouse_path}")


if __name__ == "__main__":
    main()

