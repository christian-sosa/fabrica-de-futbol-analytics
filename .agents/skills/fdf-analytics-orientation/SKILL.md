---
name: fdf-analytics-orientation
description: Use when starting work in the Fabrica de Futbol analytics repo, changing ETL/marts/dashboard code, or deciding whether the app repo must be reviewed.
---

# FDF Analytics Orientation

## Quick Start

1. Read `AGENTS.md`.
2. Read `AGENT_CONTEXT.json`.
3. Run `python scripts/check_agent_impact.py` before finalizing cross-repo-sensitive changes.

## Repo Map

- Analytics repo: `C:\Users\Christian\Documents\fabrica-de-futbol-analytics`
- App repo: `C:\Users\Christian\Documents\fabricadefutbol`
- Source schema for analytics extraction: `analytics`
- Warehouse: DuckDB at `data/warehouse/fdf.duckdb`

## Search Guide

- Table extraction contract: `fdf_analytics/schemas.py`
- Postgres -> DuckDB raw extraction: `fdf_analytics/extract.py`
- Staging/marts: `fdf_analytics/build_marts.py`
- Streamlit dashboard: `app.py`
- Sample fixtures: `fdf_analytics/sample_data.py`
- Tests: `tests/test_marts.py`

## Cross-Repo Rules

- If analytics needs a new event, review `src/lib/analytics/events.ts` in the app.
- If analytics needs a new table or column, review Supabase views and `src/types/database.ts` in the app.
- Do not introduce real PII, service role keys or production dumps.

## Verification

- `python -m fdf_analytics.extract --sample`
- `python -m fdf_analytics.build_marts`
- `python -m pytest`
- `python -m ruff check .`
