import yfinance as yf
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
# --- Universe ---
FOUNDRIES = ["TSM", "UMC"]
FABLESS = ["NVDA", "AMD", "QCOM", "AVGO", "MRVL", "MPWR",
           "MCHP", "QRVO", "SWKS", "ARM", "SLAB", "ALGM",
           "MTSI", "CRUS", "SIMO", "MXL", "RMBS"]
EQUIPMENT = ["ASML", "LRCX", "KLAC", "AMAT", "ENTG", "MKSI",
             "ACLS", "UCTT", "ICHR", "COHU", "FORM", "ONTO",
             "NVMI", "CAMT", "TER"]
IDMS = ["INTC", "TXN", "NXPI", "STM", "ADI", "ON", "WOLF"]
MEMORY = ["MU", "WDC", "STX"]
EDA_IP = ["SNPS", "CDNS" ]
SUPPLY_CHAIN = ["AVT", "ARW"]
UNIVERSE = {
    "Foundry": FOUNDRIES,
    "Fabless": FABLESS,
    "Equipment": EQUIPMENT,
    "IDM": IDMS,
    "Memory": MEMORY,
    "EDA_IP": EDA_IP,
    "SUPPLY_CHAIN": SUPPLY_CHAIN
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
            balance = t.balance_sheet
                        # Historical gross margin trend (4 years)
            try:
                income_hist = t.financials
                if "Gross Profit" in income_hist.index and "Total Revenue" in income_hist.index:
                    gp  = income_hist.loc["Gross Profit"]
                    rev = income_hist.loc["Total Revenue"]
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
            invested_capital = balance.loc["Invested Capital"].iloc[0] if "Invested Capital" in balance.index else None
            nopat            = operating_income * (1 - tax_rate) if operating_income is not None else None
            interest_exp     = income.loc["Interest Expense Non Operating"].iloc[0] if "Interest Expense Non Operating" in income.index else None

            ev_fcf          = round(ev / free_cashflow, 2)         if free_cashflow and free_cashflow > 0 else None
            fcf_margin      = round(free_cashflow / revenue * 100, 1) if free_cashflow and revenue else None
            op_margin       = round(info.get("operatingMargins") * 100, 1) if info.get("operatingMargins") else None
            gross_margin    = round(info.get("grossMargins") * 100, 1)     if info.get("grossMargins") else None
            revenue_growth  = round(info.get("revenueGrowth") * 100, 1)   if info.get("revenueGrowth") else None
            net_debt        = total_debt - cash
            net_debt_ebitda = round(net_debt / ebitda, 2)          if ebitda and ebitda > 0 else None
            interest_cov    = round(ebitda / abs(interest_exp), 2) if ebitda and interest_exp and interest_exp != 0 else None
            roic            = round(nopat / invested_capital * 100, 1) if nopat and invested_capital and invested_capital > 0 else None

            return {
                "Ticker":            ticker_symbol,
                "Archetype":         archetype,
                "Name":              info.get("shortName"),
                "EV/FCF":            ev_fcf,
                "FCF Margin":        fcf_margin,
                "Op Margin":         op_margin,
                "Gross Margin":      gross_margin,
                "GM Trend (3Y)":     gm_trend,
                "Rev Growth (YoY)":  revenue_growth,
                "ROIC":              roic,
                "Net Debt/EBITDA":   net_debt_ebitda,
                "Interest Coverage": interest_cov,
            }

        except Exception as e:
            if attempt < 2:           # 12 spaces
                print(f"Retrying...") # 16 spaces
                time.sleep(2)         # 16 spaces
            else:    
                return {
                    "Ticker":    ticker_symbol,
                    "Archetype": archetype,
                    "Error":     str(e)
                }
            

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

    df.to_csv("data/semis.csv", index=False)
    print("Saved to data/semis.csv")