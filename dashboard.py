import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Stock Screener", layout="wide")

# --- Load data ---
semis = pd.read_csv("data/semis_scored.csv")
semis["Vertical"] = "Semiconductors"

cloud = pd.read_csv("data/cloud_scored.csv")
cloud["Vertical"] = "Cloud"

saas = pd.read_csv("data/saas_scored.csv")
saas["Vertical"] = "SaaS"

cyber = pd.read_csv("data/cyber_scored.csv")
cyber["Vertical"] = "Cybersecurity"

all_df = pd.concat([semis, cloud, saas, cyber], ignore_index=True)

# --- Header: title + ticker search, always visible above the tabs ---
title_col, search_col = st.columns([3, 1])
with title_col:
    st.title("Stock Screener")
with search_col:
    st.write("")
    st.write("")
    search_ticker = st.text_input(
        "Search ticker", placeholder="🔍 Search ticker, e.g. NVDA", label_visibility="collapsed"
    ).upper().strip()

# --- Show last updated timestamp (oldest across all verticals) ---
timestamps = []
for name in ["semis", "cloud", "saas", "cyber"]:
    try:
        raw = pd.read_csv(f"data/{name}.csv")
        timestamps.append(raw["Last Updated"].iloc[0])
    except (FileNotFoundError, KeyError, IndexError):
        pass
if timestamps:
    st.caption(f"Data last updated: {min(timestamps)}")

if search_ticker:
    result = all_df[all_df["Ticker"] == search_ticker]
    if len(result) == 0:
        st.error(f"Ticker '{search_ticker}' not found.")
    else:
        row = result.iloc[0]
        verdict_colors = {"Buy": "green", "Watch": "orange", "Avoid": "orange", "Pass": "red"}
        color = verdict_colors.get(row["Verdict"], "gray")

        with st.container(border=True):
            name_col, verdict_col = st.columns([3, 1])
            with name_col:
                st.markdown(f"### {row['Name']} ({row['Ticker']})")
                st.markdown(f"{row['Archetype']} | {row['Vertical']} | AI Exposure: **{row['AI Exposure']}**")
            with verdict_col:
                st.markdown(f"#### Verdict: :{color}[{row['Verdict']}]")

            score_col1, score_col2 = st.columns(2)
            score_col1.metric("Quality Score", row["Quality Score"])
            score_col2.metric("Valuation Score", row["Valuation Score"])

            st.markdown("**Key Metrics**")
            metrics = [
                ("EV/FCF", row.get("EV/FCF")),
                ("FCF Margin", row.get("FCF Margin")),
                ("Op Margin", row.get("Op Margin")),
                ("Gross Margin", row.get("Gross Margin")),
                ("GM Trend (3Y)", row.get("GM Trend (3Y)")),
                ("Rev CAGR (3Y)", row.get("Rev CAGR (3Y)")),
                ("ROIC", row.get("ROIC")),
                ("ROIC Trend (3Y)", row.get("ROIC Trend (3Y)")),
                ("FCF Margin Trend (3Y)", row.get("FCF Margin Trend (3Y)")),
                ("R&D Intensity", row.get("R&D Intensity")),
                ("Revenue per Employee ($K)", row.get("Revenue per Employee ($K)")),
                ("Net Debt/EBITDA", row.get("Net Debt/EBITDA")),
            ]
            present_metrics = [(l, v) for l, v in metrics if v is not None and str(v) != "nan"]
            metric_cols = st.columns(4)
            for i, (label, value) in enumerate(present_metrics):
                metric_cols[i % 4].markdown(f"**{label}:** {value}")

            analysis = row.get("AI Analysis")
            if analysis and str(analysis) != "nan":
                st.divider()
                st.markdown("**AI Analysis**")
                st.markdown(analysis)

st.divider()

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

