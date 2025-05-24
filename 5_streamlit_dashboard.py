import streamlit as st
import pandas as pd
import altair as alt
from sqlalchemy import create_engine

st.set_page_config(page_title="Real-Time Revenue Dashboard", layout="wide")

# PostgreSQL connection
engine = create_engine(
    'postgresql+psycopg2://kritsadakruapat:NewSecurePassword123!@localhost:5432/revenue_dashboard'
)

# Query latest 24h transactions
query = """
SELECT * FROM transactions
WHERE timestamp >= NOW() - INTERVAL '24 hour'
ORDER BY timestamp DESC;
"""
df = pd.read_sql(query, engine)
df['hour'] = df['timestamp'].dt.hour

# Header
st.title("Real-Time Revenue Insights")

# Top KPI
st.metric("Total Revenue (USD)", f"${df['usd_amount'].sum():,.2f}")
st.markdown("---")

# Charts section
col1, col2 = st.columns(2)

with col1:
    st.subheader("Revenue by Country")
    chart_country = alt.Chart(df.groupby("country", as_index=False)["usd_amount"].sum()).mark_bar().encode(
        x=alt.X('country:N', title="Country"),
        y=alt.Y('usd_amount:Q', title="USD Revenue"),
        tooltip=['country', 'usd_amount']
    ).properties(height=300)
    st.altair_chart(chart_country, use_container_width=True)

with col2:
    st.subheader("Revenue by Currency")
    chart_currency = alt.Chart(df.groupby("currency", as_index=False)["usd_amount"].sum()).mark_bar().encode(
        x=alt.X('currency:N', title="Currency"),
        y=alt.Y('usd_amount:Q', title="USD Revenue"),
        tooltip=['currency', 'usd_amount']
    ).properties(height=300)
    st.altair_chart(chart_currency, use_container_width=True)

# Another row
col3, col4 = st.columns(2)

with col3:
    st.subheader("Revenue by User")
    chart_user = alt.Chart(df.groupby("user_id", as_index=False)["usd_amount"].sum()).mark_bar().encode(
        x=alt.X('user_id:N', sort='-y', title="User ID"),
        y=alt.Y('usd_amount:Q', title="USD Revenue"),
        tooltip=['user_id', 'usd_amount']
    ).properties(height=300)
    st.altair_chart(chart_user, use_container_width=True)

with col4:
    st.subheader("Hourly Sales Activity")
    chart_hour = alt.Chart(df.groupby("hour", as_index=False)["usd_amount"].sum()).mark_line(point=True).encode(
        x=alt.X('hour:O', title="Hour of Day"),
        y=alt.Y('usd_amount:Q', title="USD Revenue"),
        tooltip=['hour', 'usd_amount']
    ).properties(height=300)
    st.altair_chart(chart_hour, use_container_width=True)

# Latest transactions
st.markdown("---")
st.subheader("Recent Transactions (Last 24h)")
st.dataframe(df[['timestamp', 'user_id', 'country', 'currency', 'amount', 'usd_amount']].head(20).style.format({
    'amount': '${:,.2f}',
    'usd_amount': '${:,.2f}'
}))
