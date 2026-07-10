# data_fetcher.py
import requests
import os
import time
from dotenv import load_dotenv


load_dotenv()
API_KEY = os.getenv("FMP_API_KEY")
BASE_URL = "https://financialmodelingprep.com/stable"




def get(endpoint, params=None):
    if params is None:
        params = {}
    params["apikey"] = API_KEY
    response = requests.get(f"{BASE_URL}/{endpoint}", params=params)
    time.sleep(0.3)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 402:
        print(f"Daily limit reached: {endpoint}")
        return None
    elif response.status_code == 429:
        print(f"Rate limited, waiting 60s...")
        time.sleep(60)
        return get(endpoint, params)
    else:
        print(f"Error {response.status_code}: {endpoint}")
        return None


def get_profile(ticker):
    data = get("profile", {"symbol": ticker})
    return data[0] if data else None

def get_income_statement(ticker, years=5):
    data = get("income-statement", {"symbol": ticker, "limit": years})
    return data if data else []

def get_balance_sheet(ticker, years=1):
    data = get("balance-sheet-statement", {"symbol": ticker, "limit": years})
    return data if data else []

def get_cash_flow(ticker, years=1):
    data = get("cash-flow-statement", {"symbol": ticker, "limit": years})
    return data if data else []

def get_key_metrics(ticker, years=1):
    data = get("key-metrics", {"symbol": ticker, "limit": years})
    return data if data else []


def get_metrics(ticker_symbol, archetype):
    try:
        profile     = get_profile(ticker_symbol)
        income      = get_income_statement(ticker_symbol, years=2)
        balance     = get_balance_sheet(ticker_symbol)
        cashflow    = get_cash_flow(ticker_symbol)
        key_metrics = get_key_metrics(ticker_symbol)

        if not profile or not income or not balance or not cashflow or not key_metrics:
            return {
                "Ticker":    ticker_symbol,
                "Archetype": archetype,
                "Error":     "Missing data from FMP"
            }

        inc = income[0]
        bal = balance[0]
        cf  = cashflow[0]
        km  = key_metrics[0]

        # --- Use FMP pre-computed values where available ---
        revenue       = inc.get("revenue") or None
        ebitda        = inc.get("ebitda") or None
        operating_inc = inc.get("operatingIncome") or None
        interest_exp  = inc.get("interestExpense") or None
        free_cashflow = cf.get("freeCashFlow") or None
        gross_profit  = inc.get("grossProfit") or None

        # Revenue growth computed from two most recent years
        if len(income) >= 2:
            current_rev  = income[0].get("revenue")
            previous_rev = income[1].get("revenue")
            revenue_growth = round((current_rev - previous_rev) / previous_rev * 100, 1) if current_rev and previous_rev else None
        else:
            revenue_growth = None

        # Use FMP pre-computed EV multiples
        ev_fcf     = round(km.get("evToFreeCashFlow"), 2) if km.get("evToFreeCashFlow") else None
        ev_revenue = round(km.get("evToSales"), 2)        if km.get("evToSales") else None

        # Margins computed from income statement
        fcf_margin   = round(free_cashflow / revenue * 100, 1) if free_cashflow and revenue else None
        op_margin    = round(operating_inc / revenue * 100, 1) if operating_inc and revenue else None
        gross_margin = round(gross_profit / revenue * 100, 1)  if gross_profit and revenue else None

        # Debt metrics
        net_debt        = bal.get("netDebt") or 0
        net_debt_ebitda = round(net_debt / ebitda, 2) if ebitda and ebitda > 0 else None
        interest_cov    = round(ebitda / abs(interest_exp), 2) if ebitda and interest_exp and interest_exp != 0 else None

        # ROIC directly from key metrics
        roic = round(km.get("returnOnInvestedCapital") * 100, 1) if km.get("returnOnInvestedCapital") else None

        # Rule of 40
        rule_of_40 = round(revenue_growth + fcf_margin, 1) if revenue_growth is not None and fcf_margin is not None else None

        return {
            "Ticker":            ticker_symbol,
            "Archetype":         archetype,
            "Name":              profile.get("companyName"),
            "EV/FCF":            ev_fcf,
            "EV/Revenue":        ev_revenue,
            "FCF Margin":        fcf_margin,
            "Op Margin":         op_margin,
            "Gross Margin":      gross_margin,
            "Rev Growth (YoY)":  revenue_growth,
            "ROIC":              roic,
            "Rule of 40":        rule_of_40,
            "Net Debt/EBITDA":   net_debt_ebitda,
            "Interest Coverage": interest_cov,
        }

    except Exception as e:
        return {
            "Ticker":    ticker_symbol,
            "Archetype": archetype,
            "Error":     str(e)
        }