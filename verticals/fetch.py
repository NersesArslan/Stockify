# verticals/fetch.py
#
# Shared fetch scaffolding for all four verticals — extracted from what was
# near-identical, copy-pasted logic across semis.py/cloud.py/saas.py/cyber.py.
#
# `fetch_metrics()` is the pluggable data-source contract: any function with
# the signature (ticker_symbol, archetype) -> dict of the same field shape can
# stand in for it. This one is yfinance-backed; a future FMP-backed (or other)
# implementation just needs to return the same field names for `run_vertical()`
# and `scoring.py` to work with it unchanged. Each vertical's run() picks which
# fetcher (and which of its optional behaviors — ROIC, FX normalization, SaaS
# metrics) to use via functools.partial, rather than duplicating the fetch loop.

import time
import datetime
import yfinance as yf
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- FX handling for foreign filers (e.g. TSM, UMC report financials in TWD
# while their ADR market cap is quoted in USD). Only semis.py opts into this. ---
_fx_cache = {}

def get_fx_rate(financial_currency, price_currency="USD"):
    """Local-currency units per 1 price_currency unit, e.g. TWD per USD."""
    if not financial_currency or financial_currency == price_currency:
        return 1.0
    if financial_currency in _fx_cache:
        return _fx_cache[financial_currency]
    try:
        fx_info = yf.Ticker(f"{financial_currency}=X").info
        rate = fx_info.get("regularMarketPrice") or fx_info.get("previousClose")
    except Exception:
        rate = None
    _fx_cache[financial_currency] = rate
    return rate


def fetch_metrics(ticker_symbol, archetype, *, compute_roic=False,
                   normalize_fx=False, include_saas_metrics=False,
                   max_retries=3, retry_delay=2):
    """
    yfinance-backed metrics fetch. Optional behaviors, off by default:
      compute_roic         — absolute ROIC (needs Invested Capital + NOPAT).
                              Semis only; other verticals don't compute it yet.
      normalize_fx          — convert dollar figures via financialCurrency ->
                              currency FX rate. Needed for foreign filers
                              (TSM, UMC); everything else in the universe
                              already reports in USD.
      include_saas_metrics — Rule of 40 + NRR. Meaningless for hardware/
                              industrial archetypes (semis, Data_Center_Infra,
                              Power_Campus), so semis.py leaves it off.
    """
    for attempt in range(max_retries):
        try:
            t = yf.Ticker(ticker_symbol)
            info = t.info

            market_cap    = info.get("marketCap", 0) or 0
            total_debt    = info.get("totalDebt", 0) or 0
            cash          = info.get("totalCash", 0) or 0
            ebitda        = info.get("ebitda") or None
            revenue       = info.get("totalRevenue") or None
            free_cashflow = info.get("freeCashflow") or None

            if normalize_fx:
                # market_cap is always quoted in `currency`; everything else
                # above (and the financial statements below) is reported in
                # `financialCurrency`, which differs for foreign filers.
                # Normalize to `currency` (USD for our universe) so dollar
                # figures aren't corrupted.
                fx_rate = get_fx_rate(info.get("financialCurrency"), info.get("currency") or "USD")

                def to_usd(value):
                    if value is None or not fx_rate or fx_rate == 1.0:
                        return value
                    return value / fx_rate
            else:
                def to_usd(value):
                    return value

            total_debt    = to_usd(total_debt)
            cash          = to_usd(cash)
            ebitda        = to_usd(ebitda)
            revenue       = to_usd(revenue)
            free_cashflow = to_usd(free_cashflow)

            income = t.financials
            # Revenue CAGR (3Y)
            try:
                if "Total Revenue" in income.index:
                    rev_hist = income.loc["Total Revenue"].dropna()
                    if len(rev_hist) >= 4:
                        recent   = float(rev_hist.iloc[0])
                        older    = float(rev_hist.iloc[3])
                        rev_cagr = round(((recent / older) ** (1/3) - 1) * 100, 1)
                    else:
                        rev_cagr = None
                else:
                    rev_cagr = None
            except Exception:
                rev_cagr = None

            balance = t.balance_sheet
            # GM Trend (3Y)
            try:
                income_hist = income
                if "Gross Profit" in income_hist.index and "Total Revenue" in income_hist.index:
                    gp  = income_hist.loc["Gross Profit"]
                    rev = income.loc["Total Revenue"]
                    margins = (gp / rev * 100).dropna()
                    if len(margins) >= 2:
                        gm_trend = round(float(margins.iloc[0]) - float(margins.iloc[-1]), 1)
                    else:
                        gm_trend = None
                else:
                    gm_trend = None
            except Exception:
                gm_trend = None

            # ROIC Trend (3Y): most recent year's ROIC minus ROIC from 3 years ago
            try:
                if "Operating Income" in income.index and "Invested Capital" in balance.index:
                    op_income_hist = income.loc["Operating Income"]
                    invested_capital_hist = balance.loc["Invested Capital"]
                    if "Tax Rate For Calcs" in income.index:
                        tax_rate_hist = income.loc["Tax Rate For Calcs"]
                    else:
                        tax_rate_hist = pd.Series(0.21, index=op_income_hist.index)
                    roic_hist = []
                    for date in op_income_hist.index:
                        oi = op_income_hist.get(date)
                        ic = invested_capital_hist.get(date)
                        tr = tax_rate_hist.get(date)
                        if pd.isna(tr):
                            tr = 0.21
                        if pd.notna(oi) and pd.notna(ic) and ic != 0:
                            roic_hist.append(oi * (1 - tr) / ic * 100)
                    if len(roic_hist) >= 4:
                        roic_trend = round(roic_hist[0] - roic_hist[3], 1)
                    else:
                        roic_trend = None
                else:
                    roic_trend = None
            except Exception:
                roic_trend = None

            # FCF Margin Trend (3Y): most recent year's FCF margin minus FCF margin from 3 years ago
            try:
                cf = t.cashflow
                if "Free Cash Flow" in cf.index and "Total Revenue" in income.index:
                    fcf_hist = cf.loc["Free Cash Flow"]
                    rev_hist_fcf = income.loc["Total Revenue"]
                    fcf_margin_hist = []
                    for date in fcf_hist.index:
                        fcf_val = fcf_hist.get(date)
                        rev_val = rev_hist_fcf.get(date)
                        if pd.notna(fcf_val) and pd.notna(rev_val) and rev_val != 0:
                            fcf_margin_hist.append(fcf_val / rev_val * 100)
                    if len(fcf_margin_hist) >= 4:
                        fcf_margin_trend = round(fcf_margin_hist[0] - fcf_margin_hist[3], 1)
                    else:
                        fcf_margin_trend = None
                else:
                    fcf_margin_trend = None
            except Exception:
                fcf_margin_trend = None

            ev = market_cap + total_debt - cash

            interest_exp = income.loc["Interest Expense Non Operating"].iloc[0] if "Interest Expense Non Operating" in income.index else None
            rnd_expense  = income.loc["Research And Development"].iloc[0] if "Research And Development" in income.index else None
            interest_exp = to_usd(interest_exp)
            rnd_expense  = to_usd(rnd_expense)
            employees    = info.get("fullTimeEmployees") or None

            ev_fcf          = round(ev / free_cashflow, 2)            if free_cashflow and free_cashflow > 0 else None
            ev_revenue      = round(ev / revenue, 2)                  if revenue and revenue > 0 else None
            fcf_margin      = round(free_cashflow / revenue * 100, 1) if free_cashflow and revenue else None
            op_margin       = round(info.get("operatingMargins") * 100, 1) if info.get("operatingMargins") else None
            gross_margin    = round(info.get("grossMargins") * 100, 1)     if info.get("grossMargins") else None
            revenue_growth  = round(info.get("revenueGrowth") * 100, 1)   if info.get("revenueGrowth") else None
            net_debt        = total_debt - cash
            net_debt_ebitda = round(net_debt / ebitda, 2)             if ebitda and ebitda > 0 else None
            interest_cov    = round(ebitda / abs(interest_exp), 2)    if ebitda and interest_exp and interest_exp != 0 else None
            rnd_intensity   = round(rnd_expense / revenue * 100, 1)   if rnd_expense and revenue else None
            rev_per_employee = round(revenue / employees / 1000, 1)  if revenue and employees else None

            result = {
                "Ticker":            ticker_symbol,
                "Archetype":         archetype,
                "Name":              info.get("shortName"),
                "Price":             info.get("currentPrice") or info.get("regularMarketPrice"),
                "EV/FCF":            ev_fcf,
                "EV/Revenue":        ev_revenue,
                "FCF Margin":        fcf_margin,
                "Op Margin":         op_margin,
                "Gross Margin":      gross_margin,
                "GM Trend (3Y)":     gm_trend,
                "Rev CAGR (3Y)":     rev_cagr,
                "Rev Growth (YoY)":  revenue_growth,
            }

            if compute_roic:
                operating_income = income.loc["Operating Income"].iloc[0] if "Operating Income" in income.index else None
                tax_rate         = income.loc["Tax Rate For Calcs"].iloc[0] if "Tax Rate For Calcs" in income.index else 0.21
                invested_capital = balance.loc["Invested Capital"].iloc[0] if "Invested Capital" in balance.index else None
                nopat            = operating_income * (1 - tax_rate) if operating_income is not None else None
                roic             = round(nopat / invested_capital * 100, 1) if nopat and invested_capital and invested_capital > 0 else None
                result["ROIC"] = roic

            result["ROIC Trend (3Y)"] = roic_trend
            result["FCF Margin Trend (3Y)"] = fcf_margin_trend

            if include_saas_metrics:
                rule_of_40 = round(revenue_growth + fcf_margin, 1) if revenue_growth is not None and fcf_margin is not None else None
                nrr = None  # requires manual data from filings
                result["Rule of 40"] = rule_of_40
                result["NRR"] = nrr

            result["R&D Intensity"] = rnd_intensity
            result["Revenue per Employee ($K)"] = rev_per_employee
            result["Net Debt/EBITDA"] = net_debt_ebitda
            result["Interest Coverage"] = interest_cov

            return result

        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Retrying {ticker_symbol} (attempt {attempt + 1})...")
                time.sleep(retry_delay)
            else:
                return {
                    "Ticker":    ticker_symbol,
                    "Archetype": archetype,
                    "Error":     str(e)
                }


def run_vertical(universe, fetch_fn, output_csv, max_workers=4):
    """Threaded fetch across a UNIVERSE dict, printed by archetype, saved to CSV.
    `fetch_fn` is any (ticker, archetype) -> dict callable — this is the plug
    point for swapping data sources without touching this function."""
    tasks = [
        (ticker, archetype)
        for archetype, tickers in universe.items()
        for ticker in tickers
    ]

    rows = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(fetch_fn, ticker, archetype): ticker
            for ticker, archetype in tasks
        }
        for future in as_completed(futures):
            ticker = futures[future]
            print(f"Fetched {ticker}")
            rows.append(future.result())

    df = pd.DataFrame(rows)

    # Restore original order
    order = [ticker for tickers in universe.values() for ticker in tickers]
    df["Ticker"] = pd.Categorical(df["Ticker"], categories=order, ordered=True)
    df = df.sort_values("Ticker").reset_index(drop=True)

    for archetype in universe.keys():
        print(f"\n{'='*60}")
        print(f"  {archetype.upper()}")
        print(f"{'='*60}")
        subset = df[df["Archetype"] == archetype].drop(columns=["Archetype"])
        print(subset.to_string(index=False))

    df["Last Updated"] = datetime.date.today().strftime("%Y-%m-%d")
    df.to_csv(output_csv, index=False)
    print(f"Saved to {output_csv}")
    return df
