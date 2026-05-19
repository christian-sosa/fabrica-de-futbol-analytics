# Reglas Locales Para Codex

## Relacion Con La App Principal

- Este repo consume datos de `C:\Users\Christian\Documents\fabricadefutbol`.
- Si se cambia un mart, extractor, schema, SQL o dashboard que depende de eventos/producto, revisar si tambien hay que tocar:
  - `src/lib/analytics/`
  - `src/lib/growth.ts`
  - `src/app/api/analytics/`
  - `src/types/database.ts`
  - flujos de login/auth, pagos, grupos, partidos, shares y exports
- Si se agrega, renombra o elimina un evento esperado por `analytics_events`, avisar que tambien debe cambiar la allowlist de la app principal.
- No commitear `.env`, warehouses DuckDB, Parquet ni dumps reales.

## Verificacion

- Antes de cerrar cambios de ETL o marts, correr:
  - `python -m fdf_analytics.extract --sample`
  - `python -m fdf_analytics.build_marts`
  - `python -m pytest`
  - `python -m ruff check .`
