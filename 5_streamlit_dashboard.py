import streamlit as st
import pandas as pd
import altair as alt
from sqlalchemy import create_engine
import os
from datetime import datetime

# === Page config ===
st.set_page_config(page_title="Real-Time Revenue Dashboard", layout="wide")

# === Auto-refresh every 60 seconds ===
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=60 * 1000, key="dashboard_refresh")

# === PostgreSQL connection (Docker-safe with env vars) ===
DB_USER = os.getenv("DB_USER", "kritsadakruapat")
DB_PASS = os.getenv("DB_PASS", "NewSecurePassword123!")
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "revenue_dashboard")

engine = create_engine(f'postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}')

# === Query (last 24 hours) ===
query = """
SELECT * FROM transactions_converted
WHERE timestamp >= NOW() - INTERVAL '24 hour'
ORDER BY timestamp DESC;
"""
df = pd.read_sql(query, engine)

if df.empty:
    st.warning("No transactions found in the last 24 hours.")
    st.stop()

# === Preprocessing ===
df['hour'] = df['timestamp'].dt.hour

# === Header ===
st.title("Real-Time Revenue Insights")
st.metric("Total Revenue (USD)", f"${df['usd_converted'].sum():,.2f}")
st.markdown("---")

# === Charts: Country and Currency ===
col1, col2 = st.columns(2)

with col1:
    st.subheader("Revenue by Country")
    st.caption("This chart shows the total USD revenue generated from each country.")
    chart_country = alt.Chart(df.groupby("country", as_index=False)["usd_converted"].sum()).mark_bar().encode(
        x=alt.X('country:N', title="Country"),
        y=alt.Y('usd_converted:Q', title="USD Revenue"),
        tooltip=['country', 'usd_converted']
    ).properties(height=300)
    st.altair_chart(chart_country, use_container_width=True)

with col2:
    st.subheader("Revenue by Currency")
    st.caption("This chart highlights revenue grouped by transaction currency before FX conversion.")
    chart_currency = alt.Chart(df.groupby("currency", as_index=False)["usd_converted"].sum()).mark_bar().encode(
        x=alt.X('currency:N', title="Currency"),
        y=alt.Y('usd_converted:Q', title="USD Revenue"),
        tooltip=['currency', 'usd_converted']
    ).properties(height=300)
    st.altair_chart(chart_currency, use_container_width=True)

# === Charts: User and Hour ===
col3, col4 = st.columns(2)

with col3:
    st.subheader("Revenue by User")
    st.caption("Shows top spending users based on total converted USD revenue.")
    chart_user = alt.Chart(df.groupby("user_id", as_index=False)["usd_converted"].sum()).mark_bar().encode(
        x=alt.X('user_id:N', sort='-y', title="User ID"),
        y=alt.Y('usd_converted:Q', title="USD Revenue"),
        tooltip=['user_id', 'usd_converted']
    ).properties(height=300)
    st.altair_chart(chart_user, use_container_width=True)

with col4:
    st.subheader("Hourly Sales Activity")
    st.caption("Tracks the distribution of revenue across hours in a day.")
    chart_hour = alt.Chart(df.groupby("hour", as_index=False)["usd_converted"].sum()).mark_line(point=True).encode(
        x=alt.X('hour:O', title="Hour of Day"),
        y=alt.Y('usd_converted:Q', title="USD Revenue"),
        tooltip=['hour', 'usd_converted']
    ).properties(height=300)
    st.altair_chart(chart_hour, use_container_width=True)

# === FX Rate Insight (optional data exposure) ===
st.markdown("---")
st.subheader("Recent Transactions (Last 24h)")
st.caption("Below are the latest transactions with applied FX rates for USD conversion.")
st.dataframe(df[['timestamp', 'user_id', 'country', 'currency', 'amount', 'usd_converted']].head(20).style.format({
    'amount': '${:,.2f}',
    'usd_converted': '${:,.2f}'
}))
