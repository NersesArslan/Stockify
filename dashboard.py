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

saas = pd.read_csv("data/saas.csv")
saas["Vertical"] = "SaaS"

cyber = pd.read_csv("data/cyber.csv")
cyber["Vertical"] = "Cybersecurity"
# --- Percentage columns per vertical ---
pct_cols_semis  = ["FCF Margin", "Op Margin", "Gross Margin", "Rev Growth (YoY)", "ROIC"]
pct_cols_default = ["FCF Margin", "Op Margin", "Gross Margin", "Rev Growth (YoY)"]

def format_pct(df, cols):
    display = df.copy()
    for col in cols:
        if col in display.columns:
            display[col] = pd.to_numeric(display[col], errors="coerce")
            display[col] = display[col].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else None)
    return display

# --- Tabs ---
tab1, tab2, tab3, tab4 = st.tabs(["Semiconductors", "Cloud", "Enterprise SaaS", "Cybersecurity"])

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
    st.dataframe(format_pct(filtered_cloud, pct_cols_default), use_container_width=True)

    st.subheader("EV/Revenue by Company")
    ev_df = filtered_cloud.dropna(subset=["EV/Revenue"])
    fig2  = px.bar(ev_df, x="Ticker", y="EV/Revenue", color="Archetype", title="EV/Revenue")
    st.plotly_chart(fig2, use_container_width=True)
with tab3:
    st.sidebar.header("Enterprise SaaS")
    saas_archetypes = saas["Archetype"].unique().tolist()
    selected_saas   = st.sidebar.multiselect("SaaS Archetype", saas_archetypes, default=saas_archetypes)
    filtered_saas   = saas[saas["Archetype"].isin(selected_saas)]

    st.subheader("Metrics Table")
    st.dataframe(format_pct(filtered_saas, pct_cols_default), use_container_width=True)

    st.subheader("Rule of 40 by Company")
    r40_df = filtered_saas.dropna(subset=["Rule of 40"])
    fig3   = px.bar(r40_df, x="Ticker", y="Rule of 40", color="Archetype", title="Rule of 40")
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("EV/Revenue by Company")
    ev_saas_df = filtered_saas.dropna(subset=["EV/Revenue"])
    fig4       = px.bar(ev_saas_df, x="Ticker", y="EV/Revenue", color="Archetype", title="EV/Revenue")
    st.plotly_chart(fig4, use_container_width=True)
with tab4:
    st.sidebar.header("Cybersecurity")
    cyber_archetypes = cyber["Archetype"].unique().tolist()
    selected_cyber   = st.sidebar.multiselect("Cyber Archetype", cyber_archetypes, default=cyber_archetypes)
    filtered_cyber   = cyber[cyber["Archetype"].isin(selected_cyber)]

    st.subheader("Metrics Table")
    st.dataframe(format_pct(filtered_cyber, pct_cols_default), use_container_width=True)

    st.subheader("Rule of 40 by Company")
    r40_cyber = filtered_cyber.dropna(subset=["Rule of 40"])
    fig5      = px.bar(r40_cyber, x="Ticker", y="Rule of 40", color="Archetype", title="Rule of 40")
    st.plotly_chart(fig5, use_container_width=True)

    st.subheader("EV/Revenue by Company")
    ev_cyber = filtered_cyber.dropna(subset=["EV/Revenue"])
    fig6     = px.bar(ev_cyber, x="Ticker", y="EV/Revenue", color="Archetype", title="EV/Revenue")
    st.plotly_chart(fig6, use_container_width=True)