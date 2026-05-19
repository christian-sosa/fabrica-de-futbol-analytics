from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TableSpec:
    name: str
    columns: tuple[str, ...]
    types: dict[str, str]
    json_columns: tuple[str, ...] = ()

    def ddl_columns(self) -> str:
        return ", ".join(f"{column} {self.types.get(column, 'VARCHAR')}" for column in self.columns)


def spec(
    name: str,
    columns: tuple[str, ...],
    types: dict[str, str] | None = None,
    json_columns: tuple[str, ...] = (),
) -> TableSpec:
    return TableSpec(name=name, columns=columns, types=types or {}, json_columns=json_columns)


SOURCE_TABLES: dict[str, TableSpec] = {
    "analytics_events": spec(
        "analytics_events",
        (
            "id",
            "created_at",
            "event_name",
            "source",
            "admin_id",
            "organization_id",
            "club_id",
            "league_id",
            "entity_type",
            "entity_id",
            "path",
            "properties",
        ),
        {
            "id": "VARCHAR",
            "created_at": "TIMESTAMP",
            "event_name": "VARCHAR",
            "source": "VARCHAR",
            "admin_id": "VARCHAR",
            "organization_id": "VARCHAR",
            "club_id": "VARCHAR",
            "league_id": "VARCHAR",
            "entity_type": "VARCHAR",
            "entity_id": "VARCHAR",
            "path": "VARCHAR",
            "properties": "VARCHAR",
        },
        json_columns=("properties",),
    ),
    "admins": spec(
        "admins",
        ("id", "created_at", "display_name"),
        {"id": "VARCHAR", "created_at": "TIMESTAMP", "display_name": "VARCHAR"},
    ),
    "organizations": spec(
        "organizations",
        ("id", "created_at", "created_by", "name", "slug", "is_public"),
        {
            "id": "VARCHAR",
            "created_at": "TIMESTAMP",
            "created_by": "VARCHAR",
            "name": "VARCHAR",
            "slug": "VARCHAR",
            "is_public": "BOOLEAN",
        },
    ),
    "organization_admins": spec(
        "organization_admins",
        ("id", "created_at", "organization_id", "admin_id", "role"),
        {
            "id": "VARCHAR",
            "created_at": "TIMESTAMP",
            "organization_id": "VARCHAR",
            "admin_id": "VARCHAR",
            "role": "VARCHAR",
        },
    ),
    "players": spec(
        "players",
        ("id", "created_at", "organization_id", "active"),
        {
            "id": "VARCHAR",
            "created_at": "TIMESTAMP",
            "organization_id": "VARCHAR",
            "active": "BOOLEAN",
        },
    ),
    "matches": spec(
        "matches",
        (
            "id",
            "created_at",
            "created_by",
            "organization_id",
            "status",
            "modality",
            "scheduled_at",
            "finished_at",
        ),
        {
            "id": "VARCHAR",
            "created_at": "TIMESTAMP",
            "created_by": "VARCHAR",
            "organization_id": "VARCHAR",
            "status": "VARCHAR",
            "modality": "VARCHAR",
            "scheduled_at": "TIMESTAMP",
            "finished_at": "TIMESTAMP",
        },
    ),
    "clubs": spec(
        "clubs",
        ("id", "created_at", "created_by", "name", "slug", "status", "is_public"),
        {
            "id": "VARCHAR",
            "created_at": "TIMESTAMP",
            "created_by": "VARCHAR",
            "name": "VARCHAR",
            "slug": "VARCHAR",
            "status": "VARCHAR",
            "is_public": "BOOLEAN",
        },
    ),
    "club_matches": spec(
        "club_matches",
        ("id", "created_at", "created_by", "club_id", "status", "played_at", "field_cost_cents"),
        {
            "id": "VARCHAR",
            "created_at": "TIMESTAMP",
            "created_by": "VARCHAR",
            "club_id": "VARCHAR",
            "status": "VARCHAR",
            "played_at": "TIMESTAMP",
            "field_cost_cents": "BIGINT",
        },
    ),
    "club_match_payments": spec(
        "club_match_payments",
        ("id", "created_at", "match_id", "expected_cents", "paid_cents", "paid_at"),
        {
            "id": "VARCHAR",
            "created_at": "TIMESTAMP",
            "match_id": "VARCHAR",
            "expected_cents": "BIGINT",
            "paid_cents": "BIGINT",
            "paid_at": "TIMESTAMP",
        },
    ),
    "tournament_billing_payments": spec(
        "tournament_billing_payments",
        (
            "id",
            "created_at",
            "admin_id",
            "created_tournament_id",
            "amount",
            "currency_id",
            "status",
            "approved_at",
        ),
        {
            "id": "VARCHAR",
            "created_at": "TIMESTAMP",
            "admin_id": "VARCHAR",
            "created_tournament_id": "VARCHAR",
            "amount": "DOUBLE",
            "currency_id": "VARCHAR",
            "status": "VARCHAR",
            "approved_at": "TIMESTAMP",
        },
    ),
    "organization_billing_payments": spec(
        "organization_billing_payments",
        (
            "id",
            "created_at",
            "organization_id",
            "requested_by_admin_id",
            "created_organization_id",
            "amount",
            "currency_id",
            "status",
            "purpose",
            "approved_at",
        ),
        {
            "id": "VARCHAR",
            "created_at": "TIMESTAMP",
            "organization_id": "VARCHAR",
            "requested_by_admin_id": "VARCHAR",
            "created_organization_id": "VARCHAR",
            "amount": "DOUBLE",
            "currency_id": "VARCHAR",
            "status": "VARCHAR",
            "purpose": "VARCHAR",
            "approved_at": "TIMESTAMP",
        },
    ),
    "league_billing_payments": spec(
        "league_billing_payments",
        (
            "id",
            "created_at",
            "admin_id",
            "created_league_id",
            "amount",
            "currency_id",
            "status",
            "purpose",
            "approved_at",
        ),
        {
            "id": "VARCHAR",
            "created_at": "TIMESTAMP",
            "admin_id": "VARCHAR",
            "created_league_id": "VARCHAR",
            "amount": "DOUBLE",
            "currency_id": "VARCHAR",
            "status": "VARCHAR",
            "purpose": "VARCHAR",
            "approved_at": "TIMESTAMP",
        },
    ),
}

