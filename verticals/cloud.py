import yfinance as yf
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# --- Universe ---
HYPERSCALERS = [
    "AMZN",  # AWS
    "MSFT",  # Azure
    "GOOGL", # Google Cloud
    "ORCL",  # Oracle Cloud — conglomerate, scored as hyperscaler pending multi-segment handling
]

CLOUD_DATA = ["ESTC"]  # SNOW, DDOG, MDB moved to Enterprise_AI in SaaS

UNIVERSE = {
    "Hyperscaler": HYPERSCALERS,
    "Cloud_Data":  CLOUD_DATA,
}


# --- Fetcher ---
def get_metrics(ticker_symbol, archetype):
    for attempt in range(3):
        try:
            t = yf.Ticker(ticker_symbol)
            info = t.info

            market_cap     = info.get("marketCap", 0) or 0
            total_debt     = info.get("totalDebt", 0) or 0
            cash           = info.get("totalCash", 0) or 0
            ebitda         = info.get("ebitda") or None
            revenue        = info.get("totalRevenue") or None
            free_cashflow  = info.get("freeCashflow") or None

            income = t.financials
            # Revenue CAGR (3 year)
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
            ev = market_cap + total_debt - cash

            operating_income = income.loc["Operating Income"].iloc[0] if "Operating Income" in income.index else None
            tax_rate         = income.loc["Tax Rate For Calcs"].iloc[0] if "Tax Rate For Calcs" in income.index else 0.21
            interest_exp     = income.loc["Interest Expense Non Operating"].iloc[0] if "Interest Expense Non Operating" in income.index else None

            ev_fcf          = round(ev / free_cashflow, 2)         if free_cashflow and free_cashflow > 0 else None
            fcf_margin      = round(free_cashflow / revenue * 100, 1) if free_cashflow and revenue else None
            op_margin       = round(info.get("operatingMargins") * 100, 1) if info.get("operatingMargins") else None
            gross_margin    = round(info.get("grossMargins") * 100, 1)     if info.get("grossMargins") else None
            revenue_growth  = round(info.get("revenueGrowth") * 100, 1)   if info.get("revenueGrowth") else None
            net_debt        = total_debt - cash
            net_debt_ebitda = round(net_debt / ebitda, 2)          if ebitda and ebitda > 0 else None
            interest_cov    = round(ebitda / abs(interest_exp), 2) if ebitda and interest_exp and interest_exp != 0 else None
            ev_revenue = round(ev / revenue, 2) if revenue and revenue > 0 else None
            rule_of_40 = round(revenue_growth + fcf_margin, 1) if revenue_growth is not None and fcf_margin is not None else None
            nrr = None  # requires manual data from filings

            return {
                "Ticker":            ticker_symbol,
                "Archetype":         archetype,
                "Name":              info.get("shortName"),
                "EV/FCF":            ev_fcf,
                "FCF Margin":        fcf_margin,
                "Op Margin":         op_margin,
                "Gross Margin":      gross_margin,
                "Rev CAGR (3Y)":     rev_cagr,
                "Rev Growth (YoY)":  revenue_growth,
                "GM Trend (3Y)":     gm_trend,
                "EV/Revenue":              ev_revenue,
                "Net Debt/EBITDA":   net_debt_ebitda,
                "Interest Coverage": interest_cov,
                "Rule of 40": rule_of_40,
            }

        except Exception as e:
            if attempt < 2:
                print(f"Retrying {ticker_symbol} (attempt {attempt + 1})...")
                time.sleep(2)
            else:
                return {
                    "Ticker":    ticker_symbol,
                    "Archetype": archetype,
                    "Error":     str(e)
                }

# --- Main ---
def run():
    tasks = [
        (ticker, archetype)
        for archetype, tickers in UNIVERSE.items()
        for ticker in tickers
    ]

    rows = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(get_metrics, ticker, archetype): ticker
            for ticker, archetype in tasks
        }
        for future in as_completed(futures):
            ticker = futures[future]
            print(f"Fetched {ticker}")
            rows.append(future.result())

    df = pd.DataFrame(rows)

    # Restore original order
    order = [ticker for tickers in UNIVERSE.values() for ticker in tickers]
    df["Ticker"] = pd.Categorical(df["Ticker"], categories=order, ordered=True)
    df = df.sort_values("Ticker").reset_index(drop=True)

    for archetype in UNIVERSE.keys():
        print(f"\n{'='*60}")
        print(f"  {archetype.upper()}")
        print(f"{'='*60}")
        subset = df[df["Archetype"] == archetype].drop(columns=["Archetype"])
        print(subset.to_string(index=False))

    df.to_csv("data/cloud.csv", index=False)
    print("Saved to data/cloud.csv")