from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd
import plotly.express as px
import streamlit as st

from fdf_analytics.config import load_config

st.set_page_config(page_title="Fabrica de Futbol Analytics", layout="wide")


@st.cache_resource
def connect(warehouse_path: str) -> duckdb.DuckDBPyConnection:
    return duckdb.connect(warehouse_path, read_only=True)


@st.cache_data(ttl=60)
def query(warehouse_path: str, sql: str, params: tuple[object, ...] = ()) -> pd.DataFrame:
    with duckdb.connect(warehouse_path, read_only=True) as con:
        return con.execute(sql, params).df()


def table_exists(warehouse_path: Path, table_name: str) -> bool:
    if not warehouse_path.exists():
        return False
    with duckdb.connect(str(warehouse_path), read_only=True) as con:
        result = con.execute(
            "select count(*) from information_schema.tables where table_name = ?",
            [table_name],
        ).fetchone()
    return bool(result and result[0])


def metric(label: str, value: object) -> None:
    st.metric(label, value)


def main() -> None:
    config = load_config()
    warehouse_path = config.warehouse_path

    st.title("Fabrica de Futbol Analytics")

    if not table_exists(warehouse_path, "mart_growth_daily"):
        st.info("Warehouse no inicializado. Ejecuta estos comandos y recarga el dashboard.")
        st.code(
            "python -m fdf_analytics.extract --sample\n"
            "python -m fdf_analytics.build_marts\n"
            "python -m streamlit run app.py --server.port 8501",
            language="powershell",
        )
        return

    bounds = query(
        str(warehouse_path),
        """
        select min(event_date) as min_date, max(event_date) as max_date
        from mart_growth_daily
        """,
    )
    min_date = bounds["min_date"].iloc[0]
    max_date = bounds["max_date"].iloc[0]

    with st.sidebar:
        st.header("Filtros")
        date_range = st.date_input(
            "Rango de fechas",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )
        if not isinstance(date_range, tuple) or len(date_range) != 2:
            start_date, end_date = min_date, max_date
        else:
            start_date, end_date = date_range

    params = (start_date, end_date)
    growth = query(
        str(warehouse_path),
        """
        select *
        from mart_growth_daily
        where event_date between ? and ?
        """,
        params,
    )
    usage = query(
        str(warehouse_path),
        """
        select *
        from mart_admin_usage
        where event_date between ? and ?
        """,
        params,
    )
    activity = query(
        str(warehouse_path),
        """
        select *
        from mart_product_activity
        where activity_date between ? and ?
        """,
        params,
    )
    finance = query(
        str(warehouse_path),
        """
        select *
        from mart_finance
        where payment_date between ? and ?
        """,
        params,
    )
    retention = query(str(warehouse_path), "select * from mart_retention")
    ranking = query(str(warehouse_path), "select * from mart_entity_ranking")

    total_events = int(growth["events"].sum()) if not growth.empty else 0
    active_admins = int(usage["admin_id"].nunique()) if not usage.empty else 0
    paid_amount = float(finance["paid_amount"].sum()) if not finance.empty else 0
    finished_matches = int(
        activity.loc[activity["metric"].eq("matches_finished"), "value"].sum()
    ) if not activity.empty else 0

    cols = st.columns(4)
    cols[0].metric("Eventos", total_events)
    cols[1].metric("Admins activos", active_admins)
    cols[2].metric("Cobrado", f"${paid_amount:,.0f}")
    cols[3].metric("Partidos finalizados", finished_matches)

    tabs = st.tabs(["Overview", "Growth", "Uso admins", "Actividad", "Finanzas", "Ranking"])

    with tabs[0]:
        left, right = st.columns(2)
        with left:
            if not growth.empty:
                by_stage = growth.groupby("funnel_stage", as_index=False)["events"].sum()
                st.plotly_chart(
                    px.bar(by_stage, x="funnel_stage", y="events", title="Eventos por funnel"),
                    use_container_width=True,
                )
        with right:
            if not finance.empty:
                by_status = finance.groupby("status", as_index=False)[["expected_amount", "paid_amount"]].sum()
                st.plotly_chart(
                    px.bar(
                        by_status,
                        x="status",
                        y=["expected_amount", "paid_amount"],
                        barmode="group",
                        title="Esperado vs pagado",
                    ),
                    use_container_width=True,
                )

    with tabs[1]:
        if growth.empty:
            st.warning("No hay eventos en el rango seleccionado.")
        else:
            daily = growth.groupby(["event_date", "funnel_stage"], as_index=False)["events"].sum()
            st.plotly_chart(
                px.line(daily, x="event_date", y="events", color="funnel_stage", markers=True),
                use_container_width=True,
            )
            st.dataframe(growth.sort_values(["event_date", "events"], ascending=[False, False]))

    with tabs[2]:
        if usage.empty:
            st.warning("No hay logins en el rango seleccionado.")
        else:
            by_day = usage.groupby("event_date", as_index=False).agg(
                login_events=("login_events", "sum"),
                active_admins=("admin_id", "nunique"),
            )
            st.plotly_chart(
                px.bar(by_day, x="event_date", y=["login_events", "active_admins"], barmode="group"),
                use_container_width=True,
            )
            st.dataframe(usage)

    with tabs[3]:
        if activity.empty:
            st.warning("No hay actividad deportiva en el rango seleccionado.")
        else:
            st.plotly_chart(
                px.line(activity, x="activity_date", y="value", color="metric", markers=True),
                use_container_width=True,
            )
            st.dataframe(activity)

    with tabs[4]:
        if finance.empty:
            st.warning("No hay movimientos financieros en el rango seleccionado.")
        else:
            by_flow = finance.groupby(["domain", "flow"], as_index=False)[
                ["expected_amount", "paid_amount"]
            ].sum()
            st.plotly_chart(
                px.bar(
                    by_flow,
                    x="flow",
                    y=["expected_amount", "paid_amount"],
                    color="domain",
                    barmode="group",
                ),
                use_container_width=True,
            )
            st.dataframe(finance.sort_values("payment_date", ascending=False))

    with tabs[5]:
        st.plotly_chart(
            px.bar(
                ranking.head(20),
                x="organization_name",
                y="health_score",
                hover_data=["players", "matches_created", "matches_finished", "paid_amount"],
            ),
            use_container_width=True,
        )
        st.dataframe(ranking)

    if not retention.empty:
        st.subheader("Retencion por cohortes")
        st.plotly_chart(
            px.line(retention, x="day_number", y="active_admins", color="cohort_date", markers=True),
            use_container_width=True,
        )


if __name__ == "__main__":
    main()

