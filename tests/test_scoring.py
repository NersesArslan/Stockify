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
    assert verdict("QCOM") == "Buy"     # solid quality, cheap
    assert verdict("RMBS") == "Buy"     # IP licensing moat, reasonable price

    # Distressed names — should always be Pass or Avoid
    assert verdict("WOLF") == "Avoid"
    assert verdict("INTC") == "Pass"

def test_saas_verdicts():
    """Known-good verdicts for key SaaS companies."""
    df = pd.read_csv("data/saas_scored.csv")

    def verdict(ticker):
        return df[df["Ticker"] == ticker]["Verdict"].iloc[0]

    assert verdict("PLTR") == "Watch"   # exceptional quality, too expensive
    assert verdict("CRM")  == "Buy"     # quality at reasonable price
    assert verdict("BOX")  == "Watch"   # mature, slow growth

def test_weights_sum_to_one():
    """Every archetype's quality weights must sum to exactly 1.0."""
    from scoring import SCORING_CONFIG

    for archetype, config in SCORING_CONFIG.items():
        total = sum(config["quality_weights"].values())
        assert abs(total - 1.0) < 0.01, \
            f"{archetype} weights sum to {total}, not 1.0"

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
