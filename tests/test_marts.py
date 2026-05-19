from __future__ import annotations

import duckdb

from fdf_analytics.build_marts import build_marts
from fdf_analytics.extract import write_dataframes_to_warehouse
from fdf_analytics.sample_data import load_sample_frames
from fdf_analytics.schemas import SOURCE_TABLES


def test_sample_pipeline_builds_expected_marts(tmp_path):
    warehouse_path = tmp_path / "fdf.duckdb"

    write_dataframes_to_warehouse(load_sample_frames(), warehouse_path)
    marts = build_marts(warehouse_path)

    assert "mart_growth_daily" in marts
    assert "mart_finance" in marts

    with duckdb.connect(str(warehouse_path)) as con:
        growth_rows = con.execute("select count(*) from mart_growth_daily").fetchone()[0]
        usage_rows = con.execute("select count(*) from mart_admin_usage").fetchone()[0]
        finance = con.execute(
            "select sum(expected_amount), sum(paid_amount) from mart_finance"
        ).fetchone()
        finance_domains = {
            row[0]
            for row in con.execute("select distinct domain from mart_finance").fetchall()
        }
        raw_org_billing_tables = con.execute(
            """
            select count(*)
            from information_schema.tables
            where table_name in (
              'raw_organization_billing_payments',
              'raw_organization_billing_subscriptions'
            )
            """
        ).fetchone()[0]
        ranking_columns = {
            row[1]
            for row in con.execute("pragma table_info('mart_entity_ranking')").fetchall()
        }
        ranking_rows = con.execute("select count(*) from mart_entity_ranking").fetchone()[0]

    assert growth_rows > 0
    assert usage_rows > 0
    assert "organization_billing_payments" not in SOURCE_TABLES
    assert "organization_billing_subscriptions" not in SOURCE_TABLES
    assert raw_org_billing_tables == 0
    assert finance_domains == {"league", "tournament", "club_match"}
    assert finance == (36300.0, 36150.0)
    assert "expected_amount" not in ranking_columns
    assert "paid_amount" not in ranking_columns
    assert ranking_rows > 0


def test_sample_events_do_not_include_raw_email(tmp_path):
    warehouse_path = tmp_path / "fdf.duckdb"

    write_dataframes_to_warehouse(load_sample_frames(), warehouse_path)
    build_marts(warehouse_path)

    with duckdb.connect(str(warehouse_path)) as con:
        pii_hits = con.execute(
            """
            select count(*)
            from stg_analytics_events
            where regexp_matches(properties, '[^[:space:]@]+@[^[:space:]@]+\\.[^[:space:]@]+')
            """
        ).fetchone()[0]

    assert pii_hits == 0
