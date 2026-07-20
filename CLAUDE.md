# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Stockify screens public companies across four verticals (Semiconductors, Cloud, Enterprise SaaS, Cybersecurity) against a quality-first, valuation-second investment philosophy geared toward "structurally necessary" companies in the AI infrastructure buildout. It fetches financial metrics, scores each company against archetype-specific thresholds, optionally generates an AI writeup per company, and displays everything in a Streamlit dashboard.

## Commands

```bash
# Run the pipeline (fetch -> score -> analyze -> CSV), controlled by flags in main.py
python main.py

# Launch the dashboard (reads the *_scored.csv files in data/)
streamlit run dashboard.py

# Manually sanity-check the FMP fetcher against a single ticker
python test_fmp.py
```

There is no test suite, linter, or build step beyond the above. `python test_fmp.py` is the closest thing to a smoke test.

Secrets (`FMP_API_KEY`, `ANTHROPIC_API_KEY`) live in `.env` (gitignored) and are loaded via `python-dotenv`.

## Pipeline architecture

`main.py` is the entry point and orchestrates three independent stages per vertical, gated by dicts at the top of the file:

```python
FETCH   = {"semis": True, "cloud": False, "saas": False, "cyber": False}
SCORE   = {"semis": True, "cloud": False, "saas": False, "cyber": False}
ANALYZE = {"semis": False, "cloud": False, "saas": False, "cyber": False}
```

Flip these booleans to control what runs — fetching is slow (rate-limited/network-bound) and analysis costs Anthropic API calls, so both default off except when actively refreshing data. Editing these flags is the normal way to run a partial pipeline; there's no CLI argument parsing.

1. **Fetch** — each `verticals/<name>.py` module owns a `UNIVERSE` dict (archetype -> list of tickers) and a `run()` function. `run()` fetches metrics per ticker via `yfinance` (threaded with `ThreadPoolExecutor`, 3 retries each) and writes `data/<name>.csv` with a `Last Updated` column stamped in.
2. **Score** — `main.py` reads `data/<name>.csv`, calls `scoring.score_dataframe()`, and writes `data/<name>_scored.csv`.
3. **Analyze** (optional) — `analyst.py` sends each Buy/Watch row to Claude (`analyze_dataframe`) for a short natural-language writeup, added as an `AI Analysis` column.

`dashboard.py` is a separate, standalone Streamlit app — it only reads the `*_scored.csv` files in `data/` and never touches the fetch/score/analyze pipeline directly. Re-run `main.py` first if you want the dashboard to reflect new data.

### Two independent data-fetching paths

- `verticals/*.py` (the one actually wired into `main.py`) fetches via **yfinance**, computing ROIC, gross-margin trend, and revenue CAGR by hand from `t.financials`/`t.balance_sheet`.
- `data_fetcher.py` fetches the same shape of metrics via the **Financial Modeling Prep (FMP)** REST API instead, using FMP's pre-computed fields (e.g. `evToFreeCashFlow`, `returnOnInvestedCapital`) rather than deriving them. It is not called from `main.py` — only `test_fmp.py` exercises it. Treat it as an alternate/unwired data source, not dead code to remove without checking with the user.

Both paths converge on the same output shape (a metrics dict per ticker) so they can flow into the same `scoring.py` regardless of source.

### Scoring model (`scoring.py`)

- `SCORING_CONFIG` is a registry keyed by **archetype** (e.g. `"Fabless"`, `"Hyperscaler"`, `"Enterprise_SaaS"`, `"ENDPOINT"`), not by vertical — archetypes are the unit of comparability ("industry-relative benchmarking" from the investment philosophy in `analyst.py`'s system prompt). Each archetype config has `quality_weights` (metric -> weight, summing to 1.0), `quality_thresholds` (metric -> ordered list of `(min, max, score)` bands), and a single `valuation_metric` + `valuation_thresholds`.
- `score_metric()` maps a raw value to a 1-5 band via the threshold tuples. `score_row()` computes a weighted average (renormalized over metrics that had data, so missing fields don't zero out the score), scales it to 0-100, and combines Quality Score + Valuation Score into a `Verdict` via `get_verdict()`: Buy (both >=60), Watch (quality high, cheap no), Avoid (cheap but low quality), Pass (neither).
- Threshold/weight constants are shared across many archetypes (e.g. `FCF_MARGIN_THRESHOLDS`, `GROSS_MARGIN_THRESHOLDS`) — when adjusting scoring behavior, check whether a constant is shared before editing it, since a change can silently ripple across every archetype that references it.
- Adding a new archetype means adding both a `UNIVERSE` entry in the relevant `verticals/*.py` file and a matching key in `SCORING_CONFIG` — the two are joined at runtime by the `Archetype` column, with no validation if they drift out of sync (unmatched archetypes silently score as "Insufficient Data").

### Adding a company or archetype

1. Add the ticker to the right list in the relevant `verticals/<name>.py` `UNIVERSE` dict (or a new archetype key).
2. If it's a new archetype, add a corresponding entry to `SCORING_CONFIG` in `scoring.py` with weights/thresholds and a `valuation_metric`.
3. Flip that vertical's `FETCH` and `SCORE` flags on in `main.py` and run it.

## Data files

`data/*.csv` (raw fetch) and `data/*_scored.csv` (post-scoring, what the dashboard reads) are committed to the repo rather than gitignored — they act as the last-known-good snapshot the dashboard serves without requiring a fresh fetch. When changing fetch/scoring logic, regenerate them via `main.py` rather than hand-editing.
