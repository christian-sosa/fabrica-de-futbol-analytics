-- Template for Supabase/Postgres. Review before applying in production.
-- Keep credentials outside Git. Replace role/password names manually.

create extension if not exists pgcrypto;

create table if not exists public.analytics_events (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  event_name text not null check (
    event_name in (
      'billing_started',
      'cta_clicked',
      'group_created',
      'group_shared',
      'match_created',
      'match_shared',
      'payment_returned',
      'players_page_opened',
      'ranking_shared',
      'signup_started',
      'admin_login_succeeded',
      'admin_oauth_login_succeeded',
      'admin_register_succeeded',
      'match_finished',
      'payment_created',
      'payment_approved',
      'super_metrics_exported'
    )
  ),
  source text not null default 'server',
  admin_id uuid null references auth.users(id) on delete set null,
  organization_id uuid null references public.organizations(id) on delete set null,
  club_id uuid null references public.clubs(id) on delete set null,
  league_id uuid null references public.leagues(id) on delete set null,
  entity_type text null,
  entity_id uuid null,
  path text null,
  properties jsonb not null default '{}'::jsonb
);

alter table public.analytics_events enable row level security;

revoke all on table public.analytics_events from anon;
revoke all on table public.analytics_events from authenticated;

do $$
begin
  if not exists (
    select 1
    from pg_policies
    where schemaname = 'public'
      and tablename = 'analytics_events'
      and policyname = 'analytics_events_service_role_all'
  ) then
    create policy analytics_events_service_role_all
      on public.analytics_events
      for all
      to service_role
      using (true)
      with check (true);
  end if;
end $$;

create index if not exists idx_analytics_events_created_at
  on public.analytics_events (created_at desc);

create index if not exists idx_analytics_events_event_created_at
  on public.analytics_events (event_name, created_at desc);

create index if not exists idx_analytics_events_admin_created_at
  on public.analytics_events (admin_id, created_at desc)
  where admin_id is not null;

create index if not exists idx_analytics_events_organization_created_at
  on public.analytics_events (organization_id, created_at desc)
  where organization_id is not null;

-- Optional read-only analytics role. Set the password manually outside Git.
-- create role analytics_reader login password 'replace-with-local-secret';
-- grant usage on schema public to analytics_reader;
-- grant select on public.analytics_events to analytics_reader;
-- grant select on public.admins to analytics_reader;
-- grant select on public.organizations to analytics_reader;
-- grant select on public.players to analytics_reader;
-- grant select on public.matches to analytics_reader;
-- grant select on public.clubs to analytics_reader;
-- grant select on public.club_matches to analytics_reader;
-- grant select on public.club_match_payments to analytics_reader;
-- grant select on public.tournament_billing_payments to analytics_reader;
-- grant select on public.league_billing_payments to analytics_reader;
-- create policy analytics_events_analytics_reader_select
--   on public.analytics_events
--   for select
--   to analytics_reader
--   using (true);
