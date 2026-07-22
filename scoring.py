import pandas as pd

# --- Universal scoring function ---
def score_metric(value, thresholds):
    """
    Assigns a score of 1-5 based on thresholds.
    Thresholds is a list of (min, max, score) tuples.
    """
    if value is None:
        return None
    try:
        value = float(value)
    except (TypeError, ValueError):
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
    (4,  float("inf"),  1),
]

EV_FCF_THRESHOLDS = [
    (-float("inf"), 20,  5),
    (20,            35,  4),
    (35,            60,  3),
    (60,            100, 2),
    (100, float("inf"),  1),
]

RULE_OF_40_THRESHOLDS = [
    (-float("inf"), 20,  1),
    (20,            35,  2),
    (35,            50,  3),
    (50,            70,  4),
    (70,  float("inf"),  5),
]

HYPERSCALER_EV_REVENUE_THRESHOLDS = [
    (-float("inf"), 3,   5),
    (3,             6,   4),
    (6,             10,  3),
    (10,            15,  2),
    (15,  float("inf"),  1),
]

SAAS_EV_REVENUE_THRESHOLDS = [
    (-float("inf"), 5,   5),
    (5,             10,  4),
    (10,            20,  3),
    (20,            40,  2),
    (40,  float("inf"),  1),
]

ENTERPRISE_SAAS_EV_REVENUE_THRESHOLDS = [
    (-float("inf"), 2,   5),
    (2,             4,   4),
    (4,             7,   3),
    (7,             12,  2),
    (12, float("inf"),  1),
]

GM_TREND_THRESHOLDS = [
    (-float("inf"), -5,  1),  # significantly compressing
    (-5,             0,  2),  # slightly compressing
    (0,              3,  3),  # stable
    (3,              8,  4),  # modestly expanding
    (8,  float("inf"),  5),  # strongly expanding
]

COLLABORATION_EV_REVENUE_THRESHOLDS = [
    (-float("inf"), 2,   5),
    (2,             4,   4),
    (4,             6,   3),
    (6,             10,  2),
    (10, float("inf"),  1),
]

# R&D Intensity: banded, not monotonic — too low risks moat erosion, too high
# signals spend outpacing monetization. Split by hardware vs. software norms.
SEMIS_RND_THRESHOLDS = [
    (-float("inf"), 3,   1),
    (3,             7,   3),
    (7,             25,  5),
    (25,            40,  4),
    (40,  float("inf"),  2),
]

SOFTWARE_RND_THRESHOLDS = [
    (-float("inf"), 10,  2),
    (10,            20,  4),
    (20,            35,  5),
    (35,            50,  4),
    (50,  float("inf"),  3),
]
# --- Config registry ---

