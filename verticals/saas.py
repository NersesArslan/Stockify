import yfinance as yf
import pandas as pd
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# --- Universe ---
ENTERPRISE_SAAS = [
    "CRM", "HUBS", "WDAY", "INTU", "NOW",
    "ADBE", "TEAM", "SAP", "PAYC", "PCTY", "NICE",
    "ADP", "PAYX"
]
DEVOPS        = ["GTLB", "PD"]
ENTERPRISE_AI = ["PLTR", "SNOW", "DDOG", "MDB", "ZS"]
VERTICAL_SAAS = ["VEEV", "IOT", "PTC", "TYL", "ADSK", "JKHY", "BR", "TRMB", "MSI"]
COLLABORATION = ["ZM", "DBX", "BOX"]
DATA_ANALYTICS = ["MSCI", "FICO", "VRSK", "SPGI", "MCO", "CSGP"]
IT_SERVICES   = ["ACN", "CTSH"]
AD_PLATFORM   = ["APP", "TTD"]
PAYMENT_NETWORK = ["V", "MA"]

UNIVERSE = {
    "Enterprise_SaaS": ENTERPRISE_SAAS,
    "DevOps":          DEVOPS,
    "Enterprise_AI":   ENTERPRISE_AI,
    "Vertical_SaaS":   VERTICAL_SAAS,
    "Collaboration":   COLLABORATION,
    "Data_Analytics":  DATA_ANALYTICS,
    "IT_Services":     IT_SERVICES,
    "Ad_Platform":     AD_PLATFORM,
    "Payment_Network": PAYMENT_NETWORK,
}

# --- Fetcher ---
def get_metrics(ticker_symbol, archetype):
    for attempt in range(3):
        try:
            t = yf.Ticker(ticker_symbol)
            info = t.info

            market_cap    = info.get("marketCap", 0) or 0
            total_debt    = info.get("totalDebt", 0) or 0
            cash          = info.get("totalCash", 0) or 0
            ebitda        = info.get("ebitda") or None
            revenue       = info.get("totalRevenue") or None
            free_cashflow = info.get("freeCashflow") or None

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

            operating_income = income.loc["Operating Income"].iloc[0] if "Operating Income" in income.index else None
            tax_rate         = income.loc["Tax Rate For Calcs"].iloc[0] if "Tax Rate For Calcs" in income.index else 0.21
            interest_exp     = income.loc["Interest Expense Non Operating"].iloc[0] if "Interest Expense Non Operating" in income.index else None
            rnd_expense      = income.loc["Research And Development"].iloc[0] if "Research And Development" in income.index else None
            employees        = info.get("fullTimeEmployees") or None

            ev_fcf          = round(ev / free_cashflow, 2)            if free_cashflow and free_cashflow > 0 else None
            ev_revenue      = round(ev / revenue, 2)                  if revenue and revenue > 0 else None
            fcf_margin      = round(free_cashflow / revenue * 100, 1) if free_cashflow and revenue else None
            op_margin       = round(info.get("operatingMargins") * 100, 1) if info.get("operatingMargins") else None
            gross_margin    = round(info.get("grossMargins") * 100, 1)     if info.get("grossMargins") else None
            revenue_growth  = round(info.get("revenueGrowth") * 100, 1)   if info.get("revenueGrowth") else None
            net_debt        = total_debt - cash
            net_debt_ebitda = round(net_debt / ebitda, 2)             if ebitda and ebitda > 0 else None
            interest_cov    = round(ebitda / abs(interest_exp), 2)    if ebitda and interest_exp and interest_exp != 0 else None
            nrr             = None  # requires manual data from filings
            rule_of_40      = round(revenue_growth + fcf_margin, 1)   if revenue_growth is not None and fcf_margin is not None else None
            rnd_intensity   = round(rnd_expense / revenue * 100, 1)   if rnd_expense and revenue else None
            rev_per_employee = round(revenue / employees / 1000, 1)  if revenue and employees else None

            return {
                "Ticker":            ticker_symbol,
                "Archetype":         archetype,
                "Name":              info.get("shortName"),
                "EV/FCF":            ev_fcf,
                "EV/Revenue":        ev_revenue,
                "FCF Margin":        fcf_margin,
                "Op Margin":         op_margin,
                "Gross Margin":      gross_margin,
                "Rev CAGR (3Y)":     rev_cagr,
                "Rev Growth (YoY)":  revenue_growth,
                "GM Trend (3Y)":     gm_trend,
                "ROIC Trend (3Y)":   roic_trend,
                "FCF Margin Trend (3Y)": fcf_margin_trend,
                "Rule of 40":        rule_of_40,
                "NRR":               nrr,
                "R&D Intensity":     rnd_intensity,
                "Revenue per Employee ($K)": rev_per_employee,
                "Net Debt/EBITDA":   net_debt_ebitda,
                "Interest Coverage": interest_cov,
            }

        except Exception as e:
            if attempt < 2:           # 12 spaces
                print(f"Retrying...") # 16 spaces
                time.sleep(2)     
            else:       
                return {
                    "Ticker":    ticker_symbol,
                    "Archetype": archetype,
                    "Error":     str(e)
                }

# --- Run ---
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
    df["Last Updated"] = datetime.date.today().strftime("%Y-%m-%d")
    df.to_csv("data/saas.csv", index=False)
    print("Saved to data/saas.csv")