ai_exposure_color_map = {
    "Enabler":    "#2ecc71",
    "Compounder": "#3498db",
    "Disruptor":  "#9b59b6",
    "Exposed":    "#e74c3c",
    "Neutral":    "#95a5a6",
    "Unknown":    "#7f8c8d",
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

# --- Per-vertical tab config: sidebar filter -> table -> scatter -> verdict chart -> extra metric bar ---
VERTICAL_TABS = [
    {
        "label": "Semiconductors", "df": semis, "pct_cols": pct_cols_semis,
        "extra_col": "ROIC", "extra_subheader": "ROIC by Company", "extra_chart_title": "ROIC %",
    },
    {
        "label": "Cloud", "df": cloud, "pct_cols": pct_cols_default,
        "extra_col": "EV/Revenue", "extra_subheader": "EV/Revenue by Company", "extra_chart_title": "EV/Revenue",
    },
    {
        "label": "Enterprise SaaS", "df": saas, "pct_cols": pct_cols_default,
        "extra_col": "Rule of 40", "extra_subheader": "Rule of 40 by Company", "extra_chart_title": "Rule of 40",
    },
    {
        "label": "Cybersecurity", "df": cyber, "pct_cols": pct_cols_default,
        "extra_col": "Rule of 40", "extra_subheader": "Rule of 40 by Company", "extra_chart_title": "Rule of 40",
    },
]

def render_vertical_tab(cfg):
    df, label = cfg["df"], cfg["label"]

    st.sidebar.header(label)
    archetypes = df["Archetype"].unique().tolist()
    selected   = st.sidebar.multiselect(f"{label} Archetype", archetypes, default=archetypes)
    filtered   = df[df["Archetype"].isin(selected)]

    st.subheader("Metrics Table")
    st.dataframe(format_pct(filtered, cfg["pct_cols"]), use_container_width=True)

    st.subheader("Quality & Valuation Scores")
    st.dataframe(filtered[["Ticker", "Name", "Archetype", "Quality Score", "Valuation Score", "Verdict"]], use_container_width=True)

    st.subheader("Quality vs Valuation")
    st.plotly_chart(scatter_plot(filtered, f"{label} — Quality vs Valuation"), use_container_width=True)
    show_analysis(filtered, f"AI Analysis — {label}")
    st.subheader("Verdict Distribution")
    st.plotly_chart(verdict_chart(filtered, f"{label} — Verdict Distribution"), use_container_width=True)

    st.subheader(cfg["extra_subheader"])
    extra_df = filtered.dropna(subset=[cfg["extra_col"]])
    fig_extra = px.bar(extra_df, x="Ticker", y=cfg["extra_col"], color="Archetype", title=cfg["extra_chart_title"])
    st.plotly_chart(fig_extra, use_container_width=True)

# --- Tabs ---
tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Home", "Semiconductors", "Cloud", "Enterprise SaaS", "Cybersecurity", "All Companies"]
)

