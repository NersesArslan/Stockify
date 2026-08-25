# Growth-stage flag: companies where trailing GAAP financials materially
# understate the investment case — contracted/signed backlog revenue,
# construction-phase capex, or hypergrowth off a small base — that the
# scoring model's trailing metrics don't capture. Purely informational
# (does not feed into Quality/Valuation scoring); surfaced on the
# per-stock dashboard page as a disclaimer. See scoring.py's Neocloud/
# Power_Campus valuation caveats and verticals/cloud.py archetype notes.

GROWTH_STAGE = {
    "NBIS": True,
    "CRWV": True,
    "IREN": True,
    "APLD": True,
}
