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

all_df = pd.concat([
    pd.read_csv("data/semis_scored.csv").assign(Vertical="Semiconductors"),
    pd.read_csv("data/cloud_scored.csv").assign(Vertical="Cloud"),
    pd.read_csv("data/saas_scored.csv").assign(Vertical="SaaS"),
    pd.read_csv("data/cyber_scored.csv").assign(Vertical="Cybersecurity"),
], ignore_index=True)

# --- Percentage columns per vertical ---
pct_cols_semis   = ["FCF Margin", "Op Margin", "Gross Margin", "Rev Growth (YoY)", "ROIC", "Rev CAGR (3Y)"]
pct_cols_default = ["FCF Margin", "Op Margin", "Gross Margin", "Rev Growth (YoY)", "Rev CAGR (3Y)"]

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

def show_analysis(df, title="AI Analysis"):
    if "AI Analysis" not in df.columns:
        st.info("AI Analysis not yet generated for this vertical.")
        return
    analysis_df = df[df["AI Analysis"].notna()].copy()
    if len(analysis_df) == 0:
        return
    st.subheader(title)
    for _, row in analysis_df.iterrows():
        verdict_color = color_map.get(row["Verdict"], "#95a5a6")
        with st.expander(f"{row['Ticker']} — {row['Name']} | {row['Verdict']}"):
            st.markdown(row["AI Analysis"])
# --- Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Semiconductors", "Cloud", "Enterprise SaaS", "Cybersecurity", "All Companies"])

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
    show_analysis(filtered_semis, "AI Analysis — Semiconductors")
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
    show_analysis(filtered_cloud, "AI Analysis — Cloud")
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
    show_analysis(filtered_saas, "AI Analysis — Enterprise SaaS")
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
    show_analysis(filtered_cyber, "AI Analysis — Cybersecurity")
    st.subheader("Verdict Distribution")
    st.plotly_chart(verdict_chart(filtered_cyber, "Cybersecurity — Verdict Distribution"), use_container_width=True)

    st.subheader("Rule of 40 by Company")
    r40_cyber = filtered_cyber.dropna(subset=["Rule of 40"])
    fig_r40c  = px.bar(r40_cyber, x="Ticker", y="Rule of 40", color="Archetype", title="Rule of 40")
    st.plotly_chart(fig_r40c, use_container_width=True)
with tab5:
    st.sidebar.header("All Companies")
    all_verticals = all_df["Vertical"].unique().tolist()
    selected_all  = st.sidebar.multiselect("Vertical", all_verticals, default=all_verticals)
    filtered_all  = all_df[all_df["Vertical"].isin(selected_all)]

    # Summary stats
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Companies", len(filtered_all))
    col2.metric("Buy",   len(filtered_all[filtered_all["Verdict"] == "Buy"]))
    col3.metric("Watch", len(filtered_all[filtered_all["Verdict"] == "Watch"]))
    col4.metric("Pass / Avoid", len(filtered_all[filtered_all["Verdict"].isin(["Pass", "Avoid", "Insufficient Data"])]))

    # Cross-vertical scatter plot
    st.subheader("Quality vs Valuation — All Companies")
    scatter_all = filtered_all.dropna(subset=["Quality Score", "Valuation Score"])
    fig_all = px.scatter(
        scatter_all,
        x="Valuation Score",
        y="Quality Score",
        color="Vertical",
        symbol="Verdict",
        hover_name="Ticker",
        hover_data=["Name", "Archetype", "Vertical", "Verdict"],
        title="All Companies — Quality vs Valuation",
        labels={
            "Valuation Score": "Valuation Score (higher = cheaper)",
            "Quality Score":   "Quality Score (higher = better business)",
        },
        height=600,
    )
    fig_all.add_hline(y=60, line_dash="dash", line_color="gray", opacity=0.5)
    fig_all.add_vline(x=60, line_dash="dash", line_color="gray", opacity=0.5)
    st.plotly_chart(fig_all, use_container_width=True)
    show_analysis(filtered_all, "AI Analysis — All Companies")
    # Verdict distribution across all verticals
    st.subheader("Verdict Distribution — All Companies")
    verdict_all = filtered_all["Verdict"].value_counts().reset_index()
    verdict_all.columns = ["Verdict", "Count"]
    fig_verdict_all = px.bar(
        verdict_all,
        x="Verdict",
        y="Count",
        color="Verdict",
        color_discrete_map=color_map,
        title="Verdict Distribution — All Companies"
    )
    st.plotly_chart(fig_verdict_all, use_container_width=True)

    # Top Buy candidates table
    st.subheader("Top Buy Candidates")
    buys = filtered_all[filtered_all["Verdict"] == "Buy"].sort_values("Quality Score", ascending=False)
    st.dataframe(
        buys[["Ticker", "Name", "Vertical", "Archetype", "Quality Score", "Valuation Score", "Verdict"]],
        use_container_width=True
    )