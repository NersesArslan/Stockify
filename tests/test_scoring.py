import pandas as pd
from scoring import score_dataframe

def test_semi_verdicts():
    """Known-good verdicts for key semiconductor companies."""
    df = pd.read_csv("data/semis_scored.csv")

    def verdict(ticker):
        return df[df["Ticker"] == ticker]["Verdict"].iloc[0]

    # Structural necessities — should always be Watch or Buy
    assert verdict("NVDA") == "Watch"   # elite quality, expensive
    assert verdict("TSM")  == "Watch"   # elite quality, fairly valued
    assert verdict("KEYS") == "Buy"     # solid quality, cheap
    assert verdict("RMBS") == "Buy"     # IP licensing moat, reasonable price

    # Distressed names — should always be Pass or Avoid
    assert verdict("UCTT") == "Avoid"   # weakest quality in the universe
    assert verdict("INTC") == "Pass"

def test_saas_verdicts():
    """Known-good verdicts for key SaaS companies."""
    df = pd.read_csv("data/saas_scored.csv")

    def verdict(ticker):
        return df[df["Ticker"] == ticker]["Verdict"].iloc[0]

    assert verdict("PLTR") == "Watch"   # exceptional quality, too expensive
    assert verdict("CRM")  == "Buy"     # quality at reasonable price
    assert verdict("PAYX") == "Watch"   # mature, slow growth

def test_cloud_verdicts():
    """Known-good verdicts for key cloud companies."""
    df = pd.read_csv("data/cloud_scored.csv")

    def verdict(ticker):
        return df[df["Ticker"] == ticker]["Verdict"].iloc[0]

    assert verdict("AMZN") == "Buy"     # hyperscaler quality, cheap
    assert verdict("MSFT") == "Watch"   # elite quality, expensive
    assert verdict("ORCL") == "Avoid"   # weak quality, fairly valued

    assert verdict("VRT")  == "Buy"     # strong quality, reasonable price
    assert verdict("SMCI") == "Avoid"   # weak quality, cheap

def test_cyber_verdicts():
    """Known-good verdicts for key cybersecurity companies."""
    df = pd.read_csv("data/cyber_scored.csv")

    def verdict(ticker):
        return df[df["Ticker"] == ticker]["Verdict"].iloc[0]

    assert verdict("CRWD") == "Watch"   # elite quality, expensive
    assert verdict("S")    == "Buy"     # strong quality, cheap
    assert verdict("FTNT") == "Buy"     # elite quality, reasonable price

    assert verdict("VRNT") == "Avoid"   # weak quality, cheap

def test_single_constituent_archetype_sanity():
    """INTC is the sole IDM constituent, so its hand-designed weights
    (scoring.py) have no second data point to sanity-check against.
    Pin its computed scores exactly so any accidental weight/threshold
    change to this archetype is caught immediately rather than assumed
    correct until a second ticker is added.
    """
    df = pd.read_csv("data/semis_scored.csv")
    row = df[df["Ticker"] == "INTC"].iloc[0]

    assert row["Archetype"] == "IDM"
    assert row["Quality Score"] == 49.2
    assert row["Valuation Score"] == 40
    assert row["Verdict"] == "Pass"

def test_weights_sum_to_one():
    """Every archetype's quality weights must sum to exactly 1.0."""
    from scoring import SCORING_CONFIG

    for archetype, config in SCORING_CONFIG.items():
        total = sum(config["quality_weights"].values())
        assert abs(total - 1.0) < 0.01, \
            f"{archetype} weights sum to {total}, not 1.0"

def test_archetype_coverage():
    """Every ticker in every UNIVERSE dict must resolve to a scored archetype.

    Catches drift between a vertical's UNIVERSE and SCORING_CONFIG (e.g. a
    typo'd or renamed archetype key), which score_row() silently swallows
    into "Insufficient Data" instead of raising.
    """
    from verticals import semis, cloud, saas, cyber

    verticals = {
        "semis": semis.UNIVERSE,
        "cloud": cloud.UNIVERSE,
        "saas": saas.UNIVERSE,
        "cyber": cyber.UNIVERSE,
    }

    failures = []
    for name, universe in verticals.items():
        df = pd.read_csv(f"data/{name}_scored.csv")
        for archetype, tickers in universe.items():
            for ticker in tickers:
                match = df[df["Ticker"] == ticker]
                if match.empty:
                    failures.append(f"{name}/{archetype}/{ticker}: missing from data/{name}_scored.csv")
                    continue
                verdict = match["Verdict"].iloc[0]
                if verdict == "Insufficient Data":
                    failures.append(f"{name}/{archetype}/{ticker}: Verdict is 'Insufficient Data'")

    assert not failures, "Archetype coverage gaps:\n" + "\n".join(failures)

def test_ai_exposure_no_unknowns():
    """Every company in the universe must have an AI Exposure label."""
    import pandas as pd
    from ai_exposure import AI_EXPOSURE

    all_df = pd.concat([
        pd.read_csv("data/semis_scored.csv"),
        pd.read_csv("data/cloud_scored.csv"),
        pd.read_csv("data/saas_scored.csv"),
        pd.read_csv("data/cyber_scored.csv"),
    ])

    unknowns = all_df[all_df["AI Exposure"] == "Unknown"]["Ticker"].tolist()
    assert len(unknowns) == 0, f"Missing AI Exposure for: {unknowns}"
