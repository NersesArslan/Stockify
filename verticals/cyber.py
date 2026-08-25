from functools import partial
from verticals.fetch import fetch_metrics, run_vertical

ENDPOINT  = ["CRWD", "S"]
NETWORK   = ["PANW", "FTNT", "CHKP"]
IDENTITY  = ["OKTA", "SAIL",
             # "CYBR" — removed, being acquired by PANW (deal announced July 2025)
]
CLOUD_SEC = []  # ZS moved to Enterprise_AI in SaaS
# or remove CLOUD_SEC entirely
DATA_SEC  = ["QLYS", "VRNT", "TENB", "GEN", "VRNS", "RPD"]

UNIVERSE = {
    "ENDPOINT": ENDPOINT,
    "NETWORK":  NETWORK,
    "IDENTITY": IDENTITY,
    "DATA_SEC": DATA_SEC,
}

# --- Fetcher ---
# Rule of 40/NRR are core signals for subscription software; ROIC and FX
# normalization aren't needed — every ticker in this vertical reports in USD.
# See verticals/fetch.py for the shared fetch/run scaffolding every vertical uses.
get_metrics = partial(fetch_metrics, include_saas_metrics=True)


def run():
    return run_vertical(UNIVERSE, get_metrics, "data/cyber.csv")
