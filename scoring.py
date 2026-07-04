# scoring.py

def score_metric(value, thresholds):
    """
    Assigns a score of 1-5 based on thresholds.
    Thresholds is a list of (min, max, score) tuples.
    """
    if value is None:
        return None
    for min_val, max_val, score in thresholds:
        if min_val <= value < max_val:
            return score
    return None

# --- Threshold definitions ---

ROIC_THRESHOLDS = [
    (-float("inf"), 5,   1),
    (5,             15,  2),
    (15,            25,  3),
    (25,            40,  4),
    (40,  float("inf"),  5),
]

FCF_MARGIN_THRESHOLDS = [
    (-float("inf"), 0,   1),
    (0,             10,  2),
    (10,            20,  3),
    (20,            30,  4),
    (30,  float("inf"),  5),
]

GROSS_MARGIN_THRESHOLDS = [
    (-float("inf"), 20,  1),
    (20,            35,  2),
    (35,            50,  3),
    (50,            65,  4),
    (65,  float("inf"),  5),
]

OP_MARGIN_THRESHOLDS = [
    (-float("inf"), 0,   1),
    (0,             10,  2),
    (10,            20,  3),
    (20,            35,  4),
    (35,  float("inf"),  5),
]

REV_GROWTH_THRESHOLDS = [
    (-float("inf"), 0,   1),
    (0,             5,   2),
    (5,             15,  3),
    (15,            30,  4),
    (30,  float("inf"),  5),
]

NET_DEBT_EBITDA_THRESHOLDS = [
    (-float("inf"), 0,   5),
    (0,             1,   4),
    (1,             2,   3),
    (2,             4,   2),
    (4,  float("inf"),   1),
]

EV_FCF_THRESHOLDS = [
    (-float("inf"), 20,  5),
    (20,            35,  4),
    (35,            60,  3),
    (60,            100, 2),
    (100, float("inf"),  1),
]

# --- SaaS / Cyber thresholds ---

RULE_OF_40_THRESHOLDS = [
    (-float("inf"), 20,  1),
    (20,            35,  2),
    (35,            50,  3),
    (50,            70,  4),
    (70,  float("inf"),  5),
]

EV_REVENUE_THRESHOLDS = [
    (-float("inf"), 5,   5),
    (5,             10,  4),
    (10,            20,  3),
    (20,            40,  2),
    (40,  float("inf"),  1),
]

# --- Weights ---

SEMI_QUALITY_WEIGHTS = {
    "ROIC":              0.25,
    "FCF Margin":        0.20,
    "Gross Margin":      0.20,
    "Op Margin":         0.15,
    "Rev Growth (YoY)":  0.15,
    "Net Debt/EBITDA":   0.05,
}

SAAS_QUALITY_WEIGHTS = {
    "Rule of 40":        0.30,
    "FCF Margin":        0.25,
    "Gross Margin":      0.20,
    "Rev Growth (YoY)":  0.15,
    "Net Debt/EBITDA":   0.10,
}

# --- Scorers ---

def score_semi_quality(row):
    scores = {
        "ROIC":             score_metric(row.get("ROIC"),             ROIC_THRESHOLDS),
        "FCF Margin":       score_metric(row.get("FCF Margin"),       FCF_MARGIN_THRESHOLDS),
        "Gross Margin":     score_metric(row.get("Gross Margin"),     GROSS_MARGIN_THRESHOLDS),
        "Op Margin":        score_metric(row.get("Op Margin"),        OP_MARGIN_THRESHOLDS),
        "Rev Growth (YoY)": score_metric(row.get("Rev Growth (YoY)"), REV_GROWTH_THRESHOLDS),
        "Net Debt/EBITDA":  score_metric(row.get("Net Debt/EBITDA"),  NET_DEBT_EBITDA_THRESHOLDS),
    }

    total_weight = 0
    weighted_sum = 0
    for metric, weight in SEMI_QUALITY_WEIGHTS.items():
        if scores[metric] is not None:
            weighted_sum += scores[metric] * weight
            total_weight += weight

    quality = round(weighted_sum / total_weight * 20, 1) if total_weight > 0 else None
    return quality


def score_semi_valuation(row):
    ev_fcf_score = score_metric(row.get("EV/FCF"), EV_FCF_THRESHOLDS)
    if ev_fcf_score is None:
        return None
    return round(ev_fcf_score * 20, 1)


def score_saas_quality(row):
    scores = {
        "Rule of 40":       score_metric(row.get("Rule of 40"),      RULE_OF_40_THRESHOLDS),
        "FCF Margin":       score_metric(row.get("FCF Margin"),       FCF_MARGIN_THRESHOLDS),
        "Gross Margin":     score_metric(row.get("Gross Margin"),     GROSS_MARGIN_THRESHOLDS),
        "Rev Growth (YoY)": score_metric(row.get("Rev Growth (YoY)"), REV_GROWTH_THRESHOLDS),
        "Net Debt/EBITDA":  score_metric(row.get("Net Debt/EBITDA"),  NET_DEBT_EBITDA_THRESHOLDS),
    }

    total_weight = 0
    weighted_sum = 0
    for metric, weight in SAAS_QUALITY_WEIGHTS.items():
        if scores[metric] is not None:
            weighted_sum += scores[metric] * weight
            total_weight += weight

    quality = round(weighted_sum / total_weight * 20, 1) if total_weight > 0 else None
    return quality

def score_saas_valuation(row):
    ev_rev_score = score_metric(row.get("EV/Revenue"), EV_REVENUE_THRESHOLDS)
    if ev_rev_score is None:
        return None
    return round(ev_rev_score * 20, 1)

def get_verdict(quality, valuation):
    if quality is None or valuation is None:
        return "Insufficient Data"
    if quality >= 60 and valuation >= 60:
        return "Buy"
    elif quality >= 60 and valuation < 60:
        return "Watch"
    elif quality < 60 and valuation >= 60:
        return "Avoid"
    else:
        return "Pass"


def score_dataframe(df):
    df = df.copy()
    df["Quality Score"] = df.apply(score_semi_quality, axis=1)
    df["Valuation Score"] = df.apply(score_semi_valuation, axis=1)
    df["Verdict"] = df.apply(
        lambda row: get_verdict(row["Quality Score"], row["Valuation Score"]), axis=1
    )
    return df

def score_saas_dataframe(df):
    df = df.copy()
    df["Quality Score"]   = df.apply(score_saas_quality, axis=1)
    df["Valuation Score"] = df.apply(score_saas_valuation, axis=1)
    df["Verdict"]         = df.apply(
        lambda row: get_verdict(row["Quality Score"], row["Valuation Score"]), axis=1
    )
    return df