import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Stock Screener", layout="wide")
st.title("Stock Screener")

# --- Load data ---
semis = pd.read_csv("data/semis_scored.csv")
semis["Vertical"] = "Semiconductors"

cloud = pd.read_csv("data/cloud_scored.csv")
cloud["Vertical"] = "Cloud"

saas = pd.read_csv("data/saas_scored.csv")
saas["Vertical"] = "SaaS"

cyber = pd.read_csv("data/cyber_scored.csv")
cyber["Vertical"] = "Cybersecurity"

# --- Percentage columns per vertical ---
pct_cols_semis  = ["FCF Margin", "Op Margin", "Gross Margin", "Rev Growth (YoY)", "ROIC"]
pct_cols_default = ["FCF Margin", "Op Margin", "Gross Margin", "Rev Growth (YoY)"]

color_map = {
    "Buy":               "#2ecc71",
    "Watch":             "#f39c12",
    "Avoid":             "#e67e22",
    "Pass":              "#e74c3c",
    "Insufficient Data": "#95a5a6",
}

def format_pct(df, cols):
    display = df.copy()
    for col in cols:
        if col in display.columns:
            display[col] = pd.to_numeric(display[col], errors="coerce")
            display[col] = display[col].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else None)
    return display

def scatter_plot(df, title):
    scatter_df = df.dropna(subset=["Quality Score", "Valuation Score"])
    fig = px.scatter(
        scatter_df,
        x="Valuation Score",
        y="Quality Score",
        color="Verdict",
        color_discrete_map=color_map,
        hover_name="Ticker",
        hover_data=["Archetype", "Name"],
        title=title,
        labels={
            "Valuation Score": "Valuation Score (higher = cheaper)",
            "Quality Score":   "Quality Score (higher = better business)",
        }
    )
    fig.add_hline(y=60, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=60, line_dash="dash", line_color="gray", opacity=0.5)
    return fig

def verdict_chart(df, title):
    counts = df["Verdict"].value_counts().reset_index()
    counts.columns = ["Verdict", "Count"]
    return px.bar(counts, x="Verdict", y="Count", color="Verdict",
                  color_discrete_map=color_map, title=title)

# --- Tabs ---
tab1, tab2, tab3, tab4 = st.tabs(["Semiconductors", "Cloud", "Enterprise SaaS", "Cybersecurity"])

with tab1:
    st.sidebar.header("Semiconductors")
    semi_archetypes = semis["Archetype"].unique().tolist()
    selected_semis  = st.sidebar.multiselect("Semi Archetype", semi_archetypes, default=semi_archetypes)
    filtered_semis  = semis[semis["Archetype"].isin(selected_semis)]

    st.subheader("Metrics Table")
    st.dataframe(format_pct(filtered_semis, pct_cols_semis), use_container_width=True)

    st.subheader("Quality & Valuation Scores")
    st.dataframe(filtered_semis[["Ticker", "Name", "Archetype", "Quality Score", "Valuation Score", "Verdict"]], use_container_width=True)

    st.subheader("Quality vs Valuation")
    st.plotly_chart(scatter_plot(filtered_semis, "Semiconductors — Quality vs Valuation"), use_container_width=True)

    st.subheader("Verdict Distribution")
    st.plotly_chart(verdict_chart(filtered_semis, "Semiconductors — Verdict Distribution"), use_container_width=True)

    st.subheader("ROIC by Company")
    roic_df = filtered_semis.dropna(subset=["ROIC"])
    fig_roic = px.bar(roic_df, x="Ticker", y="ROIC", color="Archetype", title="ROIC %")
    st.plotly_chart(fig_roic, use_container_width=True)

