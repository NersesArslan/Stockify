# backlog.py
#
# Quarterly backlog / book-to-bill tracker for the Data_Center_Infra archetype.
#
# Backlog isn't a standardized GAAP field, so no fundamentals API (yfinance,
# FMP, etc.) exposes it — it only exists in earnings releases and 10-Q/10-K
# narrative disclosure. This uses Claude with the web search tool to look it
# up per ticker instead of trying to build a scraper/fetch pipeline for it.
#
# Deliberately NOT wired into main.py's FETCH/SCORE/ANALYZE flags — backlog
# is disclosed quarterly, not on every pipeline run. Run this manually after
# each earnings season: `python backlog.py`
#
# Results are qualitative context, not a scored metric — see data/backlog_notes.csv
# (gitignored, append-only, same pattern as data/history.csv).

import os
import re
import datetime
import anthropic
import pandas as pd
from dotenv import load_dotenv
from verticals import cloud

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are a research assistant finding the most recently disclosed
backlog and book-to-bill figures for industrial/hardware companies, from their own
investor materials (earnings releases, 10-Q/10-K, investor presentations).

Only report numbers the company has actually disclosed — do not estimate or infer
a figure that wasn't stated. If a company doesn't disclose backlog or book-to-bill
numerically, say so plainly rather than approximating from other data.

Respond with ONLY the five lines below — no preamble, no acknowledgment of the
search, no text before or after them. Keep BACKLOG and BOOK_TO_BILL to just the
figure itself — no commentary or caveats in those two fields, even if the company
doesn't disclose a clean number; put all nuance and context in SUMMARY instead:
BACKLOG: <dollar figure and unit, e.g. "$9.5 billion" — or exactly "Not disclosed">
BOOK_TO_BILL: <ratio, e.g. "1.4x" — or exactly "Not disclosed">
AS_OF: <date or fiscal quarter the figure is as-of>
SOURCE: <URL>
SUMMARY: <one or two sentences of context — trend direction, growth driver, and
  what the company disclosed instead if BACKLOG/BOOK_TO_BILL is "Not disclosed">"""

# Not anchored to line-start on purpose — the model occasionally prepends a
# preamble sentence with no newline before the first label (e.g. "...disclosures.
# BACKLOG: ..."), which would silently fail to match a ^-anchored pattern.
FIELD_PATTERN = re.compile(r"(BACKLOG|BOOK_TO_BILL|AS_OF|SOURCE|SUMMARY):\s*(.*)")


def build_prompt(ticker, name):
    return (
        f"Find the most recently disclosed backlog and book-to-bill figures for "
        f"{name} ({ticker}), from their most recent earnings release or SEC filing."
    )


def parse_response(text):
    fields = {"BACKLOG": None, "BOOK_TO_BILL": None, "AS_OF": None, "SOURCE": None, "SUMMARY": None}
    for key, value in FIELD_PATTERN.findall(text):
        fields[key] = value.strip() or None
    return fields


def research_backlog(ticker, name):
    """Look up one ticker's backlog/book-to-bill via Claude + web search."""
    try:
        response = client.messages.create(
            model="claude-opus-5",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            output_config={"effort": "low"},
            tools=[{"type": "web_search_20260209", "name": "web_search", "max_uses": 5}],
            messages=[{"role": "user", "content": build_prompt(ticker, name)}],
        )
        text = "".join(block.text for block in response.content if block.type == "text")
        fields = parse_response(text)
    except Exception as e:
        fields = {"BACKLOG": None, "BOOK_TO_BILL": None, "AS_OF": None, "SOURCE": None,
                   "SUMMARY": f"Lookup error: {e}"}

    return {
        "run_date":     datetime.date.today().strftime("%Y-%m-%d"),
        "Ticker":       ticker,
        "Backlog":      fields["BACKLOG"],
        "Book_to_Bill": fields["BOOK_TO_BILL"],
        "As_Of":        fields["AS_OF"],
        "Source":       fields["SOURCE"],
        "Summary":      fields["SUMMARY"],
    }


def run():
    tickers = cloud.UNIVERSE.get("Data_Center_Infra", [])
    try:
        names = pd.read_csv("data/cloud_scored.csv").set_index("Ticker")["Name"].to_dict()
    except (FileNotFoundError, KeyError):
        names = {}

    rows = []
    for ticker in tickers:
        name = names.get(ticker, ticker)
        print(f"Researching backlog for {ticker}...")
        rows.append(research_backlog(ticker, name))

    out = pd.DataFrame(rows)
    print(out.to_string(index=False))

    path = "data/backlog_notes.csv"
    out.to_csv(path, mode="a", header=not os.path.exists(path), index=False)
    print(f"\nAppended {len(out)} rows to {path}")


if __name__ == "__main__":
    run()
