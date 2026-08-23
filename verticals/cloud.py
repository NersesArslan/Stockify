from functools import partial
from verticals.fetch import fetch_metrics, run_vertical

# --- Universe ---
HYPERSCALERS = [
    "AMZN",  # AWS
    "MSFT",  # Azure
    "GOOGL", # Google Cloud
    "ORCL",  # Oracle Cloud — conglomerate, scored as hyperscaler pending multi-segment handling
]

# CLOUD_DATA (ESTC, AKAM, GDDY, FFIV, VRSN, FSLY) — removed 2026-08-21: CDN/edge/
# domain-registry businesses, not directly AI-infrastructure exposure.
# SNOW, DDOG, MDB moved to Enterprise_AI in SaaS
NETWORK_HARDWARE = ["ANET"]
DATA_CENTER_INFRA = ["VRT", "SMCI", "CLS"]
# VRT (Vertiv) — power/thermal management
# SMCI (Super Micro) — AI/data-center server systems
# CLS (Celestica) — hyperscaler networking switches, liquid-cooled rack systems

NEOCLOUD = ["NBIS", "CRWV"]
# NBIS (Nebius) — GPU cloud, full-stack AI infrastructure platform
# CRWV (CoreWeave) — GPU cloud, same business model, close comp to NBIS
# Growth-stage pure-play GPU cloud providers, already at meaningful realized
# consumption revenue — distinct from Hyperscaler (mature, highly profitable)
# despite the thematic overlap. See scoring.py for why.

POWER_CAMPUS = ["IREN", "APLD"]
# IREN — vertically integrated: owns power + data centers + GPUs, runs its own
# AI Cloud GPU-rental revenue (closer to Neocloud in that respect), still
# transitioning off legacy bitcoin-mining revenue.
# APLD — pure capacity developer: builds/owns AI data-center campuses and
# leases them to CoreWeave/hyperscalers under long-term (15Y), take-or-pay,
# non-cancellable contracts — landlord/developer economics, not a cloud
# operator at all.
# Not identical business models, but grouped together because both share the
# defining characteristic that separates this archetype from Neocloud: massive
# *contracted/signed* revenue (IREN's ARR-under-contract, APLD's $30B+ lease
# backlog) that dwarfs current trailing revenue, financed by real construction-
# phase debt. Trailing financials understate the real investment case here even
# more than for Neocloud — see scoring.py's valuation caveat.
#
# Considered and left out for now: WULF, CIFR, HUT (still substantially
# bitcoin-mining-legacy revenue transitioning to AI hosting — same
# conglomerate-style caution as SPGI/MCO earlier); AGPU (too new/thinly-covered
# to responsibly include yet).

UNIVERSE = {
    "Hyperscaler":         HYPERSCALERS,
    "Network_Hardware":    NETWORK_HARDWARE,
    "Data_Center_Infra":   DATA_CENTER_INFRA,
    "Neocloud":            NEOCLOUD,
    "Power_Campus":        POWER_CAMPUS,
}

# --- Fetcher ---
# Rule of 40/NRR are meaningful here (subscription/consumption revenue mixed
# with capex-heavy names); ROIC and FX normalization aren't needed — every
# ticker in this vertical reports in USD. See verticals/fetch.py for the
# shared fetch/run scaffolding every vertical uses.
get_metrics = partial(fetch_metrics, include_saas_metrics=True)


def run():
    return run_vertical(UNIVERSE, get_metrics, "data/cloud.csv")
