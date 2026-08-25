# backlog.py
#
# Quarterly contracted-revenue tracker for Data_Center_Infra and Power_Campus.
#
# Covers both "backlog" in the traditional manufacturing-order-book sense
# (VRT/SMCI/CLS) and its equivalents for capacity developers — ARR-under-
# contract, signed lease value (IREN/APLD) — since neither is a standardized
# GAAP field. No fundamentals API (yfinance, FMP, etc.) exposes any of this —
# it only exists in earnings releases and 10-Q/10-K narrative disclosure. This
# uses Claude with the web search tool to look it up per ticker instead of
# trying to build a scraper/fetch pipeline for it. More load-bearing for
# Power_Campus than Data_Center_Infra: IREN/APLD's entire investment case is
# the gap between trailing financials and contracted-but-not-yet-live revenue.
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

ARCHETYPES = ["Data_Center_Infra", "Power_Campus"]

SYSTEM_PROMPT = """You are a research assistant finding the most recently disclosed
figures for future revenue a company has already secured but not yet recognized,
from its own investor materials (earnings releases, 10-Q/10-K, investor presentations).

This takes different forms depending on the business: a traditional manufacturing
order backlog and book-to-bill ratio (industrial/hardware companies); ARR already
under contract (subscription/consumption businesses); or the total value of signed,
long-term, take-or-pay lease agreements (data-center capacity developers/landlords).
Report whichever form the company actually discloses — use BACKLOG for the dollar
figure regardless of which of these it represents, and note in SUMMARY which kind
of commitment it is. BOOK_TO_BILL only applies to traditional order-backlog
businesses — use "Not applicable" for a company whose model doesn't have that
concept (e.g. a lease-based capacity developer), distinct from "Not disclosed" for
a company where the concept applies but the company just doesn't share the number.

Only report numbers the company has actually disclosed — do not estimate or infer
a figure that wasn't stated. If a company doesn't disclose one of these figures
numerically, say so plainly rather than approximating from other data.

Respond with ONLY the five lines below — no preamble, no acknowledgment of the
search, no text before or after them. Keep BACKLOG and BOOK_TO_BILL to just the
figure itself — no commentary or caveats in those two fields, even if the company
doesn't disclose a clean number; put all nuance and context in SUMMARY instead:
BACKLOG: <dollar figure and unit, e.g. "$9.5 billion" — or exactly "Not disclosed">
BOOK_TO_BILL: <ratio, e.g. "1.4x" — or exactly "Not disclosed" or "Not applicable">
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
        f"Find the most recently disclosed backlog/ARR-under-contract/signed-lease-"
        f"value figures (whichever this company actually reports) for {name} "
        f"({ticker}), from their most recent earnings release or SEC filing."
    )


def parse_response(text):
    fields = {"BACKLOG": None, "BOOK_TO_BILL": None, "AS_OF": None, "SOURCE": None, "SUMMARY": None}
    for key, value in FIELD_PATTERN.findall(text):
        fields[key] = value.strip() or None
    return fields


def research_backlog(ticker, name):
    """Look up one ticker's backlog/ARR-under-contract/lease-value via Claude +
    web search. Raises on failure — caller decides how to handle it. Deliberately
    doesn't swallow the error into a written row: since the dashboard always reads
    the *latest* row per ticker, silently writing a failed-lookup row would shadow
    the last known-good data instead of just leaving it in place."""
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
    tickers = [t for archetype in ARCHETYPES for t in cloud.UNIVERSE.get(archetype, [])]
    try:
        names = pd.read_csv("data/cloud_scored.csv").set_index("Ticker")["Name"].to_dict()
    except (FileNotFoundError, KeyError):
        names = {}

    rows, failed = [], []
    for ticker in tickers:
        name = names.get(ticker, ticker)
        print(f"Researching backlog for {ticker}...")
        try:
            rows.append(research_backlog(ticker, name))
        except Exception as e:
            print(f"  FAILED — {ticker} skipped, last known-good data left in place: {e}")
            failed.append(ticker)

    if not rows:
        print("\nNo successful lookups this run — nothing appended.")
        return

    out = pd.DataFrame(rows)
    print(out.to_string(index=False))

    path = "data/backlog_notes.csv"
    out.to_csv(path, mode="a", header=not os.path.exists(path), index=False)
    print(f"\nAppended {len(out)} rows to {path}")
    if failed:
        print(f"Skipped (failed): {', '.join(failed)} — re-run once fixed.")


if __name__ == "__main__":
    run()
