from __future__ import annotations

import json

import pandas as pd


def load_sample_frames() -> dict[str, pd.DataFrame]:
    return {
        "admins": pd.DataFrame(
            [
                {"id": "admin-1", "created_at": "2026-05-01T12:00:00Z", "display_name": "Owner"},
                {"id": "admin-2", "created_at": "2026-05-07T15:00:00Z", "display_name": "Liga Norte"},
            ]
        ),
        "organizations": pd.DataFrame(
            [
                {
                    "id": "org-1",
                    "created_at": "2026-05-02T10:00:00Z",
                    "created_by": "admin-1",
                    "name": "Futbol 7 Palermo",
                    "slug": "f7-palermo",
                    "is_public": True,
                },
                {
                    "id": "org-2",
                    "created_at": "2026-05-08T18:00:00Z",
                    "created_by": "admin-2",
                    "name": "Liga Norte",
                    "slug": "liga-norte",
                    "is_public": True,
                },
            ]
        ),
        "organization_admins": pd.DataFrame(
            [
                {
                    "id": "oa-1",
                    "created_at": "2026-05-02T10:00:00Z",
                    "organization_id": "org-1",
                    "admin_id": "admin-1",
                    "role": "owner",
                },
                {
                    "id": "oa-2",
                    "created_at": "2026-05-08T18:00:00Z",
                    "organization_id": "org-2",
                    "admin_id": "admin-2",
                    "role": "owner",
                },
            ]
        ),
        "players": pd.DataFrame(
            [
                {"id": f"player-{idx}", "created_at": "2026-05-03T12:00:00Z", "organization_id": "org-1", "active": True}
                for idx in range(1, 9)
            ]
            + [
                {"id": f"player-b-{idx}", "created_at": "2026-05-09T12:00:00Z", "organization_id": "org-2", "active": True}
                for idx in range(1, 6)
            ]
        ),
        "matches": pd.DataFrame(
            [
                {
                    "id": "match-1",
                    "created_at": "2026-05-04T19:00:00Z",
                    "created_by": "admin-1",
                    "organization_id": "org-1",
                    "status": "finished",
                    "modality": "7v7",
                    "scheduled_at": "2026-05-05T22:00:00Z",
                    "finished_at": "2026-05-05T23:30:00Z",
                },
                {
                    "id": "match-2",
                    "created_at": "2026-05-10T19:00:00Z",
                    "created_by": "admin-1",
                    "organization_id": "org-1",
                    "status": "confirmed",
                    "modality": "5v5",
                    "scheduled_at": "2026-05-11T22:00:00Z",
                    "finished_at": None,
                },
                {
                    "id": "match-3",
                    "created_at": "2026-05-11T20:00:00Z",
                    "created_by": "admin-2",
                    "organization_id": "org-2",
                    "status": "finished",
                    "modality": "9v9",
                    "scheduled_at": "2026-05-12T22:00:00Z",
                    "finished_at": "2026-05-12T23:45:00Z",
                },
            ]
        ),
        "clubs": pd.DataFrame(
            [
                {
                    "id": "club-1",
                    "created_at": "2026-05-06T12:00:00Z",
                    "created_by": "admin-1",
                    "name": "Club Sur",
                    "slug": "club-sur",
                    "status": "active",
                    "is_public": True,
                }
            ]
        ),
        "club_matches": pd.DataFrame(
            [
                {
                    "id": "club-match-1",
                    "created_at": "2026-05-13T12:00:00Z",
                    "created_by": "admin-1",
                    "club_id": "club-1",
                    "status": "played",
                    "played_at": "2026-05-14T21:00:00Z",
                    "field_cost_cents": 30000,
                }
            ]
        ),
        "club_match_payments": pd.DataFrame(
            [
                {
                    "id": "cmp-1",
                    "created_at": "2026-05-14T22:00:00Z",
                    "match_id": "club-match-1",
                    "expected_cents": 10000,
                    "paid_cents": 10000,
                    "paid_at": "2026-05-14T22:30:00Z",
                },
                {
                    "id": "cmp-2",
                    "created_at": "2026-05-14T22:00:00Z",
                    "match_id": "club-match-1",
                    "expected_cents": 10000,
                    "paid_cents": 5000,
                    "paid_at": "2026-05-15T10:00:00Z",
                },
                {
                    "id": "cmp-3",
                    "created_at": "2026-05-14T22:00:00Z",
                    "match_id": "club-match-1",
                    "expected_cents": 10000,
                    "paid_cents": 0,
                    "paid_at": None,
                },
            ]
        ),
        "organization_billing_payments": pd.DataFrame(
            [
                {
                    "id": "org-pay-1",
                    "created_at": "2026-05-08T18:10:00Z",
                    "organization_id": "org-1",
                    "requested_by_admin_id": "admin-1",
                    "created_organization_id": None,
                    "amount": 14000,
                    "currency_id": "ARS",
                    "status": "approved",
                    "purpose": "organization_subscription",
                    "approved_at": "2026-05-08T18:20:00Z",
                },
                {
                    "id": "org-pay-2",
                    "created_at": "2026-05-12T18:10:00Z",
                    "organization_id": "org-2",
                    "requested_by_admin_id": "admin-2",
                    "created_organization_id": "org-2",
                    "amount": 14000,
                    "currency_id": "ARS",
                    "status": "pending",
                    "purpose": "organization_creation",
                    "approved_at": None,
                },
            ]
        ),
        "league_billing_payments": pd.DataFrame(
            [
                {
                    "id": "league-pay-1",
                    "created_at": "2026-05-10T17:00:00Z",
                    "admin_id": "admin-2",
                    "created_league_id": "league-1",
                    "amount": 18000,
                    "currency_id": "ARS",
                    "status": "approved",
                    "purpose": "league_creation",
                    "approved_at": "2026-05-10T17:10:00Z",
                }
            ]
        ),
        "tournament_billing_payments": pd.DataFrame(
            [
                {
                    "id": "tournament-pay-1",
                    "created_at": "2026-05-11T17:00:00Z",
                    "admin_id": "admin-2",
                    "created_tournament_id": "tournament-1",
                    "amount": 18000,
                    "currency_id": "ARS",
                    "status": "approved",
                    "approved_at": "2026-05-11T17:10:00Z",
                }
            ]
        ),
        "analytics_events": pd.DataFrame(
            [
                event("evt-1", "2026-05-03T11:00:00Z", "cta_clicked", "home_hero", None, None, None, None, "landing", None, "/", {"cta": "create_group"}),
                event("evt-2", "2026-05-03T11:05:00Z", "signup_started", "login_form", None, None, None, None, "admin", None, "/admin/login", {"mode": "register"}),
                event("evt-3", "2026-05-03T11:20:00Z", "admin_register_succeeded", "server", "admin-1", None, None, None, "admin", "admin-1", "/admin/login", {"method": "password"}),
                event("evt-4", "2026-05-04T10:00:00Z", "group_created", "server", "admin-1", "org-1", None, None, "organization", "org-1", "/admin/new", {"visibility": "public"}),
                event("evt-5", "2026-05-05T12:00:00Z", "admin_login_succeeded", "server", "admin-1", "org-1", None, None, "admin", "admin-1", "/admin/login", {"method": "password"}),
                event("evt-6", "2026-05-05T19:00:00Z", "match_created", "server", "admin-1", "org-1", None, None, "match", "match-1", "/admin/matches/new", {"modality": "7v7"}),
                event("evt-7", "2026-05-05T23:30:00Z", "match_finished", "server", "admin-1", "org-1", None, None, "match", "match-1", "/admin/matches/match-1", {"status": "finished"}),
                event("evt-8", "2026-05-08T18:20:00Z", "payment_approved", "server", "admin-1", "org-1", None, None, "payment", "org-pay-1", None, {"flow": "organization_subscription"}),
                event("evt-9", "2026-05-10T10:00:00Z", "group_shared", "whatsapp", None, "org-1", None, None, "organization", "org-1", "/groups/f7-palermo", {"content": "ranking"}),
                event("evt-10", "2026-05-12T22:00:00Z", "admin_login_succeeded", "server", "admin-2", "org-2", None, None, "admin", "admin-2", "/admin/login", {"method": "oauth"}),
            ]
        ),
    }


def event(
    event_id: str,
    created_at: str,
    event_name: str,
    source: str,
    admin_id: str | None,
    organization_id: str | None,
    club_id: str | None,
    league_id: str | None,
    entity_type: str | None,
    entity_id: str | None,
    path: str | None,
    properties: dict[str, object],
) -> dict[str, object]:
    return {
        "id": event_id,
        "created_at": created_at,
        "event_name": event_name,
        "source": source,
        "admin_id": admin_id,
        "organization_id": organization_id,
        "club_id": club_id,
        "league_id": league_id,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "path": path,
        "properties": json.dumps(properties, sort_keys=True),
    }

