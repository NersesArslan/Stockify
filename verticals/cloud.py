import yfinance as yf
import pandas as pd

# --- Universe ---
HYPERSCALERS = ["AMZN", "MSFT", "GOOGL", "ORCL"]

CLOUD_DATA = [
    "SNOW",  # Snowflake - data warehousing
    "MDB",   # MongoDB - cloud-native database
    "DDOG",  # Datadog - observability
    "NET",   # Cloudflare - edge network
    "ESTC",  # Elastic - search and analytics
]

UNIVERSE = {
    "Hyperscaler": HYPERSCALERS,
    "Cloud_Data":  CLOUD_DATA,
}


# --- Fetcher ---
def get_metrics(ticker_symbol, archetype):
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
        balance = t.balance_sheet

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
        nrr = None  # requires manual data from filings

        return {
            "Ticker":            ticker_symbol,
            "Archetype":         archetype,
            "Name":              info.get("shortName"),
            "EV/FCF":            ev_fcf,
            "FCF Margin":        fcf_margin,
            "Op Margin":         op_margin,
            "Gross Margin":      gross_margin,
            "Rev Growth (YoY)":  revenue_growth,
            "EV_Revenue":              ev_revenue,
            "Net Debt/EBITDA":   net_debt_ebitda,
            "Interest Coverage": interest_cov,
        }

    except Exception as e:
        return {
            "Ticker":    ticker_symbol,
            "Archetype": archetype,
            "Error":     str(e)
        }

# --- Main ---
def run():
    rows = []
    for archetype, tickers in UNIVERSE.items():
        for ticker in tickers:
            print(f"Fetching {ticker}...")
            rows.append(get_metrics(ticker, archetype))

    df = pd.DataFrame(rows)

    # Display each archetype separately
    for archetype in UNIVERSE.keys():
        print(f"\n{'='*60}")
        print(f"  {archetype.upper()}")
        print(f"{'='*60}")
        subset = df[df["Archetype"] == archetype].drop(columns=["Archetype"])
        print(subset.to_string(index=False))

    df.to_csv("data/cloud.csv", index=False)
    print("Saved to data/cloud.csv")