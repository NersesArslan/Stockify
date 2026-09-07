import pandas as pd
from scoring import score_dataframe, SCORING_CONFIG
from verticals import semis, cloud, saas, cyber

# Fixture rows are hand-authored, fixed-forever metric values — not live
# fetch data. That means these tests only ever fail when scoring.py's
# weights/thresholds/logic change, never because a stock's price or
# fundamentals moved since the fixture was written. See tests/fixtures/
# synthetic_universe.csv for the full row values and the band each metric
# was placed in.
FIXTURE_PATH = "tests/fixtures/synthetic_universe.csv"


def _scored_fixture():
    df = pd.read_csv(FIXTURE_PATH)
    return score_dataframe(df).set_index("Ticker")


def test_elite_quality_expensive_is_watch():
    """Every metric in band 5 (quality=100) but a rich EV/FCF (band 1) —
    the NVDA/TSM shape: too good to Pass/Avoid, too expensive to Buy."""
    row = _scored_fixture().loc["FAB_ELITE"]
    assert row["Quality Score"] == 100.0
    assert row["Valuation Score"] == 20.0
    assert row["Verdict"] == "Watch"


def test_solid_quality_cheap_is_buy():
    """Every metric in band 4 (quality=80) with a cheap EV/FCF (band 5)."""
    row = _scored_fixture().loc["FAB_BUY"]
    assert row["Quality Score"] == 80.0
    assert row["Valuation Score"] == 100.0
    assert row["Verdict"] == "Buy"


def test_weak_quality_cheap_is_avoid():
    """Every metric in band 1 (quality=20) but still cheap on EV/FCF —
    cheap for a reason, not a bargain."""
    row = _scored_fixture().loc["FAB_AVOID"]
    assert row["Quality Score"] == 20.0
    assert row["Valuation Score"] == 100.0
    assert row["Verdict"] == "Avoid"


def test_weak_quality_expensive_is_pass():
    """Same weak fundamentals as FAB_AVOID, but also expensive — no case
    for touching it at all."""
    row = _scored_fixture().loc["FAB_PASS"]
    assert row["Quality Score"] == 20.0
    assert row["Valuation Score"] == 20.0
    assert row["Verdict"] == "Pass"


def test_single_constituent_archetype_sanity():
    """IDM's weights have no second real constituent to sanity-check
    against, so this pins an exact weighted-average result computed from
    metrics spread across five different bands (not all-5s or all-4s,
    which would stay unchanged under most weight edits). Any accidental
    change to IDM's weights or thresholds shifts this number and fails
    the test immediately.
    """
    row = _scored_fixture().loc["IDM_SANITY"]
    assert row["Quality Score"] == 68.8
    assert row["Valuation Score"] == 60.0
    assert row["Verdict"] == "Buy"


def test_negative_ev_fcf_falls_back_to_ev_revenue():
    """Regression test for the negative-EV-FCF bug (fixed in
    443b909/PR #2): EV/FCF = -50 must not match any band (thresholds
    now start at 0, not -inf) and must fall back to EV/Revenue instead
    of silently scoring as maximally cheap."""
    row = _scored_fixture().loc["FAB_NEGEV_FALLBACK"]
    assert row["Valuation Score"] == 60.0
    assert row["Verdict"] == "Buy"


def test_negative_ev_fcf_with_no_fallback_is_insufficient_data():
    """Same negative EV/FCF, but EV/Revenue is also missing — valuation
    must come back undefined (None), not maximally cheap, and the verdict
    must reflect that rather than silently defaulting to a score."""
    row = _scored_fixture().loc["FAB_NEGEV_INSUFFICIENT"]
    assert pd.isna(row["Valuation Score"])
    assert row["Verdict"] == "Insufficient Data"


def test_unknown_archetype_is_insufficient_data():
    """A ticker whose Archetype doesn't match any SCORING_CONFIG key
    (e.g. a typo, or a UNIVERSE entry added without a matching config)
    must score as Insufficient Data, not silently crash or default."""
    row = _scored_fixture().loc["UNKNOWN_ARCHETYPE"]
    assert pd.isna(row["Quality Score"])
    assert pd.isna(row["Valuation Score"])
    assert row["Verdict"] == "Insufficient Data"


def test_weights_sum_to_one():
    """Every archetype's quality weights must sum to exactly 1.0."""
    for archetype, config in SCORING_CONFIG.items():
        total = sum(config["quality_weights"].values())
        assert abs(total - 1.0) < 0.01, \
            f"{archetype} weights sum to {total}, not 1.0"


def test_archetype_coverage():
    """Every ticker in every UNIVERSE dict must resolve to a scored archetype.

    Catches drift between a vertical's UNIVERSE and SCORING_CONFIG (e.g. a
    typo'd or renamed archetype key), which score_row() silently swallows
    into "Insufficient Data" instead of raising. This one intentionally
    reads the live, committed data — it's checking today's real universe
    for gaps, not pinning a score value, so it's supposed to track
    whatever is currently in data/.
    """
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
    """Every company in the universe must have an AI Exposure label.
    Reads live data deliberately, same reasoning as test_archetype_coverage.
    """
    all_df = pd.concat([
        pd.read_csv("data/semis_scored.csv"),
        pd.read_csv("data/cloud_scored.csv"),
        pd.read_csv("data/saas_scored.csv"),
        pd.read_csv("data/cyber_scored.csv"),
    ])

    unknowns = all_df[all_df["AI Exposure"] == "Unknown"]["Ticker"].tolist()
    assert len(unknowns) == 0, f"Missing AI Exposure for: {unknowns}"
