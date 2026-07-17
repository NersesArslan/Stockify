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
# --- Config registry ---

SCORING_CONFIG = {

    # --- Semiconductors ---
    "Foundry": {
"quality_weights": {
    "ROIC":             0.25,
    "FCF Margin":       0.20,
    "Gross Margin":     0.15,  # reduced from 0.20
    "GM Trend (3Y)":    0.10,  # NEW
    "Op Margin":        0.15,
    "Rev CAGR (3Y)":    0.10,  # reduced from 0.15
    "Net Debt/EBITDA":  0.05,
},
"quality_thresholds": {
    "ROIC":             ROIC_THRESHOLDS,
    "FCF Margin":       FCF_MARGIN_THRESHOLDS,
    "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
    "GM Trend (3Y)":    GM_TREND_THRESHOLDS,  # NEW
    "Op Margin":        OP_MARGIN_THRESHOLDS,
    "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,
    "Net Debt/EBITDA":  NET_DEBT_EBITDA_THRESHOLDS,
},
        "valuation_metric":     "EV/FCF",
        "valuation_thresholds": EV_FCF_THRESHOLDS,
    },

    "Fabless": {
"quality_weights": {
    "ROIC":             0.25,
    "FCF Margin":       0.20,
    "Gross Margin":     0.15,  # reduced from 0.20
    "GM Trend (3Y)":    0.10,  # NEW
    "Op Margin":        0.15,
    "Rev CAGR (3Y)":    0.10,  # reduced from 0.15
    "Net Debt/EBITDA":  0.05,
},
"quality_thresholds": {
    "ROIC":             ROIC_THRESHOLDS,
    "FCF Margin":       FCF_MARGIN_THRESHOLDS,
    "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
    "GM Trend (3Y)":    GM_TREND_THRESHOLDS,  # NEW
    "Op Margin":        OP_MARGIN_THRESHOLDS,
    "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,
    "Net Debt/EBITDA":  NET_DEBT_EBITDA_THRESHOLDS,
},
        "valuation_metric":     "EV/FCF",
        "valuation_thresholds": EV_FCF_THRESHOLDS,
    },

    "Equipment": {
"quality_weights": {
    "ROIC":             0.25,
    "FCF Margin":       0.20,
    "Gross Margin":     0.15,  # reduced from 0.20
    "GM Trend (3Y)":    0.10,  # NEW
    "Op Margin":        0.15,
    "Rev CAGR (3Y)":    0.10,  # reduced from 0.15
    "Net Debt/EBITDA":  0.05,
},
"quality_thresholds": {
    "ROIC":             ROIC_THRESHOLDS,
    "FCF Margin":       FCF_MARGIN_THRESHOLDS,
    "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
    "GM Trend (3Y)":    GM_TREND_THRESHOLDS,  # NEW
    "Op Margin":        OP_MARGIN_THRESHOLDS,
    "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,
    "Net Debt/EBITDA":  NET_DEBT_EBITDA_THRESHOLDS,
},
        "valuation_metric":     "EV/FCF",
        "valuation_thresholds": EV_FCF_THRESHOLDS,
    },

    "IDM": {
"quality_weights": {
    "ROIC":             0.25,
    "FCF Margin":       0.20,
    "Gross Margin":     0.15,  # reduced from 0.20
    "GM Trend (3Y)":    0.10,  # NEW
    "Op Margin":        0.15,
    "Rev CAGR (3Y)":    0.10,  # reduced from 0.15
    "Net Debt/EBITDA":  0.05,
},
"quality_thresholds": {
    "ROIC":             ROIC_THRESHOLDS,
    "FCF Margin":       FCF_MARGIN_THRESHOLDS,
    "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
    "GM Trend (3Y)":    GM_TREND_THRESHOLDS,  # NEW
    "Op Margin":        OP_MARGIN_THRESHOLDS,
    "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,
    "Net Debt/EBITDA":  NET_DEBT_EBITDA_THRESHOLDS,
},
        "valuation_metric":     "EV/FCF",
        "valuation_thresholds": EV_FCF_THRESHOLDS,
    },

    "Memory": {
"quality_weights": {
    "ROIC":             0.25,
    "FCF Margin":       0.20,
    "Gross Margin":     0.15,  # reduced from 0.20
    "GM Trend (3Y)":    0.10,  # NEW
    "Op Margin":        0.15,
    "Rev CAGR (3Y)":    0.10,  # reduced from 0.15
    "Net Debt/EBITDA":  0.05,
},
"quality_thresholds": {
    "ROIC":             ROIC_THRESHOLDS,
    "FCF Margin":       FCF_MARGIN_THRESHOLDS,
    "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
    "GM Trend (3Y)":    GM_TREND_THRESHOLDS,  # NEW
    "Op Margin":        OP_MARGIN_THRESHOLDS,
    "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,
    "Net Debt/EBITDA":  NET_DEBT_EBITDA_THRESHOLDS,
},
        "valuation_metric":     "EV/FCF",
        "valuation_thresholds": EV_FCF_THRESHOLDS,
    },

    "EDA_IP": {
"quality_weights": {
    "ROIC":             0.25,
    "FCF Margin":       0.20,
    "Gross Margin":     0.15,  # reduced from 0.20
    "GM Trend (3Y)":    0.10,  # NEW
    "Op Margin":        0.15,
    "Rev CAGR (3Y)":    0.10,  # reduced from 0.15
    "Net Debt/EBITDA":  0.05,
},
"quality_thresholds": {
    "ROIC":             ROIC_THRESHOLDS,
    "FCF Margin":       FCF_MARGIN_THRESHOLDS,
    "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
    "GM Trend (3Y)":    GM_TREND_THRESHOLDS,  # NEW
    "Op Margin":        OP_MARGIN_THRESHOLDS,
    "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,
    "Net Debt/EBITDA":  NET_DEBT_EBITDA_THRESHOLDS,
},
        "valuation_metric":     "EV/FCF",
        "valuation_thresholds": EV_FCF_THRESHOLDS,
    },

    "SUPPLY_CHAIN": {
"quality_weights": {
    "ROIC":             0.25,
    "FCF Margin":       0.20,
    "Gross Margin":     0.15,  # reduced from 0.20
    "GM Trend (3Y)":    0.10,  # NEW
    "Op Margin":        0.15,
    "Rev CAGR (3Y)":    0.10,  # reduced from 0.15
    "Net Debt/EBITDA":  0.05,
},
"quality_thresholds": {
    "ROIC":             ROIC_THRESHOLDS,
    "FCF Margin":       FCF_MARGIN_THRESHOLDS,
    "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
    "GM Trend (3Y)":    GM_TREND_THRESHOLDS,  # NEW
    "Op Margin":        OP_MARGIN_THRESHOLDS,
    "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,
    "Net Debt/EBITDA":  NET_DEBT_EBITDA_THRESHOLDS,
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
    "CRM_Sales": {
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

    "HR_Mgmt": {
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

    "ERP_Finance": {
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

    "DevOps": {
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

    "Data_Analytics": {
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

    "Vertical_SaaS": {
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

    "NETWORK": {
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