with tab2:
    st.sidebar.header("Cloud")
    cloud_archetypes = cloud["Archetype"].unique().tolist()
    selected_cloud   = st.sidebar.multiselect("Cloud Archetype", cloud_archetypes, default=cloud_archetypes)
    filtered_cloud   = cloud[cloud["Archetype"].isin(selected_cloud)]

    st.subheader("Metrics Table")
    st.dataframe(format_pct(filtered_cloud, pct_cols_default), use_container_width=True)

    st.subheader("Quality & Valuation Scores")
    st.dataframe(filtered_cloud[["Ticker", "Name", "Archetype", "Quality Score", "Valuation Score", "Verdict"]], use_container_width=True)

    st.subheader("Quality vs Valuation")
    st.plotly_chart(scatter_plot(filtered_cloud, "Cloud — Quality vs Valuation"), use_container_width=True)

    st.subheader("Verdict Distribution")
    st.plotly_chart(verdict_chart(filtered_cloud, "Cloud — Verdict Distribution"), use_container_width=True)

    st.subheader("EV/Revenue by Company")
    ev_df = filtered_cloud.dropna(subset=["EV/Revenue"])
    fig_ev = px.bar(ev_df, x="Ticker", y="EV/Revenue", color="Archetype", title="EV/Revenue")
    st.plotly_chart(fig_ev, use_container_width=True)

with tab3:
    st.sidebar.header("Enterprise SaaS")
    saas_archetypes = saas["Archetype"].unique().tolist()
    selected_saas   = st.sidebar.multiselect("SaaS Archetype", saas_archetypes, default=saas_archetypes)
    filtered_saas   = saas[saas["Archetype"].isin(selected_saas)]

    st.subheader("Metrics Table")
    st.dataframe(format_pct(filtered_saas, pct_cols_default), use_container_width=True)

    st.subheader("Quality & Valuation Scores")
    st.dataframe(filtered_saas[["Ticker", "Name", "Archetype", "Quality Score", "Valuation Score", "Verdict"]], use_container_width=True)

    st.subheader("Quality vs Valuation")
    st.plotly_chart(scatter_plot(filtered_saas, "Enterprise SaaS — Quality vs Valuation"), use_container_width=True)

    st.subheader("Verdict Distribution")
    st.plotly_chart(verdict_chart(filtered_saas, "Enterprise SaaS — Verdict Distribution"), use_container_width=True)

    st.subheader("Rule of 40 by Company")
    r40_df = filtered_saas.dropna(subset=["Rule of 40"])
    fig_r40 = px.bar(r40_df, x="Ticker", y="Rule of 40", color="Archetype", title="Rule of 40")
    st.plotly_chart(fig_r40, use_container_width=True)

with tab4:
    st.sidebar.header("Cybersecurity")
    cyber_archetypes = cyber["Archetype"].unique().tolist()
    selected_cyber   = st.sidebar.multiselect("Cyber Archetype", cyber_archetypes, default=cyber_archetypes)
    filtered_cyber   = cyber[cyber["Archetype"].isin(selected_cyber)]

    st.subheader("Metrics Table")
    st.dataframe(format_pct(filtered_cyber, pct_cols_default), use_container_width=True)

    st.subheader("Quality & Valuation Scores")
    st.dataframe(filtered_cyber[["Ticker", "Name", "Archetype", "Quality Score", "Valuation Score", "Verdict"]], use_container_width=True)

    st.subheader("Quality vs Valuation")
    st.plotly_chart(scatter_plot(filtered_cyber, "Cybersecurity — Quality vs Valuation"), use_container_width=True)

    st.subheader("Verdict Distribution")
    st.plotly_chart(verdict_chart(filtered_cyber, "Cybersecurity — Verdict Distribution"), use_container_width=True)

    st.subheader("Rule of 40 by Company")
    r40_cyber = filtered_cyber.dropna(subset=["Rule of 40"])
    fig_r40c  = px.bar(r40_cyber, x="Ticker", y="Rule of 40", color="Archetype", title="Rule of 40")
    st.plotly_chart(fig_r40c, use_container_width=True)