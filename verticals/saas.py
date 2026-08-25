from functools import partial
from verticals.fetch import fetch_metrics, run_vertical

# --- Universe ---
ENTERPRISE_SAAS = [
    "CRM", "HUBS", "WDAY", "INTU", "NOW",
    "ADBE", "TEAM", "SAP", "PAYC", "PCTY", "NICE",
    "ADP", "PAYX", "FIVN", "SSNC", "MANH"
    # SMAR — removed, yfinance/Yahoo Finance returns no quote for this symbol
    # (taken private by Blackstone/Vista Equity Partners, early 2025)
]
DEVOPS = ["GTLB", "PD"]
ENTERPRISE_AI = ["PLTR", "SNOW", "DDOG", "MDB", "ZS"]
# VERTICAL_SAAS (VEEV, IOT, PTC, TYL, ADSK, JKHY, BR, TRMB, MSI, PCOR, NCNO, SHOP),
# COLLABORATION (ZM, DBX, BOX), DATA_ANALYTICS (MSCI, FICO, VRSK, SPGI, MCO, CSGP),
# IT_SERVICES (ACN, CTSH), AD_PLATFORM (APP, TTD), PAYMENT_NETWORK (V, MA) —
# removed 2026-08-21: excellent businesses, but not directly involved in the AI
# infrastructure buildout/maintenance thesis. See CLAUDE.md scope note.

UNIVERSE = {
    "Enterprise_SaaS": ENTERPRISE_SAAS,
    "DevOps":          DEVOPS,
    "Enterprise_AI":   ENTERPRISE_AI,
}

# --- Fetcher ---
# Rule of 40/NRR are core signals for subscription software; ROIC and FX
# normalization aren't needed — every ticker in this vertical reports in USD.
# See verticals/fetch.py for the shared fetch/run scaffolding every vertical uses.
get_metrics = partial(fetch_metrics, include_saas_metrics=True)


def run():
    return run_vertical(UNIVERSE, get_metrics, "data/saas.csv")
