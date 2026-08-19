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

SEMIS_EV_REVENUE_THRESHOLDS = [
    (-float("inf"), 3,   5),  # cheap for semis
    (3,             6,   4),  # reasonable
    (6,             10,  3),  # fair value
    (10,            15,  2),  # expensive
    (15, float("inf"),  1),  # very expensive
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

DEVOPS_EV_REVENUE_THRESHOLDS = [
    (-float("inf"), 2,   5),
    (2,             4,   4),
    (4,             6,   3),
    (6,             10,  2),
    (10, float("inf"),  1),
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

# ROIC Trend (3Y): monotonic, unlike R&D Intensity — improving capital
# efficiency is unambiguously good, deteriorating is unambiguously bad.
ROIC_TREND_THRESHOLDS = [
    (-float("inf"), -10,  1),  # severe deterioration
    (-10,            -3,  2),  # meaningful deterioration
    (-3,              3,  3),  # stable
    (3,              10,  4),  # improving
    (10,  float("inf"),  5),  # strongly improving
]

# FCF Margin Trend (3Y): monotonic, same shape as ROIC Trend — improving cash
# conversion is unambiguously good, deteriorating is unambiguously bad.
FCF_MARGIN_TREND_THRESHOLDS = [
    (-float("inf"), -10,  1),  # severe deterioration
    (-10,            -3,  2),  # meaningful deterioration
    (-3,              3,  3),  # stable
    (3,              10,  4),  # improving
    (10,  float("inf"),  5),  # strongly improving
]

# Revenue per Employee ($K): wired into semis and USD-reporting SaaS archetypes.
# Foreign filers (e.g. TSM, UMC) are normalized to USD in verticals/semis.py via
# the financialCurrency FX conversion before this metric is computed.
REV_PER_EMPLOYEE_THRESHOLDS = [
    (-float("inf"), 300, 1),
    (300,           450, 2),
    (450,           600, 3),
    (600,           900, 4),
    (900, float("inf"),  5),
]

# Revenue per Employee ($K), IT services scale: staffing-heavy consulting/
# outsourcing firms (e.g. ACN, CTSH) run at a fraction of software companies'
# per-employee revenue by business-model design — REV_PER_EMPLOYEE_THRESHOLDS
# above would bottom both out at 1 with no differentiation.
IT_SERVICES_REV_PER_EMPLOYEE_THRESHOLDS = [
    (-float("inf"), 50,   1),  # very low efficiency
    (50,            70,   2),  # below average — CTSH territory
    (70,            90,   3),  # average — ACN territory
    (90,            120,  4),  # strong
    (120, float("inf"),  5),  # exceptional for IT services
]
# --- Config registry ---

SCORING_CONFIG = {

    # --- Semiconductors ---
    "Foundry": {
"quality_weights": {
    # Scale, capital-intensive business — ROIC is the biggest differentiator
    # between disciplined operators and laggards; leverage matters given
    # enormous fab capex. Rev/Employee de-weighted: fabs are capital-heavy,
    # not headcount-leveraged.
    "ROIC":             0.21,
    "FCF Margin":       0.13,
    "Gross Margin":     0.12,
    "Op Margin":        0.11,
    "Net Debt/EBITDA":  0.07,
    "R&D Intensity":    0.07,
    "GM Trend (3Y)":    0.07,
    "ROIC Trend (3Y)":  0.07,
    "Rev CAGR (3Y)":    0.06,
    "Revenue per Employee ($K)": 0.03,
    "FCF Margin Trend (3Y)": 0.06,
},
"quality_thresholds": {
    "ROIC":             ROIC_THRESHOLDS,
    "FCF Margin":       FCF_MARGIN_THRESHOLDS,
    "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
    "GM Trend (3Y)":    GM_TREND_THRESHOLDS,  # NEW
    "ROIC Trend (3Y)":  ROIC_TREND_THRESHOLDS,  # NEW
    "FCF Margin Trend (3Y)": FCF_MARGIN_TREND_THRESHOLDS,  # NEW
    "Op Margin":        OP_MARGIN_THRESHOLDS,
    "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,
    "Net Debt/EBITDA":  NET_DEBT_EBITDA_THRESHOLDS,
    "R&D Intensity":    SEMIS_RND_THRESHOLDS,
    "Revenue per Employee ($K)": REV_PER_EMPLOYEE_THRESHOLDS,
},
        "valuation_metric":     "EV/FCF",
        "valuation_thresholds": EV_FCF_THRESHOLDS,
    },

    "Fabless": {
"quality_weights": {
    # Asset-light, IP-driven — R&D and headcount leverage are the moat;
    # growth is a real quality signal here (capturing AI buildout upside),
    # unlike capex-heavy archetypes. Rarely levered, so debt weight is low.
    "ROIC":             0.18,
    "FCF Margin":       0.14,
    "Gross Margin":     0.10,
    "Op Margin":        0.10,
    "Rev CAGR (3Y)":    0.10,
    "R&D Intensity":    0.08,
    "Revenue per Employee ($K)": 0.07,
    "GM Trend (3Y)":    0.07,
    "ROIC Trend (3Y)":  0.07,
    "Net Debt/EBITDA":  0.03,
    "FCF Margin Trend (3Y)": 0.06,
},
"quality_thresholds": {
    "ROIC":             ROIC_THRESHOLDS,
    "FCF Margin":       FCF_MARGIN_THRESHOLDS,
    "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
    "GM Trend (3Y)":    GM_TREND_THRESHOLDS,  # NEW
    "ROIC Trend (3Y)":  ROIC_TREND_THRESHOLDS,  # NEW
    "FCF Margin Trend (3Y)": FCF_MARGIN_TREND_THRESHOLDS,  # NEW
    "Op Margin":        OP_MARGIN_THRESHOLDS,
    "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,
    "Net Debt/EBITDA":  NET_DEBT_EBITDA_THRESHOLDS,
    "R&D Intensity":    SEMIS_RND_THRESHOLDS,
    "Revenue per Employee ($K)": REV_PER_EMPLOYEE_THRESHOLDS,
},
        "valuation_metric":     "EV/FCF",
        "valuation_thresholds": EV_FCF_THRESHOLDS,
    },

    "Equipment": {
"quality_weights": {
    # Technological-moat, cyclical-orders business — margin quality and R&D
    # matter far more than trailing growth, which is mostly cycle noise.
    # Most equipment names run net cash, so debt weight is minimal.
    "ROIC":             0.18,
    "Gross Margin":     0.14,
    "FCF Margin":       0.13,
    "R&D Intensity":    0.11,
    "Op Margin":        0.11,
    "GM Trend (3Y)":    0.07,
    "ROIC Trend (3Y)":  0.06,
    "Revenue per Employee ($K)": 0.05,
    "Rev CAGR (3Y)":    0.06,
    "Net Debt/EBITDA":  0.03,
    "FCF Margin Trend (3Y)": 0.06,
},
"quality_thresholds": {
    "ROIC":             ROIC_THRESHOLDS,
    "FCF Margin":       FCF_MARGIN_THRESHOLDS,
    "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
    "GM Trend (3Y)":    GM_TREND_THRESHOLDS,  # NEW
    "ROIC Trend (3Y)":  ROIC_TREND_THRESHOLDS,  # NEW
    "FCF Margin Trend (3Y)": FCF_MARGIN_TREND_THRESHOLDS,  # NEW
    "Op Margin":        OP_MARGIN_THRESHOLDS,
    "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,
    "Net Debt/EBITDA":  NET_DEBT_EBITDA_THRESHOLDS,
    "R&D Intensity":    SEMIS_RND_THRESHOLDS,
    "Revenue per Employee ($K)": REV_PER_EMPLOYEE_THRESHOLDS,
},
        "valuation_metric":     "EV/FCF",
        "valuation_thresholds": EV_FCF_THRESHOLDS,
    },

    "IDM": {
"quality_weights": {
    # Same capital intensity as Foundry, but the key quality tell is
    # leverage discipline (e.g. TXN vs. Intel) rather than pure scale ROIC.
    "ROIC":             0.19,
    "FCF Margin":       0.14,
    "Op Margin":        0.12,
    "Gross Margin":     0.11,
    "Net Debt/EBITDA":  0.07,
    "GM Trend (3Y)":    0.06,
    "ROIC Trend (3Y)":  0.07,
    "Rev CAGR (3Y)":    0.07,
    "R&D Intensity":    0.07,
    "Revenue per Employee ($K)": 0.04,
    "FCF Margin Trend (3Y)": 0.06,
},
"quality_thresholds": {
    "ROIC":             ROIC_THRESHOLDS,
    "FCF Margin":       FCF_MARGIN_THRESHOLDS,
    "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
    "GM Trend (3Y)":    GM_TREND_THRESHOLDS,  # NEW
    "ROIC Trend (3Y)":  ROIC_TREND_THRESHOLDS,  # NEW
    "FCF Margin Trend (3Y)": FCF_MARGIN_TREND_THRESHOLDS,  # NEW
    "Op Margin":        OP_MARGIN_THRESHOLDS,
    "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,
    "Net Debt/EBITDA":  NET_DEBT_EBITDA_THRESHOLDS,
    "R&D Intensity":    SEMIS_RND_THRESHOLDS,
    "Revenue per Employee ($K)": REV_PER_EMPLOYEE_THRESHOLDS,
},
        "valuation_metric":     "EV/FCF",
        "valuation_thresholds": EV_FCF_THRESHOLDS,
    },

    "Memory": {
"quality_weights": {
    # Commodity, brutally cyclical — trailing ROIC/margins are noisy and can
    # go negative at trough. Quality here means surviving the cycle: balance
    # sheet strength and GM trend (inflection signal) outweigh peak
    # profitability. Growth is exogenous/cycle-driven, so it's a weak signal.
    "FCF Margin":       0.18,
    "Net Debt/EBITDA":  0.14,
    "GM Trend (3Y)":    0.12,
    "ROIC":             0.12,
    "ROIC Trend (3Y)":  0.07,
    "Gross Margin":     0.10,
    "Op Margin":        0.09,
    "R&D Intensity":    0.05,
    "Rev CAGR (3Y)":    0.04,
    "Revenue per Employee ($K)": 0.03,
    "FCF Margin Trend (3Y)": 0.06,
},
"quality_thresholds": {
    "ROIC":             ROIC_THRESHOLDS,
    "FCF Margin":       FCF_MARGIN_THRESHOLDS,
    "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
    "GM Trend (3Y)":    GM_TREND_THRESHOLDS,  # NEW
    "ROIC Trend (3Y)":  ROIC_TREND_THRESHOLDS,  # NEW
    "FCF Margin Trend (3Y)": FCF_MARGIN_TREND_THRESHOLDS,  # NEW
    "Op Margin":        OP_MARGIN_THRESHOLDS,
    "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,
    "Net Debt/EBITDA":  NET_DEBT_EBITDA_THRESHOLDS,
    "R&D Intensity":    SEMIS_RND_THRESHOLDS,
    "Revenue per Employee ($K)": REV_PER_EMPLOYEE_THRESHOLDS,
},
        "valuation_metric":     "EV/FCF",
        "valuation_thresholds": EV_FCF_THRESHOLDS,
    },

    "EDA_IP": {
"quality_weights": {
    # Best-in-class asset-light IP moat, near-duopoly — R&D and
    # per-employee leverage are the whole thesis; growth from design-cycle
    # attach is a real signal; balance sheet risk is essentially irrelevant.
    "ROIC":             0.17,
    "FCF Margin":       0.14,
    "R&D Intensity":    0.10,
    "Revenue per Employee ($K)": 0.10,
    "Op Margin":        0.10,
    "Rev CAGR (3Y)":    0.09,
    "Gross Margin":     0.09,
    "GM Trend (3Y)":    0.06,
    "ROIC Trend (3Y)":  0.07,
    "Net Debt/EBITDA":  0.02,
    "FCF Margin Trend (3Y)": 0.06,
},
"quality_thresholds": {
    "ROIC":             ROIC_THRESHOLDS,
    "FCF Margin":       FCF_MARGIN_THRESHOLDS,
    "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
    "GM Trend (3Y)":    GM_TREND_THRESHOLDS,  # NEW
    "ROIC Trend (3Y)":  ROIC_TREND_THRESHOLDS,  # NEW
    "FCF Margin Trend (3Y)": FCF_MARGIN_TREND_THRESHOLDS,  # NEW
    "Op Margin":        OP_MARGIN_THRESHOLDS,
    "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,
    "Net Debt/EBITDA":  NET_DEBT_EBITDA_THRESHOLDS,
    "R&D Intensity":    SEMIS_RND_THRESHOLDS,
    "Revenue per Employee ($K)": REV_PER_EMPLOYEE_THRESHOLDS,
},
        "valuation_metric":     "EV/FCF",
        "valuation_thresholds": EV_FCF_THRESHOLDS,
    },

    "SUPPLY_CHAIN": {
"quality_weights": {
    # Distributor, not an IP-driven tech co (AVT, ARW) — Revenue per Employee
    # and R&D Intensity excluded since headcount leverage and R&D spend aren't
    # quality signals for a distribution business.
    "ROIC":             0.22,
    "FCF Margin":       0.18,
    "Gross Margin":     0.13,
    "Op Margin":        0.13,
    "GM Trend (3Y)":    0.08,
    "ROIC Trend (3Y)":  0.07,
    "Rev CAGR (3Y)":    0.08,
    "Net Debt/EBITDA":  0.05,
    "FCF Margin Trend (3Y)": 0.06,
},
"quality_thresholds": {
    "ROIC":             ROIC_THRESHOLDS,
    "FCF Margin":       FCF_MARGIN_THRESHOLDS,
    "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
    "GM Trend (3Y)":    GM_TREND_THRESHOLDS,  # NEW
    "ROIC Trend (3Y)":  ROIC_TREND_THRESHOLDS,  # NEW
    "FCF Margin Trend (3Y)": FCF_MARGIN_TREND_THRESHOLDS,  # NEW
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
    # Mega-cap, capital-intensive cloud infra — FCF margin and operating
    # leverage are the clearest proof of quality at scale; growth and
    # balance-sheet discipline matter given the size of AI capex.
    "FCF Margin":       0.26,
    "Op Margin":        0.20,
    "Gross Margin":     0.14,
    "GM Trend (3Y)":    0.09,
    "Rev CAGR (3Y)":    0.15,
    "Net Debt/EBITDA":  0.10,
    "FCF Margin Trend (3Y)": 0.06,
},
        "quality_thresholds": {
            "FCF Margin":       FCF_MARGIN_THRESHOLDS,
            "Op Margin":        OP_MARGIN_THRESHOLDS,
            "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
            "GM Trend (3Y)":    GM_TREND_THRESHOLDS,
            "FCF Margin Trend (3Y)": FCF_MARGIN_TREND_THRESHOLDS,  # NEW
            "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,
            "Net Debt/EBITDA":  NET_DEBT_EBITDA_THRESHOLDS,
        },
        "valuation_metric":     "EV/Revenue",
        "valuation_thresholds": HYPERSCALER_EV_REVENUE_THRESHOLDS,
    },

    "Cloud_Data": {
"quality_weights": {
    "Rule of 40":       0.24,
    "FCF Margin":       0.19,
    "Gross Margin":     0.14,
    "GM Trend (3Y)":    0.09,
    "Op Margin":        0.14,
    "Rev CAGR (3Y)":    0.09,
    "Net Debt/EBITDA":  0.05,
    "FCF Margin Trend (3Y)": 0.06,
},
        "quality_thresholds": {
            "Rule of 40":       RULE_OF_40_THRESHOLDS,
            "FCF Margin":       FCF_MARGIN_THRESHOLDS,
            "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
            "Op Margin":        OP_MARGIN_THRESHOLDS,
            "GM Trend (3Y)":    GM_TREND_THRESHOLDS,
            "FCF Margin Trend (3Y)": FCF_MARGIN_TREND_THRESHOLDS,  # NEW
            "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,
            "Net Debt/EBITDA":  NET_DEBT_EBITDA_THRESHOLDS,
        },
        "valuation_metric":     "EV/Revenue",
        "valuation_thresholds": SAAS_EV_REVENUE_THRESHOLDS,
    },

    "Network_Hardware": {
        "quality_weights": {
            "Rule of 40":       0.25,  # growth/profit blend
            "Op Margin":        0.20,  # software-like margins on hardware
            "FCF Margin":       0.20,  # cash generation
            "Rev CAGR (3Y)":    0.15,  # AI-driven demand trajectory
            "GM Trend (3Y)":    0.10,  # margin expansion = moat strengthening
            "Gross Margin":     0.10,  # lower baseline than SaaS, weighted accordingly
        },
        "quality_thresholds": {
            "Rule of 40":       RULE_OF_40_THRESHOLDS,
            "Op Margin":        OP_MARGIN_THRESHOLDS,
            "FCF Margin":       FCF_MARGIN_THRESHOLDS,
            "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,
            "GM Trend (3Y)":    GM_TREND_THRESHOLDS,
            "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
        },
        "valuation_metric":     "EV/Revenue",
        "valuation_thresholds": SAAS_EV_REVENUE_THRESHOLDS,
    },

    # --- SaaS ---
"Enterprise_SaaS": {
    "quality_weights": {
        "FCF Margin":       0.22,
        "Rule of 40":       0.17,
        "Gross Margin":     0.13,
        "Op Margin":        0.13,
        "GM Trend (3Y)":    0.08,
        "Rev CAGR (3Y)":    0.08,
        "Net Debt/EBITDA":  0.05,
        "Revenue per Employee ($K)": 0.08,
        "FCF Margin Trend (3Y)": 0.06,
    },
    "quality_thresholds": {
        "FCF Margin":       FCF_MARGIN_THRESHOLDS,
        "Rule of 40":       RULE_OF_40_THRESHOLDS,
        "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
        "Op Margin":        OP_MARGIN_THRESHOLDS,
        "GM Trend (3Y)":    GM_TREND_THRESHOLDS,
        "FCF Margin Trend (3Y)": FCF_MARGIN_TREND_THRESHOLDS,  # NEW
        "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,
        "Net Debt/EBITDA":  NET_DEBT_EBITDA_THRESHOLDS,
        "Revenue per Employee ($K)": REV_PER_EMPLOYEE_THRESHOLDS,
    },
    "valuation_metric":     "EV/Revenue",
    "valuation_thresholds": ENTERPRISE_SAAS_EV_REVENUE_THRESHOLDS,
},
"Enterprise_AI": {
    "quality_weights": {
        "Gross Margin":     0.20,
        "Rule of 40":       0.20,
        "Rev CAGR (3Y)":    0.16,
        "FCF Margin":       0.12,
        "GM Trend (3Y)":    0.07,
        "Op Margin":        0.05,
        "R&D Intensity":    0.07,
        "Revenue per Employee ($K)": 0.07,
        "FCF Margin Trend (3Y)": 0.06,
    },
    "quality_thresholds": {
        "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
        "Rule of 40":       RULE_OF_40_THRESHOLDS,
        "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,
        "FCF Margin":       FCF_MARGIN_THRESHOLDS,
        "GM Trend (3Y)":    GM_TREND_THRESHOLDS,
        "FCF Margin Trend (3Y)": FCF_MARGIN_TREND_THRESHOLDS,  # NEW
        "Op Margin":        OP_MARGIN_THRESHOLDS,
        "R&D Intensity":    SOFTWARE_RND_THRESHOLDS,
        "Revenue per Employee ($K)": REV_PER_EMPLOYEE_THRESHOLDS,
    },
    "valuation_metric":     "EV/Revenue",
    "valuation_thresholds": SAAS_EV_REVENUE_THRESHOLDS,
},
"Vertical_SaaS": {
    "quality_weights": {
        "Gross Margin":     0.24,  # vertical moat signal
        "FCF Margin":       0.23,  # cash generation validates moat
        "Op Margin":        0.19,  # operational efficiency
        "GM Trend (3Y)":    0.14,  # moat durability over time
        "Rule of 40":       0.09,  # growth/profitability balance
        "Rev CAGR (3Y)":    0.05,  # durability > growth for verticals
        "FCF Margin Trend (3Y)": 0.06,
    },
    "quality_thresholds": {
        "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
        "FCF Margin":       FCF_MARGIN_THRESHOLDS,
        "Op Margin":        OP_MARGIN_THRESHOLDS,
        "GM Trend (3Y)":    GM_TREND_THRESHOLDS,
        "FCF Margin Trend (3Y)": FCF_MARGIN_TREND_THRESHOLDS,  # NEW
        "Rule of 40":       RULE_OF_40_THRESHOLDS,
        "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,
    },
    "valuation_metric":     "EV/Revenue",
    "valuation_thresholds": SAAS_EV_REVENUE_THRESHOLDS,
},
"Data_Analytics": {
    "quality_weights": {
        # Asset-light data/index/analytics subscriptions (e.g. MSCI) — elite,
        # durable margins and moat trend matter more than growth rate; some
        # leverage tolerance since these businesses fund buybacks with debt.
        "Gross Margin":     0.22,
        "FCF Margin":       0.22,
        "Op Margin":        0.18,
        "GM Trend (3Y)":    0.12,
        "Net Debt/EBITDA":  0.10,
        "Rev CAGR (3Y)":    0.10,
        "FCF Margin Trend (3Y)": 0.06,
    },
    "quality_thresholds": {
        "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
        "FCF Margin":       FCF_MARGIN_THRESHOLDS,
        "Op Margin":        OP_MARGIN_THRESHOLDS,
        "GM Trend (3Y)":    GM_TREND_THRESHOLDS,
        "Net Debt/EBITDA":  NET_DEBT_EBITDA_THRESHOLDS,
        "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,
        "FCF Margin Trend (3Y)": FCF_MARGIN_TREND_THRESHOLDS,
    },
    "valuation_metric":     "EV/Revenue",
    "valuation_thresholds": SAAS_EV_REVENUE_THRESHOLDS,
},
"IT_Services": {
    "quality_weights": {
        "Revenue per Employee ($K)": 0.30,  # primary signal — staffing efficiency
        "FCF Margin":                0.20,
        "Op Margin":                 0.20,
        "Rev CAGR (3Y)":             0.15,
        "Gross Margin":              0.10,
        "Net Debt/EBITDA":           0.05,
    },
    "quality_thresholds": {
        "Revenue per Employee ($K)": IT_SERVICES_REV_PER_EMPLOYEE_THRESHOLDS,
        "FCF Margin":                FCF_MARGIN_THRESHOLDS,
        "Op Margin":                 OP_MARGIN_THRESHOLDS,
        "Rev CAGR (3Y)":             REV_GROWTH_THRESHOLDS,
        "Gross Margin":              GROSS_MARGIN_THRESHOLDS,
        "Net Debt/EBITDA":           NET_DEBT_EBITDA_THRESHOLDS,
    },
    "valuation_metric":     "EV/Revenue",
    "valuation_thresholds": ENTERPRISE_SAAS_EV_REVENUE_THRESHOLDS,
},
"Ad_Platform": {
    "quality_weights": {
        "Gross Margin":              0.25,  # platform take rate — APP 88.5% vs TTD 76.9%
        "Rule of 40":                0.25,  # growth/profit blend
        "FCF Margin":                0.20,  # cash generation
        "Rev CAGR (3Y)":             0.15,  # platform adoption
        "Revenue per Employee ($K)": 0.10,  # platform efficiency
        "GM Trend (3Y)":             0.05,  # moat durability
    },
    "quality_thresholds": {
        "Gross Margin":              GROSS_MARGIN_THRESHOLDS,
        "Rule of 40":                RULE_OF_40_THRESHOLDS,
        "FCF Margin":                FCF_MARGIN_THRESHOLDS,
        "Rev CAGR (3Y)":             REV_GROWTH_THRESHOLDS,
        "Revenue per Employee ($K)": REV_PER_EMPLOYEE_THRESHOLDS,
        "GM Trend (3Y)":             GM_TREND_THRESHOLDS,
    },
    "valuation_metric":     "EV/Revenue",
    "valuation_thresholds": SAAS_EV_REVENUE_THRESHOLDS,
},
"Payment_Network": {
    "quality_weights": {
        "Op Margin":        0.30,  # network moat visible here
        "FCF Margin":       0.25,  # cash conversion
        "Gross Margin":     0.15,  # near-perfect for both, low differentiation
        "Rule of 40":       0.15,  # growth/profit balance
        "Rev CAGR (3Y)":    0.10,  # steady growth
        "GM Trend (3Y)":    0.05,  # stable, low differentiation
    },
    "quality_thresholds": {
        "Op Margin":        OP_MARGIN_THRESHOLDS,
        "FCF Margin":       FCF_MARGIN_THRESHOLDS,
        "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
        "Rule of 40":       RULE_OF_40_THRESHOLDS,
        "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,
        "GM Trend (3Y)":    GM_TREND_THRESHOLDS,
    },
    "valuation_metric":     "EV/FCF",
    "valuation_thresholds": EV_FCF_THRESHOLDS,
},
"DevOps": {
    "quality_weights": {
        "Rule of 40":       0.26,  # primary quality signal
        "Rev CAGR (3Y)":    0.17,  # growth trajectory matters most
        "Gross Margin":     0.17,  # platform moat signal
        "FCF Margin":       0.13,  # real cash generation
        "GM Trend (3Y)":    0.08,  # moat durability
        "Op Margin":        0.05,  # low weight — GAAP artifact
        "R&D Intensity":    0.08,
        "FCF Margin Trend (3Y)": 0.06,
    },
    "quality_thresholds": {
        "Rule of 40":       RULE_OF_40_THRESHOLDS,
        "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,
        "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
        "FCF Margin":       FCF_MARGIN_THRESHOLDS,
        "GM Trend (3Y)":    GM_TREND_THRESHOLDS,
        "FCF Margin Trend (3Y)": FCF_MARGIN_TREND_THRESHOLDS,  # NEW
        "Op Margin":        OP_MARGIN_THRESHOLDS,
        "R&D Intensity":    SOFTWARE_RND_THRESHOLDS,
    },
    "valuation_metric":     "EV/Revenue",
    "valuation_thresholds": DEVOPS_EV_REVENUE_THRESHOLDS,
},


    "Collaboration": {
"quality_weights": {
"FCF Margin":       0.22,  # cash generation is the only thesis
"Op Margin":        0.22,
"Gross Margin":     0.18,
"GM Trend (3Y)":    0.08,
"Rule of 40":       0.08,  # less relevant for slow growers
"Rev CAGR (3Y)":    0.08,  # growth is minimal, weight it low
"Revenue per Employee ($K)": 0.08,
"FCF Margin Trend (3Y)": 0.06,
},
        "quality_thresholds": {
            "Rule of 40":       RULE_OF_40_THRESHOLDS,
            "FCF Margin":       FCF_MARGIN_THRESHOLDS,
            "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
            "Op Margin":        OP_MARGIN_THRESHOLDS,
            "GM Trend (3Y)":    GM_TREND_THRESHOLDS,
            "FCF Margin Trend (3Y)": FCF_MARGIN_TREND_THRESHOLDS,  # NEW
            "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,
            "Revenue per Employee ($K)": REV_PER_EMPLOYEE_THRESHOLDS,

        },
        "valuation_metric":     "EV/Revenue",
        "valuation_thresholds": COLLABORATION_EV_REVENUE_THRESHOLDS
    },

    # --- Cybersecurity ---
    "ENDPOINT": {
"quality_weights": {
    "Rule of 40":       0.26,  # early-stage platform — growth+profit blend is the thesis
    "Rev CAGR (3Y)":    0.22,  # high growth is the core signal at this stage
    "Gross Margin":     0.13,  # platform moat
    "FCF Margin":       0.13,  # real cash generation despite GAAP losses
    "GM Trend (3Y)":    0.08,  # moat durability
    "Op Margin":        0.05,  # low weight — negative GAAP margins are accounting artifacts
    "Revenue per Employee ($K)": 0.07,
    "FCF Margin Trend (3Y)": 0.06,
},
        "quality_thresholds": {
            "Rule of 40":       RULE_OF_40_THRESHOLDS,
            "FCF Margin":       FCF_MARGIN_THRESHOLDS,
            "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
            "Op Margin":        OP_MARGIN_THRESHOLDS,
            "GM Trend (3Y)":    GM_TREND_THRESHOLDS,
            "FCF Margin Trend (3Y)": FCF_MARGIN_TREND_THRESHOLDS,  # NEW
            "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,
            "Revenue per Employee ($K)": REV_PER_EMPLOYEE_THRESHOLDS,
        },
        "valuation_metric":     "EV/Revenue",
        "valuation_thresholds": SAAS_EV_REVENUE_THRESHOLDS,
    },

    "NETWORK": {
"quality_weights": {
    "FCF Margin":       0.22,  # mature platform — real cash generation matters most
    "Op Margin":        0.22,  # real GAAP profitability, not an artifact at this stage
    "Gross Margin":     0.13,
    "GM Trend (3Y)":    0.08,
    "Rule of 40":       0.08,  # secondary to raw profitability here
    "Rev CAGR (3Y)":    0.09,  # growth weighted below profitability
    "Net Debt/EBITDA":  0.05,
    "Revenue per Employee ($K)": 0.07,
    "FCF Margin Trend (3Y)": 0.06,
},
        "quality_thresholds": {
            "Rule of 40":       RULE_OF_40_THRESHOLDS,
            "FCF Margin":       FCF_MARGIN_THRESHOLDS,
            "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
            "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,
            "Op Margin":        OP_MARGIN_THRESHOLDS,
            "GM Trend (3Y)":    GM_TREND_THRESHOLDS,
            "FCF Margin Trend (3Y)": FCF_MARGIN_TREND_THRESHOLDS,  # NEW
            "Net Debt/EBITDA":  NET_DEBT_EBITDA_THRESHOLDS,
            "Revenue per Employee ($K)": REV_PER_EMPLOYEE_THRESHOLDS,
        },
        "valuation_metric":     "EV/Revenue",
        "valuation_thresholds": SAAS_EV_REVENUE_THRESHOLDS,
    },

    "IDENTITY": {
"quality_weights": {
    "Gross Margin":     0.17,  # switching-cost moat signal
    "Rule of 40":       0.18,  # balanced growth/profit blend
    "FCF Margin":       0.18,  # balanced growth/profit blend
    "Op Margin":        0.13,
    "Rev CAGR (3Y)":    0.13,
    "GM Trend (3Y)":    0.08,
    "Revenue per Employee ($K)": 0.07,
    "FCF Margin Trend (3Y)": 0.06,
},
        "quality_thresholds": {
            "Rule of 40":       RULE_OF_40_THRESHOLDS,
            "FCF Margin":       FCF_MARGIN_THRESHOLDS,
            "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
            "Op Margin":        OP_MARGIN_THRESHOLDS,
            "GM Trend (3Y)":    GM_TREND_THRESHOLDS,
            "FCF Margin Trend (3Y)": FCF_MARGIN_TREND_THRESHOLDS,  # NEW
            "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,
            "Revenue per Employee ($K)": REV_PER_EMPLOYEE_THRESHOLDS,
        },
        "valuation_metric":     "EV/Revenue",
        "valuation_thresholds": SAAS_EV_REVENUE_THRESHOLDS,
    },

    "CLOUD_SEC": {
"quality_weights": {
    "Rule of 40":       0.24,
    "FCF Margin":       0.19,
    "Gross Margin":     0.14,
    "GM Trend (3Y)":    0.09,
    "Op Margin":        0.14,
    "Rev CAGR (3Y)":    0.09,
    "Net Debt/EBITDA":  0.05,
    "FCF Margin Trend (3Y)": 0.06,
},
        "quality_thresholds": {
            "Rule of 40":       RULE_OF_40_THRESHOLDS,
            "FCF Margin":       FCF_MARGIN_THRESHOLDS,
            "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
            "Op Margin":        OP_MARGIN_THRESHOLDS,
            "GM Trend (3Y)":    GM_TREND_THRESHOLDS,
            "FCF Margin Trend (3Y)": FCF_MARGIN_TREND_THRESHOLDS,  # NEW
            "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,
            "Net Debt/EBITDA":  NET_DEBT_EBITDA_THRESHOLDS,
        },
        "valuation_metric":     "EV/Revenue",
        "valuation_thresholds": SAAS_EV_REVENUE_THRESHOLDS,
    },

    "DATA_SEC": {
"quality_weights": {
    "FCF Margin":       0.22,  # mature tooling — profitability matters most
    "Op Margin":        0.18,
    "Gross Margin":     0.18,
    "GM Trend (3Y)":    0.08,
    "Net Debt/EBITDA":  0.08,
    "Rule of 40":       0.08,
    "Rev CAGR (3Y)":    0.05,  # growth least important at this stage
    "Revenue per Employee ($K)": 0.07,
    "FCF Margin Trend (3Y)": 0.06,
},
        "quality_thresholds": {
            "Rule of 40":       RULE_OF_40_THRESHOLDS,
            "FCF Margin":       FCF_MARGIN_THRESHOLDS,
            "Gross Margin":     GROSS_MARGIN_THRESHOLDS,
            "Op Margin":        OP_MARGIN_THRESHOLDS,
            "GM Trend (3Y)":    GM_TREND_THRESHOLDS,
            "FCF Margin Trend (3Y)": FCF_MARGIN_TREND_THRESHOLDS,  # NEW
            "Rev CAGR (3Y)":    REV_GROWTH_THRESHOLDS,
            "Net Debt/EBITDA":  NET_DEBT_EBITDA_THRESHOLDS,
            "Revenue per Employee ($K)": REV_PER_EMPLOYEE_THRESHOLDS,
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

    # Fallback to EV/Revenue if the primary metric is undefined (e.g. EV/FCF
    # with negative or zero FCF). Only triggers for EV/FCF-primary archetypes
    # (semis) since every other archetype already uses EV/Revenue directly.
    if val_score is None and val_metric != "EV/Revenue":
        val_score = score_metric(row.get("EV/Revenue"), SEMIS_EV_REVENUE_THRESHOLDS)

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