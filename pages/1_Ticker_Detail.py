# Ticker Detail page — Streamlit auto-detects this sibling `pages/` dir next
# to dashboard.py and adds it to the sidebar nav, no routing code needed.
#
# Shell for the roadmap's "Live & Historical Price Comparison" feature: pick
# a ticker, see its current scorecard (shared with dashboard.py's search box
# via dashboard_common.py), and a price-vs-score chart to sanity-check the
# scoring model against what the market actually did. The score side of that
# chart is necessarily sparse today — it only has as many points as days the
# pipeline has run since the Price column was added (see
# .github/workflows/daily_pipeline.yml) — and fills in day by day.

import streamlit as st
import pandas as pd
import yfinance as yf
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from dashboard_common import load_all_scored, load_backlog_notes, render_stock_card

st.set_page_config(page_title="Ticker Detail", layout="wide")

all_df = load_all_scored()
backlog_notes = load_backlog_notes()

st.title("Ticker Detail")

tickers = sorted(all_df["Ticker"].dropna().unique().tolist())
ticker = st.selectbox("Ticker", tickers, index=None, placeholder="Choose a ticker...")

if not ticker:
    st.info("Pick a ticker above to see its scorecard and price history.")
    st.stop()

result = all_df[all_df["Ticker"] == ticker]
if len(result) == 0:
    st.error(f"Ticker '{ticker}' not found.")
    st.stop()

render_stock_card(result.iloc[0], backlog_notes)

st.divider()
st.subheader("Price vs. Score History")
st.caption(
    "Stress-test the score against reality: does a high Quality/Valuation score actually "
    "track with how the market prices the stock over time? The score line is sparse — it "
    "only has one point per day the daily pipeline has run since price logging started — "
    "and fills in day by day. Price history can't be backfilled for past scores."
)

try:
    price_hist = yf.Ticker(ticker).history(period="1y")
except Exception as e:
    price_hist = pd.DataFrame()
    st.warning(f"Couldn't fetch price history from yfinance: {e}")

try:
    score_hist = pd.read_csv("data/history.csv")
    score_hist = score_hist[score_hist["Ticker"] == ticker].sort_values("run_date")
    score_hist["run_date"] = pd.to_datetime(score_hist["run_date"])
except (FileNotFoundError, KeyError):
    score_hist = pd.DataFrame()

if price_hist.empty and score_hist.empty:
    st.info("No price or score history available yet for this ticker.")
else:
    if not price_hist.empty:
        latest_price = price_hist["Close"].iloc[-1]
        st.metric("Latest Price (yfinance, may be delayed)", f"${latest_price:,.2f}")

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    if not price_hist.empty:
        fig.add_trace(
            go.Scatter(x=price_hist.index, y=price_hist["Close"], name="Price ($)", line=dict(color="#3498db")),
            secondary_y=False,
        )
    if not score_hist.empty:
        fig.add_trace(
            go.Scatter(
                x=score_hist["run_date"], y=score_hist["Quality Score"],
                name="Quality Score", mode="lines+markers", line=dict(color="#2ecc71"),
            ),
            secondary_y=True,
        )
        fig.add_trace(
            go.Scatter(
                x=score_hist["run_date"], y=score_hist["Valuation Score"],
                name="Valuation Score", mode="lines+markers", line=dict(color="#f39c12"),
            ),
            secondary_y=True,
        )

    fig.update_layout(title=f"{ticker} — Price vs. Score (1Y)", height=500, hovermode="x unified")
    fig.update_yaxes(title_text="Price ($)", secondary_y=False)
    fig.update_yaxes(title_text="Score (0-100)", range=[0, 100], secondary_y=True)
    st.plotly_chart(fig, use_container_width=True)
