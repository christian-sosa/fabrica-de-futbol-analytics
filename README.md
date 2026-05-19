# Fabrica de Futbol Analytics

Proyecto de analitica avanzada para Fabrica de Futbol. Consume datos operativos desde Supabase/Postgres, los persiste en DuckDB y expone dashboards interactivos con Streamlit.

## Stack

- Streamlit para dashboards interactivos.
- DuckDB como warehouse local persistente.
- Pandas/Polars para transformaciones tabulares.
- Plotly para visualizaciones.
- psycopg para leer Supabase/Postgres con credenciales read-only.
- pytest y ruff para calidad.

## Setup local

```powershell
cd C:\Users\Christian\Documents\fabrica-de-futbol-analytics
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Crear `.env` desde `.env.example` y configurar `SUPABASE_DB_URL` con un rol read-only.

## Correr con datos reales

```powershell
python -m fdf_analytics.extract --full-refresh
python -m fdf_analytics.build_marts
python -m streamlit run app.py --server.port 8501
```

## Correr demo portfolio sin credenciales

```powershell
python -m fdf_analytics.extract --sample
python -m fdf_analytics.build_marts
python -m streamlit run app.py --server.port 8501
```

## Marts iniciales

- `mart_growth_daily`: eventos por dia, fuente, funnel y CTA.
- `mart_admin_usage`: logins por dia, admins activos y frecuencia.
- `mart_product_activity`: grupos, jugadores y partidos creados/finalizados.
- `mart_finance`: ingresos y cobros existentes por flujo.
- `mart_retention`: cohortes por fecha de creacion y actividad posterior.
- `mart_entity_ranking`: ranking de entidades para priorizar seguimiento.

## Seguridad

No commitear `.env`, warehouses DuckDB, Parquet ni dumps reales. El SQL en `sql/analytics_events.sql` es una plantilla didactica; aplicar en Supabase con revision manual y credenciales reales fuera del repo.
