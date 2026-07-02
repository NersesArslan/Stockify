import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Semiconductor Screener", layout="wide")
st.title("Semiconductor Stock Screener")

# Load data
df = pd.read_csv("data/semis.csv")

# Sidebar filter
archetypes = df["Archetype"].unique().tolist()
selected = st.sidebar.multiselect("Archetype", archetypes, default=archetypes)
filtered = df[df["Archetype"].isin(selected)]

# Format percentage columns for display only
pct_cols = ["FCF Margin", "Op Margin", "Gross Margin", "Rev Growth (YoY)", "ROIC"]
display_df = filtered.copy()
for col in pct_cols:
    display_df[col] = display_df[col].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else None)

# Table
st.subheader("Metrics Table")
st.dataframe(display_df, use_container_width=True)

# ROIC bar chart
st.subheader("ROIC by Company")
fig = px.bar(filtered, x="Ticker", y="ROIC", color="Archetype", title="ROIC %")
st.plotly_chart(fig, use_container_width=True)

