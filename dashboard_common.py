# Shared loading/rendering logic used by both dashboard.py (the main
# tab-based screener) and pages/1_Ticker_Detail.py (the per-ticker page).
# Kept here so the two don't duplicate the same ~60 lines of card-rendering.

import pandas as pd
import streamlit as st


def load_all_scored():
    """Concat every vertical's *_scored.csv into one DataFrame, tagged with
    a Vertical column. Same shape dashboard.py has loaded inline since the
    beginning — factored out so pages/1_Ticker_Detail.py can reuse it."""
    semis = pd.read_csv("data/semis_scored.csv")
    semis["Vertical"] = "Semiconductors"

    cloud = pd.read_csv("data/cloud_scored.csv")
    cloud["Vertical"] = "Cloud"

    saas = pd.read_csv("data/saas_scored.csv")
    saas["Vertical"] = "SaaS"

    cyber = pd.read_csv("data/cyber_scored.csv")
    cyber["Vertical"] = "Cybersecurity"

    return pd.concat([semis, cloud, saas, cyber], ignore_index=True)


def load_backlog_notes():
    """Latest quarterly backlog/book-to-bill research note per ticker
    (Data_Center_Infra archetype only, populated by backlog.py). Empty
    DataFrame if the file hasn't been generated yet."""
    try:
        backlog_notes = pd.read_csv("data/backlog_notes.csv")
        return (
            backlog_notes.sort_values("run_date")
            .groupby("Ticker", as_index=False)
            .last()
            .set_index("Ticker")
        )
    except (FileNotFoundError, KeyError):
        return pd.DataFrame()


def render_stock_card(row, backlog_notes):
    """The per-stock detail block: verdict, Growth Stage disclaimer,
    Quality/Valuation scores, key metrics grid, AI analysis, backlog note.
    Used by dashboard.py's ticker search and pages/1_Ticker_Detail.py."""
    verdict_colors = {"Buy": "green", "Watch": "orange", "Avoid": "orange", "Pass": "red"}
    color = verdict_colors.get(row["Verdict"], "gray")

    with st.container(border=True):
        name_col, verdict_col = st.columns([3, 1])
        with name_col:
            st.markdown(f"### {row['Name']} ({row['Ticker']})")
            st.markdown(f"{row['Archetype']} | {row['Vertical']} | AI Exposure: **{row['AI Exposure']}**")
        with verdict_col:
            st.markdown(f"#### Verdict: :{color}[{row['Verdict']}]")

        if row.get("Growth Stage") in (True, "True"):
            st.warning(
                "🚧 **Growth-stage company** — trailing financial metrics may understate "
                "investment case. Contracted/backlog revenue not reflected in scores."
            )

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

        if row["Ticker"] in backlog_notes.index:
            note = backlog_notes.loc[row["Ticker"]]
            # st.markdown renders `$...$` as LaTeX math — escape dollar signs
            # in free-text fields so "$9.5 billion" doesn't get mangled.
            esc = lambda s: str(s).replace("$", "\\$") if pd.notna(s) else "Not disclosed"
            st.divider()
            st.markdown(f"**Backlog** (as of {esc(note['As_Of'])}, researched {note['run_date']})")
            bl_col1, bl_col2 = st.columns(2)
            bl_col1.markdown(f"**Backlog:** {esc(note['Backlog'])}")
            bl_col2.markdown(f"**Book-to-Bill:** {esc(note['Book_to_Bill'])}")
            if pd.notna(note["Summary"]):
                st.markdown(esc(note["Summary"]))
            if pd.notna(note["Source"]):
                st.caption(f"Source: {note['Source']}")
