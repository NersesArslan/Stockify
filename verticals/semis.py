from functools import partial
from verticals.fetch import fetch_metrics, run_vertical

# --- Universe ---
FOUNDRIES = ["TSM", "UMC"]
FABLESS = ["NVDA", "AMD", "AVGO", "MRVL", "MPWR", "ARM",
           "MTSI", "SIMO", "RMBS", "SITM", "AMBA"]
# QCOM, MCHP, QRVO, SWKS, SLAB, ALGM, CRUS, MXL, PI — removed 2026-08-21:
# mobile/auto/industrial-first revenue, not directly AI-infrastructure exposure
EQUIPMENT = ["ASML", "LRCX", "KLAC", "AMAT", "ENTG", "MKSI",
             "ACLS", "UCTT", "ICHR", "COHU", "FORM", "ONTO",
             "NVMI", "CAMT", "TER", "KEYS"]
IDMS = ["INTC"]
# TXN, NXPI, STM, ADI, ON, WOLF — removed 2026-08-21: analog/auto/industrial-first
# revenue, not directly AI-infrastructure exposure
MEMORY = ["MU", "WDC", "STX"]
# PSTG — removed, yfinance/Yahoo Finance returns no quote for this symbol (likely delisted)
EDA_IP = ["SNPS", "CDNS"]
# ANSS — removed, yfinance/Yahoo Finance returns no quote for this symbol (likely delisted, e.g. post-acquisition)
# SUPPLY_CHAIN (AVT, ARW, CDW) — removed 2026-08-21: generic component distribution,
# not directly AI-infrastructure exposure
UNIVERSE = {
    "Foundry": FOUNDRIES,
    "Fabless": FABLESS,
    "Equipment": EQUIPMENT,
    "IDM": IDMS,
    "Memory": MEMORY,
    "EDA_IP": EDA_IP,
}

# --- Fetcher ---
# Semis is the only vertical that computes absolute ROIC (capital-intensity is
# central to how this vertical scores quality) and normalizes FX (TSM/UMC
# report financials in TWD while their ADR market cap is quoted in USD).
# See verticals/fetch.py for the shared fetch/run scaffolding every vertical uses.
get_metrics = partial(fetch_metrics, compute_roic=True, normalize_fx=True)


def run():
    return run_vertical(UNIVERSE, get_metrics, "data/semis.csv")
