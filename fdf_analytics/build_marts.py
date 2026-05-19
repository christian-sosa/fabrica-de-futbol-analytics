from __future__ import annotations

import argparse
from pathlib import Path

import duckdb

from fdf_analytics.config import load_config
from fdf_analytics.schemas import SOURCE_TABLES


def ensure_raw_tables(con: duckdb.DuckDBPyConnection) -> None:
    for table, spec in SOURCE_TABLES.items():
        con.execute(f"create table if not exists raw_{table} ({spec.ddl_columns()})")


def build_marts(warehouse_path: Path) -> list[str]:
    warehouse_path.parent.mkdir(parents=True, exist_ok=True)

    with duckdb.connect(str(warehouse_path)) as con:
        ensure_raw_tables(con)
        con.execute("create schema if not exists main")

        con.execute(
            """
            create or replace table stg_analytics_events as
            select
              cast(id as varchar) as id,
              try_cast(created_at as timestamp) as event_at,
              cast(date_trunc('day', try_cast(created_at as timestamp)) as date) as event_date,
              cast(event_name as varchar) as event_name,
              coalesce(nullif(cast(source as varchar), ''), 'unknown') as source,
              cast(admin_id as varchar) as admin_id,
              cast(organization_id as varchar) as organization_id,
              cast(club_id as varchar) as club_id,
              cast(league_id as varchar) as league_id,
              cast(entity_type as varchar) as entity_type,
              cast(entity_id as varchar) as entity_id,
              cast(path as varchar) as path,
              cast(properties as varchar) as properties,
              case
                when event_name in ('cta_clicked', 'signup_started') then 'acquisition'
                when event_name in ('admin_register_succeeded', 'group_created') then 'activation'
                when event_name in ('group_shared', 'ranking_shared', 'match_shared') then 'referral'
                when event_name in ('billing_started', 'payment_created', 'payment_returned', 'payment_approved') then 'revenue'
                when event_name in ('admin_login_succeeded', 'admin_oauth_login_succeeded') then 'retention'
                else 'product'
              end as funnel_stage
            from raw_analytics_events
            where event_name is not null
              and try_cast(created_at as timestamp) is not null
            """
        )

        con.execute(
            """
            create or replace table stg_organizations as
            select
              cast(id as varchar) as organization_id,
              try_cast(created_at as timestamp) as created_at,
              cast(date_trunc('day', try_cast(created_at as timestamp)) as date) as created_date,
              cast(created_by as varchar) as admin_id,
              cast(name as varchar) as organization_name,
              cast(slug as varchar) as organization_slug,
              coalesce(try_cast(is_public as boolean), false) as is_public
            from raw_organizations
            where id is not null
            """
        )

        con.execute(
            """
            create or replace table stg_matches as
            select
              cast(id as varchar) as match_id,
              try_cast(created_at as timestamp) as created_at,
              cast(date_trunc('day', try_cast(created_at as timestamp)) as date) as created_date,
              cast(created_by as varchar) as admin_id,
              cast(organization_id as varchar) as organization_id,
              cast(status as varchar) as status,
              cast(modality as varchar) as modality,
              try_cast(scheduled_at as timestamp) as scheduled_at,
              try_cast(finished_at as timestamp) as finished_at
            from raw_matches
            where id is not null
            """
        )

        con.execute(
            """
            create or replace table mart_growth_daily as
            select
              event_date,
              source,
              funnel_stage,
              event_name,
              count(*) as events,
              count(distinct admin_id) filter (where admin_id is not null) as admins,
              count(distinct organization_id) filter (where organization_id is not null) as organizations
            from stg_analytics_events
            group by all
            order by event_date, funnel_stage, event_name
            """
        )

        con.execute(
            """
            create or replace table mart_admin_usage as
            select
              event_date,
              coalesce(admin_id, 'anonymous') as admin_id,
              count(*) as login_events,
              min(event_at) as first_login_at,
              max(event_at) as last_login_at
            from stg_analytics_events
            where event_name in ('admin_login_succeeded', 'admin_oauth_login_succeeded')
            group by all
            order by event_date, admin_id
            """
        )

        con.execute(
            """
            create or replace table mart_product_activity as
            with daily as (
              select created_date as activity_date, organization_id, 'groups_created' as metric, count(*) as value
              from stg_organizations
              group by all
              union all
              select
                cast(date_trunc('day', try_cast(created_at as timestamp)) as date) as activity_date,
                cast(organization_id as varchar) as organization_id,
                'players_created' as metric,
                count(*) as value
              from raw_players
              where id is not null and try_cast(created_at as timestamp) is not null
              group by all
              union all
              select created_date as activity_date, organization_id, 'matches_created' as metric, count(*) as value
              from stg_matches
              group by all
              union all
              select
                cast(date_trunc('day', coalesce(finished_at, created_at)) as date) as activity_date,
                organization_id,
                'matches_finished' as metric,
                count(*) as value
              from stg_matches
              where status in ('finished', 'played')
              group by all
            )
            select *
            from daily
            where activity_date is not null
            order by activity_date, metric
            """
        )

        con.execute(
            """
            create or replace table mart_finance as
            with org_payments as (
              select
                cast(date_trunc('day', try_cast(created_at as timestamp)) as date) as payment_date,
                'organization' as domain,
                coalesce(nullif(cast(purpose as varchar), ''), 'organization_payment') as flow,
                cast(organization_id as varchar) as entity_id,
                cast(status as varchar) as status,
                coalesce(try_cast(amount as double), 0) as expected_amount,
                case when status = 'approved' then coalesce(try_cast(amount as double), 0) else 0 end as paid_amount,
                coalesce(cast(currency_id as varchar), 'ARS') as currency
              from raw_organization_billing_payments
              union all
              select
                cast(date_trunc('day', try_cast(created_at as timestamp)) as date) as payment_date,
                'league' as domain,
                coalesce(nullif(cast(purpose as varchar), ''), 'league_payment') as flow,
                cast(created_league_id as varchar) as entity_id,
                cast(status as varchar) as status,
                coalesce(try_cast(amount as double), 0) as expected_amount,
                case when status = 'approved' then coalesce(try_cast(amount as double), 0) else 0 end as paid_amount,
                coalesce(cast(currency_id as varchar), 'ARS') as currency
              from raw_league_billing_payments
              union all
              select
                cast(date_trunc('day', try_cast(created_at as timestamp)) as date) as payment_date,
                'tournament' as domain,
                'tournament_payment' as flow,
                cast(created_tournament_id as varchar) as entity_id,
                cast(status as varchar) as status,
                coalesce(try_cast(amount as double), 0) as expected_amount,
                case when status = 'approved' then coalesce(try_cast(amount as double), 0) else 0 end as paid_amount,
                coalesce(cast(currency_id as varchar), 'ARS') as currency
              from raw_tournament_billing_payments
              union all
              select
                cast(date_trunc('day', try_cast(created_at as timestamp)) as date) as payment_date,
                'club_match' as domain,
                'field_cost_collection' as flow,
                cast(match_id as varchar) as entity_id,
                case
                  when coalesce(try_cast(paid_cents as double), 0) >= coalesce(try_cast(expected_cents as double), 0) then 'paid'
                  when coalesce(try_cast(paid_cents as double), 0) > 0 then 'partial'
                  else 'pending'
                end as status,
                coalesce(try_cast(expected_cents as double), 0) / 100 as expected_amount,
                coalesce(try_cast(paid_cents as double), 0) / 100 as paid_amount,
                'ARS' as currency
              from raw_club_match_payments
            )
            select *
            from org_payments
            where payment_date is not null
            order by payment_date, domain, flow
            """
        )

        con.execute(
            """
            create or replace table mart_retention as
            with cohorts as (
              select
                admin_id,
                organization_id,
                created_date as cohort_date
              from stg_organizations
              where admin_id is not null
            ),
            activity as (
              select admin_id, organization_id, event_date as activity_date
              from stg_analytics_events
              where admin_id is not null and event_date is not null
            )
            select
              cohorts.cohort_date,
              date_diff('day', cohorts.cohort_date, activity.activity_date) as day_number,
              count(distinct cohorts.admin_id) as active_admins,
              count(distinct cohorts.organization_id) as active_organizations
            from cohorts
            left join activity
              on activity.admin_id = cohorts.admin_id
             and activity.activity_date >= cohorts.cohort_date
             and activity.activity_date < cohorts.cohort_date + interval '31 days'
            group by all
            order by cohort_date, day_number
            """
        )

        con.execute(
            """
            create or replace table mart_entity_ranking as
            with player_counts as (
              select cast(organization_id as varchar) as organization_id, count(*) as players
              from raw_players
              where id is not null
              group by all
            ),
            match_counts as (
              select
                organization_id,
                count(*) as matches_created,
                count(*) filter (where status in ('finished', 'played')) as matches_finished
              from stg_matches
              group by all
            ),
            finance as (
              select entity_id as organization_id, sum(expected_amount) as expected_amount, sum(paid_amount) as paid_amount
              from mart_finance
              where domain = 'organization'
              group by all
            )
            select
              org.organization_id,
              org.organization_name,
              org.created_date,
              coalesce(players.players, 0) as players,
              coalesce(matches.matches_created, 0) as matches_created,
              coalesce(matches.matches_finished, 0) as matches_finished,
              coalesce(finance.expected_amount, 0) as expected_amount,
              coalesce(finance.paid_amount, 0) as paid_amount,
              (
                coalesce(players.players, 0)
                + coalesce(matches.matches_created, 0) * 3
                + coalesce(matches.matches_finished, 0) * 5
                + case when coalesce(finance.paid_amount, 0) > 0 then 10 else 0 end
              ) as health_score
            from stg_organizations org
            left join player_counts players using (organization_id)
            left join match_counts matches using (organization_id)
            left join finance using (organization_id)
            order by health_score desc, org.created_date desc
            """
        )

    return [
        "mart_growth_daily",
        "mart_admin_usage",
        "mart_product_activity",
        "mart_finance",
        "mart_retention",
        "mart_entity_ranking",
    ]


def build_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(description="Build DuckDB staging tables and analytics marts.")


def main() -> None:
    build_parser().parse_args()
    config = load_config()
    marts = build_marts(config.warehouse_path)
    print(f"Built {len(marts)} marts in {config.warehouse_path}: {', '.join(marts)}")


if __name__ == "__main__":
    main()