SCORING_CONFIG = {

    # --- Semiconductors ---
    "Foundry": {
"quality_weights": {
    "ROIC":             0.23,
    "FCF Margin":       0.18,
    "Gross Margin":     0.14,
    "GM Trend (3Y)":    0.09,
    "Op Margin":        0.14,
    "Rev CAGR (3Y)":    0.09,
    "Net Debt/EBITDA":  0.05,
    "R&D Intensity":    0.08,
},
"quality_thresholds": {
    "ROIC":             ROIC_THRESHOLDS,
    "FCF Margin":       FCF_MARGIN_THRESHOLDS,
    "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
    "GM Trend (3Y)":    GM_TREND_THRESHOLDS,  # NEW
    "Op Margin":        OP_MARGIN_THRESHOLDS,
    "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,
    "Net Debt/EBITDA":  NET_DEBT_EBITDA_THRESHOLDS,
    "R&D Intensity":    SEMIS_RND_THRESHOLDS,
},
        "valuation_metric":     "EV/FCF",
        "valuation_thresholds": EV_FCF_THRESHOLDS,
    },

    "Fabless": {
"quality_weights": {
    "ROIC":             0.23,
    "FCF Margin":       0.18,
    "Gross Margin":     0.14,
    "GM Trend (3Y)":    0.09,
    "Op Margin":        0.14,
    "Rev CAGR (3Y)":    0.09,
    "Net Debt/EBITDA":  0.05,
    "R&D Intensity":    0.08,
},
"quality_thresholds": {
    "ROIC":             ROIC_THRESHOLDS,
    "FCF Margin":       FCF_MARGIN_THRESHOLDS,
    "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
    "GM Trend (3Y)":    GM_TREND_THRESHOLDS,  # NEW
    "Op Margin":        OP_MARGIN_THRESHOLDS,
    "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,
    "Net Debt/EBITDA":  NET_DEBT_EBITDA_THRESHOLDS,
    "R&D Intensity":    SEMIS_RND_THRESHOLDS,
},
        "valuation_metric":     "EV/FCF",
        "valuation_thresholds": EV_FCF_THRESHOLDS,
    },

    "Equipment": {
"quality_weights": {
    "ROIC":             0.23,
    "FCF Margin":       0.18,
    "Gross Margin":     0.14,
    "GM Trend (3Y)":    0.09,
    "Op Margin":        0.14,
    "Rev CAGR (3Y)":    0.09,
    "Net Debt/EBITDA":  0.05,
    "R&D Intensity":    0.08,
},
"quality_thresholds": {
    "ROIC":             ROIC_THRESHOLDS,
    "FCF Margin":       FCF_MARGIN_THRESHOLDS,
    "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
    "GM Trend (3Y)":    GM_TREND_THRESHOLDS,  # NEW
    "Op Margin":        OP_MARGIN_THRESHOLDS,
    "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,
    "Net Debt/EBITDA":  NET_DEBT_EBITDA_THRESHOLDS,
    "R&D Intensity":    SEMIS_RND_THRESHOLDS,
},
        "valuation_metric":     "EV/FCF",
        "valuation_thresholds": EV_FCF_THRESHOLDS,
    },

    "IDM": {
"quality_weights": {
    "ROIC":             0.23,
    "FCF Margin":       0.18,
    "Gross Margin":     0.14,
    "GM Trend (3Y)":    0.09,
    "Op Margin":        0.14,
    "Rev CAGR (3Y)":    0.09,
    "Net Debt/EBITDA":  0.05,
    "R&D Intensity":    0.08,
},
"quality_thresholds": {
    "ROIC":             ROIC_THRESHOLDS,
    "FCF Margin":       FCF_MARGIN_THRESHOLDS,
    "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
    "GM Trend (3Y)":    GM_TREND_THRESHOLDS,  # NEW
    "Op Margin":        OP_MARGIN_THRESHOLDS,
    "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,
    "Net Debt/EBITDA":  NET_DEBT_EBITDA_THRESHOLDS,
    "R&D Intensity":    SEMIS_RND_THRESHOLDS,
},
        "valuation_metric":     "EV/FCF",
        "valuation_thresholds": EV_FCF_THRESHOLDS,
    },

    "Memory": {
"quality_weights": {
    "ROIC":             0.23,
    "FCF Margin":       0.18,
    "Gross Margin":     0.14,
    "GM Trend (3Y)":    0.09,
    "Op Margin":        0.14,
    "Rev CAGR (3Y)":    0.09,
    "Net Debt/EBITDA":  0.05,
    "R&D Intensity":    0.08,
},
"quality_thresholds": {
    "ROIC":             ROIC_THRESHOLDS,
    "FCF Margin":       FCF_MARGIN_THRESHOLDS,
    "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
    "GM Trend (3Y)":    GM_TREND_THRESHOLDS,  # NEW
    "Op Margin":        OP_MARGIN_THRESHOLDS,
    "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,
    "Net Debt/EBITDA":  NET_DEBT_EBITDA_THRESHOLDS,
    "R&D Intensity":    SEMIS_RND_THRESHOLDS,
},
        "valuation_metric":     "EV/FCF",
        "valuation_thresholds": EV_FCF_THRESHOLDS,
    },

    "EDA_IP": {
"quality_weights": {
    "ROIC":             0.23,
    "FCF Margin":       0.18,
    "Gross Margin":     0.14,
    "GM Trend (3Y)":    0.09,
    "Op Margin":        0.14,
    "Rev CAGR (3Y)":    0.09,
    "Net Debt/EBITDA":  0.05,
    "R&D Intensity":    0.08,
},
"quality_thresholds": {
    "ROIC":             ROIC_THRESHOLDS,
    "FCF Margin":       FCF_MARGIN_THRESHOLDS,
    "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
    "GM Trend (3Y)":    GM_TREND_THRESHOLDS,  # NEW
    "Op Margin":        OP_MARGIN_THRESHOLDS,
    "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,
    "Net Debt/EBITDA":  NET_DEBT_EBITDA_THRESHOLDS,
    "R&D Intensity":    SEMIS_RND_THRESHOLDS,
},
        "valuation_metric":     "EV/FCF",
        "valuation_thresholds": EV_FCF_THRESHOLDS,
    },

    "SUPPLY_CHAIN": {
"quality_weights": {
    "ROIC":             0.23,
    "FCF Margin":       0.18,
    "Gross Margin":     0.14,
    "GM Trend (3Y)":    0.09,
    "Op Margin":        0.14,
    "Rev CAGR (3Y)":    0.09,
    "Net Debt/EBITDA":  0.05,
    "R&D Intensity":    0.08,
},
"quality_thresholds": {
    "ROIC":             ROIC_THRESHOLDS,
    "FCF Margin":       FCF_MARGIN_THRESHOLDS,
    "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
    "GM Trend (3Y)":    GM_TREND_THRESHOLDS,  # NEW
    "Op Margin":        OP_MARGIN_THRESHOLDS,
    "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,
    "Net Debt/EBITDA":  NET_DEBT_EBITDA_THRESHOLDS,
    "R&D Intensity":    SEMIS_RND_THRESHOLDS,
},
        "valuation_metric":     "EV/FCF",
        "valuation_thresholds": EV_FCF_THRESHOLDS,
    },

    # --- Cloud ---
    "Hyperscaler": {
"quality_weights": {
    "FCF Margin":       0.25,  # reduced from 0.30
    "Op Margin":        0.20,  # reduced from 0.25
    "Gross Margin":     0.15,  # reduced from 0.20
    "GM Trend (3Y)":    0.10,  # NEW
    "Rev CAGR (3Y)":    0.15,
    "Net Debt/EBITDA":  0.10,  # unchanged
},
        "quality_thresholds": {
            "FCF Margin":       FCF_MARGIN_THRESHOLDS,
            "Op Margin":        OP_MARGIN_THRESHOLDS,
            "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
            "GM Trend (3Y)":    GM_TREND_THRESHOLDS, 
            "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,
            "Net Debt/EBITDA":  NET_DEBT_EBITDA_THRESHOLDS,
        },
        "valuation_metric":     "EV/Revenue",
        "valuation_thresholds": HYPERSCALER_EV_REVENUE_THRESHOLDS,
    },

    "Cloud_Data": {
"quality_weights": {
    "Rule of 40":       0.25,  # reduced from 0.30
    "FCF Margin":       0.20,  # reduced from 0.25
    "Gross Margin":     0.15,  # reduced from 0.20
    "GM Trend (3Y)":    0.10,  # NEW
    "Op Margin":        0.15,
    "Rev CAGR (3Y)":    0.10,  # reduced from 0.15
    "Net Debt/EBITDA":  0.05,
},
        "quality_thresholds": {
            "Rule of 40":       RULE_OF_40_THRESHOLDS,
            "FCF Margin":       FCF_MARGIN_THRESHOLDS,
            "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
            "Op Margin":        OP_MARGIN_THRESHOLDS,
            "GM Trend (3Y)":    GM_TREND_THRESHOLDS, 
            "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,
            "Net Debt/EBITDA":  NET_DEBT_EBITDA_THRESHOLDS,
        },
        "valuation_metric":     "EV/Revenue",
        "valuation_thresholds": SAAS_EV_REVENUE_THRESHOLDS,
    },

    # --- SaaS ---
"Enterprise_SaaS": {
    "quality_weights": {
        "FCF Margin":       0.25,
        "Rule of 40":       0.20,
        "Gross Margin":     0.15,
        "Op Margin":        0.15,
        "GM Trend (3Y)":    0.10,
        "Rev CAGR (3Y)":    0.10,
        "Net Debt/EBITDA":  0.05,
    },
    "quality_thresholds": {
        "FCF Margin":       FCF_MARGIN_THRESHOLDS,
        "Rule of 40":       RULE_OF_40_THRESHOLDS,
        "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
        "Op Margin":        OP_MARGIN_THRESHOLDS,
        "GM Trend (3Y)":    GM_TREND_THRESHOLDS,
        "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,
        "Net Debt/EBITDA":  NET_DEBT_EBITDA_THRESHOLDS,
    },
    "valuation_metric":     "EV/Revenue",
    "valuation_thresholds": ENTERPRISE_SAAS_EV_REVENUE_THRESHOLDS,
},
"Enterprise_AI": {
    "quality_weights": {
        "Gross Margin":     0.23,
        "Rule of 40":       0.23,
        "Rev CAGR (3Y)":    0.18,
        "FCF Margin":       0.14,
        "GM Trend (3Y)":    0.09,
        "Op Margin":        0.05,
        "R&D Intensity":    0.08,
    },
    "quality_thresholds": {
        "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
        "Rule of 40":       RULE_OF_40_THRESHOLDS,
        "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,
        "FCF Margin":       FCF_MARGIN_THRESHOLDS,
        "GM Trend (3Y)":    GM_TREND_THRESHOLDS,
        "Op Margin":        OP_MARGIN_THRESHOLDS,
        "R&D Intensity":    SOFTWARE_RND_THRESHOLDS,
    },
    "valuation_metric":     "EV/Revenue",
    "valuation_thresholds": SAAS_EV_REVENUE_THRESHOLDS,
},
"Vertical_SaaS": {
    "quality_weights": {
        "Gross Margin":     0.25,  # vertical moat signal
        "FCF Margin":       0.25,  # cash generation validates moat
        "Op Margin":        0.20,  # operational efficiency
        "GM Trend (3Y)":    0.15,  # moat durability over time
        "Rule of 40":       0.10,  # growth/profitability balance
        "Rev CAGR (3Y)":    0.05,  # durability > growth for verticals
    },
    "quality_thresholds": {
        "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
        "FCF Margin":       FCF_MARGIN_THRESHOLDS,
        "Op Margin":        OP_MARGIN_THRESHOLDS,
        "GM Trend (3Y)":    GM_TREND_THRESHOLDS,
        "Rule of 40":       RULE_OF_40_THRESHOLDS,
        "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,
    },
    "valuation_metric":     "EV/Revenue",
    "valuation_thresholds": SAAS_EV_REVENUE_THRESHOLDS,
},
"DevOps": {
    "quality_weights": {
        "Rule of 40":       0.28,  # primary quality signal
        "Rev CAGR (3Y)":    0.18,  # growth trajectory matters most
        "Gross Margin":     0.18,  # platform moat signal
        "FCF Margin":       0.14,  # real cash generation
        "GM Trend (3Y)":    0.09,  # moat durability
        "Op Margin":        0.05,  # low weight — GAAP artifact
        "R&D Intensity":    0.08,
    },
    "quality_thresholds": {
        "Rule of 40":       RULE_OF_40_THRESHOLDS,
        "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,
        "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
        "FCF Margin":       FCF_MARGIN_THRESHOLDS,
        "GM Trend (3Y)":    GM_TREND_THRESHOLDS,
        "Op Margin":        OP_MARGIN_THRESHOLDS,
        "R&D Intensity":    SOFTWARE_RND_THRESHOLDS,
    },
    "valuation_metric":     "EV/Revenue",
    "valuation_thresholds": SAAS_EV_REVENUE_THRESHOLDS,
},


    "Collaboration": {
"quality_weights": {
"FCF Margin":       0.25,  # cash generation is the only thesis
"Op Margin":        0.25,
"Gross Margin":     0.20,
"GM Trend (3Y)":    0.10,
"Rule of 40":       0.10,  # less relevant for slow growers
"Rev CAGR (3Y)":    0.10,  # growth is minimal, weight it low

},
        "quality_thresholds": {
            "Rule of 40":       RULE_OF_40_THRESHOLDS,
            "FCF Margin":       FCF_MARGIN_THRESHOLDS,
            "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
            "Op Margin":        OP_MARGIN_THRESHOLDS,
            "GM Trend (3Y)":    GM_TREND_THRESHOLDS, 
            "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,

        },
        "valuation_metric":     "EV/Revenue",
        "valuation_thresholds": COLLABORATION_EV_REVENUE_THRESHOLDS
    },

    # --- Cybersecurity ---
    "ENDPOINT": {
"quality_weights": {
    "Rule of 40":       0.30,  # early-stage platform — growth+profit blend is the thesis
    "Rev CAGR (3Y)":    0.25,  # high growth is the core signal at this stage
    "Gross Margin":     0.15,  # platform moat
    "FCF Margin":       0.15,  # real cash generation despite GAAP losses
    "GM Trend (3Y)":    0.10,  # moat durability
    "Op Margin":        0.05,  # low weight — negative GAAP margins are accounting artifacts
},
        "quality_thresholds": {
            "Rule of 40":       RULE_OF_40_THRESHOLDS,
            "FCF Margin":       FCF_MARGIN_THRESHOLDS,
            "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
            "Op Margin":        OP_MARGIN_THRESHOLDS,
            "GM Trend (3Y)":    GM_TREND_THRESHOLDS,
            "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,
        },
        "valuation_metric":     "EV/Revenue",
        "valuation_thresholds": SAAS_EV_REVENUE_THRESHOLDS,
    },

    "NETWORK": {
"quality_weights": {
    "FCF Margin":       0.25,  # mature platform — real cash generation matters most
    "Op Margin":        0.25,  # real GAAP profitability, not an artifact at this stage
    "Gross Margin":     0.15,
    "GM Trend (3Y)":    0.10,
    "Rule of 40":       0.10,  # secondary to raw profitability here
    "Rev CAGR (3Y)":    0.10,  # growth weighted below profitability
    "Net Debt/EBITDA":  0.05,
},
        "quality_thresholds": {
            "Rule of 40":       RULE_OF_40_THRESHOLDS,
            "FCF Margin":       FCF_MARGIN_THRESHOLDS,
            "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
            "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,
            "Op Margin":        OP_MARGIN_THRESHOLDS,
            "GM Trend (3Y)":    GM_TREND_THRESHOLDS,
            "Net Debt/EBITDA":  NET_DEBT_EBITDA_THRESHOLDS,
        },
        "valuation_metric":     "EV/Revenue",
        "valuation_thresholds": SAAS_EV_REVENUE_THRESHOLDS,
    },

    "IDENTITY": {
"quality_weights": {
    "Gross Margin":     0.20,  # switching-cost moat signal
    "Rule of 40":       0.20,  # balanced growth/profit blend
    "FCF Margin":       0.20,  # balanced growth/profit blend
    "Op Margin":        0.15,
    "Rev CAGR (3Y)":    0.15,
    "GM Trend (3Y)":    0.10,
},
        "quality_thresholds": {
            "Rule of 40":       RULE_OF_40_THRESHOLDS,
            "FCF Margin":       FCF_MARGIN_THRESHOLDS,
            "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
            "Op Margin":        OP_MARGIN_THRESHOLDS,
            "GM Trend (3Y)":    GM_TREND_THRESHOLDS,
            "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,
        },
        "valuation_metric":     "EV/Revenue",
        "valuation_thresholds": SAAS_EV_REVENUE_THRESHOLDS,
    },

    "CLOUD_SEC": {
"quality_weights": {
    "Rule of 40":       0.25,
    "FCF Margin":       0.20,
    "Gross Margin":     0.15,
    "GM Trend (3Y)":    0.10,
    "Op Margin":        0.15,
    "Rev CAGR (3Y)":    0.10,
    "Net Debt/EBITDA":  0.05,
},
        "quality_thresholds": {
            "Rule of 40":       RULE_OF_40_THRESHOLDS,
            "FCF Margin":       FCF_MARGIN_THRESHOLDS,
            "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
            "Op Margin":        OP_MARGIN_THRESHOLDS,
            "GM Trend (3Y)":    GM_TREND_THRESHOLDS, 
            "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,
            "Net Debt/EBITDA":  NET_DEBT_EBITDA_THRESHOLDS,
        },
        "valuation_metric":     "EV/Revenue",
        "valuation_thresholds": SAAS_EV_REVENUE_THRESHOLDS,
    },

    "DATA_SEC": {
"quality_weights": {
    "FCF Margin":       0.25,  # mature tooling — profitability matters most
    "Op Margin":        0.20,
    "Gross Margin":     0.20,
    "GM Trend (3Y)":    0.10,
    "Net Debt/EBITDA":  0.10,
    "Rule of 40":       0.10,
    "Rev CAGR (3Y)":    0.05,  # growth least important at this stage
},
        "quality_thresholds": {
            "Rule of 40":       RULE_OF_40_THRESHOLDS,
            "FCF Margin":       FCF_MARGIN_THRESHOLDS,
            "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
            "Op Margin":        OP_MARGIN_THRESHOLDS,
            "GM Trend (3Y)":    GM_TREND_THRESHOLDS, 
            "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,
            "Net Debt/EBITDA":  NET_DEBT_EBITDA_THRESHOLDS,
        },
        "valuation_metric":     "EV/Revenue",
        "valuation_thresholds": SAAS_EV_REVENUE_THRESHOLDS,
    },
}


# --- Universal scoring functions ---

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


def score_row(row):
    archetype = row.get("Archetype")
    config = SCORING_CONFIG.get(archetype)

    if config is None:
        return pd.Series({
            "Quality Score":   None,
            "Valuation Score": None,
            "Verdict":         "Insufficient Data",
        })

    # Quality score
    total_weight = 0
    weighted_sum = 0
    for metric, weight in config["quality_weights"].items():
        thresholds = config["quality_thresholds"][metric]
        score = score_metric(row.get(metric), thresholds)
        if score is not None:
            weighted_sum += score * weight
            total_weight += weight

    quality = round(weighted_sum / total_weight * 20, 1) if total_weight > 0 else None

    # Valuation score
    val_metric     = config["valuation_metric"]
    val_thresholds = config["valuation_thresholds"]
    val_score      = score_metric(row.get(val_metric), val_thresholds)
    valuation      = round(val_score * 20, 1) if val_score is not None else None

    verdict = get_verdict(quality, valuation)

    return pd.Series({
        "Quality Score":   quality,
        "Valuation Score": valuation,
        "Verdict":         verdict,
    })


def score_dataframe(df):
    scores = df.apply(score_row, axis=1)
    return pd.concat([df, scores], axis=1)