with tab0:
    st.title("Find the real winners of the AI revolution")
    
    st.markdown("""
    A quality-first stock screener for semiconductor and tech investors. Built on the belief 
    that AI infrastructure represents a once-in-a-generation investment opportunity — and that 
    separating the genuine beneficiaries from the narrative hype requires more than a price chart.
    
    This screener taxonomizes semiconductor and tech companies by archetype — Foundry, Fabless, 
    Equipment, Enterprise SaaS, Cybersecurity and more — and evaluates each company using 
    archetype-specific metrics. A Foundry is not scored like a SaaS company. An Enabler is not 
    valued like a Disruptor. Quality comes first. Valuation comes second. AI exposure tells you 
    whether the tailwind is structural or narrative.
    """)

    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Quality First")
        st.markdown("Companies scored on profitability, cash generation, moat durability and trajectory across 18 industry archetypes.")
    with col2:
        st.subheader("Valuation Second")
        st.markdown("Quality score must clear 60 before valuation matters. High quality at a fair price beats cheap mediocrity every time.")
    with col3:
        st.subheader("AI Exposure")
        st.markdown("Every company classified as Enabler, Compounder, Disruptor, Exposed or Neutral — because AI is a tailwind for some and a headwind for others.")

    st.divider()

    st.subheader("How to read the verdicts")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.success("**Buy** — High quality, reasonable price")
    with col2:
        st.warning("**Watch** — High quality, expensive. Wait for a better entry.")
    with col3:
        st.warning("**Avoid** — Low quality, cheap. Value trap.")
    with col4:
        st.error("**Pass** — Low quality, expensive. Stay away.")

    st.divider()

    st.subheader("All Companies — Quality vs Valuation")
    scatter_home = all_df.dropna(subset=["Quality Score", "Valuation Score"])
    fig_home = px.scatter(
        scatter_home,
        x="Valuation Score",
        y="Quality Score",
        color="AI Exposure",
        hover_name="Ticker",
        hover_data=["Name", "Archetype", "Verdict"],
        title="Quality vs Valuation — colored by AI Exposure",
        labels={
            "Valuation Score": "Valuation Score (higher = cheaper)",
            "Quality Score":   "Quality Score (higher = better business)",
        },
        height=500,
    )
    fig_home.add_hline(y=60, line_dash="dash", line_color="gray", opacity=0.5)
    fig_home.add_vline(x=60, line_dash="dash", line_color="gray", opacity=0.5)
    st.plotly_chart(fig_home, use_container_width=True)

for tab, cfg in zip([tab1, tab2, tab3, tab4], VERTICAL_TABS):
    with tab:
        render_vertical_tab(cfg)

with tab5:
    st.sidebar.header("All Companies")
    all_verticals = all_df["Vertical"].unique().tolist()
    selected_all  = st.sidebar.multiselect("Vertical", all_verticals, default=all_verticals)
    all_ai_exposures = all_df["AI Exposure"].unique().tolist()
    selected_ai_exposures = st.sidebar.multiselect("AI Exposure", all_ai_exposures, default=all_ai_exposures)
    filtered_all  = all_df[
        all_df["Vertical"].isin(selected_all) &
        all_df["AI Exposure"].isin(selected_ai_exposures)
    ]

    # Summary stats
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Companies", len(filtered_all))
    col2.metric("Buy",   len(filtered_all[filtered_all["Verdict"] == "Buy"]))
    col3.metric("Watch", len(filtered_all[filtered_all["Verdict"] == "Watch"]))
    col4.metric("Pass / Avoid", len(filtered_all[filtered_all["Verdict"].isin(["Pass", "Avoid", "Insufficient Data"])]))

    # Cross-vertical scatter plots
    def all_companies_scatter(df, color_field, color_map_arg, title):
        scatter_df = df.dropna(subset=["Quality Score", "Valuation Score"])
        fig = px.scatter(
            scatter_df,
            x="Valuation Score",
            y="Quality Score",
            color=color_field,
            color_discrete_map=color_map_arg,
            symbol="Verdict",
            hover_name="Ticker",
            hover_data=["Name", "Archetype", "Vertical", "Verdict", "AI Exposure"],
            title=title,
            labels={
                "Valuation Score": "Valuation Score (higher = cheaper)",
                "Quality Score":   "Quality Score (higher = better business)",
            },
            height=600,
        )
        fig.add_hline(y=60, line_dash="dash", line_color="gray", opacity=0.5)
        fig.add_vline(x=60, line_dash="dash", line_color="gray", opacity=0.5)
        return fig

    st.subheader("Quality vs Valuation — All Companies")
    scatter_col1, scatter_col2 = st.columns(2)
    with scatter_col1:
        st.plotly_chart(
            all_companies_scatter(filtered_all, "AI Exposure", ai_exposure_color_map, "Colored by AI Exposure"),
            use_container_width=True,
        )
    with scatter_col2:
        st.plotly_chart(
            all_companies_scatter(filtered_all, "Vertical", None, "Colored by Vertical"),
            use_container_width=True,
        )
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