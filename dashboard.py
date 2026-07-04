import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Stock Screener", layout="wide")
st.title("Stock Screener")

# --- Load data ---
semis = pd.read_csv("data/semis.csv")
semis["Vertical"] = "Semiconductors"

cloud = pd.read_csv("data/cloud.csv")
cloud["Vertical"] = "Cloud"

# --- Percentage columns per vertical ---
pct_cols_semis  = ["FCF Margin", "Op Margin", "Gross Margin", "Rev Growth (YoY)", "ROIC"]
pct_cols_cloud  = ["FCF Margin", "Op Margin", "Gross Margin", "Rev Growth (YoY)"]

def format_pct(df, cols):
    display = df.copy()
    for col in cols:
        if col in display.columns:
            display[col] = pd.to_numeric(display[col], errors="coerce")
            display[col] = display[col].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else None)
    return display

# --- Tabs ---
tab1, tab2 = st.tabs(["Semiconductors", "Cloud"])

with tab1:
    st.sidebar.header("Semiconductors")
    semi_archetypes = semis["Archetype"].unique().tolist()
    selected_semis  = st.sidebar.multiselect("Semi Archetype", semi_archetypes, default=semi_archetypes)
    filtered_semis  = semis[semis["Archetype"].isin(selected_semis)]

    st.subheader("Metrics Table")
    st.dataframe(format_pct(filtered_semis, pct_cols_semis), use_container_width=True)

    st.subheader("ROIC by Company")
    roic_df = filtered_semis.dropna(subset=["ROIC"])
    fig1 = px.bar(roic_df, x="Ticker", y="ROIC", color="Archetype", title="ROIC %")
    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    st.sidebar.header("Cloud")
    cloud_archetypes = cloud["Archetype"].unique().tolist()
    selected_cloud   = st.sidebar.multiselect("Cloud Archetype", cloud_archetypes, default=cloud_archetypes)
    filtered_cloud   = cloud[cloud["Archetype"].isin(selected_cloud)]

    st.subheader("Metrics Table")
    st.dataframe(format_pct(filtered_cloud, pct_cols_cloud), use_container_width=True)

    st.subheader("EV/Revenue by Company")
    ev_df = filtered_cloud.dropna(subset=["EV/Revenue"])
    fig2  = px.bar(ev_df, x="Ticker", y="EV/Revenue", color="Archetype", title="EV/Revenue")
    st.plotly_chart(fig2, use_container_width=True)