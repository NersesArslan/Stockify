import pandas as pd
from verticals import semis, cloud, saas, cyber
from scoring import score_dataframe, score_saas_dataframe, score_cloud_dataframe

# --- Control flags ---
FETCH = {
    "semis": False,
    "cloud": True,
    "saas":  False,
    "cyber": False,
}

# --- Fetch ---
if FETCH["semis"]: semis.run()
if FETCH["cloud"]: cloud.run()
if FETCH["saas"]:  saas.run()
if FETCH["cyber"]: cyber.run()


# Semis scoring
df_semis = pd.read_csv("data/semis.csv")
df_semis = score_dataframe(df_semis)
df_semis.to_csv("data/semis_scored.csv", index=False)
print("\nSemis scoring complete.")
print(df_semis[["Ticker", "Archetype", "Quality Score", "Valuation Score", "Verdict"]].to_string(index=False))

# Cloud scoring
df_cloud = pd.read_csv("data/cloud.csv")
df_cloud = score_cloud_dataframe(df_cloud)
df_cloud.to_csv("data/cloud_scored.csv", index=False)
print("\nCloud scoring complete.")
print(df_cloud[["Ticker", "Archetype", "Quality Score", "Valuation Score", "Verdict"]].to_string(index=False))

# SaaS scoring
df_saas = pd.read_csv("data/saas.csv")
df_saas = score_saas_dataframe(df_saas)
df_saas.to_csv("data/saas_scored.csv", index=False)
print("\nSaaS scoring complete.")
print(df_saas[["Ticker", "Archetype", "Quality Score", "Valuation Score", "Verdict"]].to_string(index=False))

# Cyber scoring
df_cyber = pd.read_csv("data/cyber.csv")
df_cyber = score_saas_dataframe(df_cyber)
df_cyber.to_csv("data/cyber_scored.csv", index=False)
print("\nCyber scoring complete.")
print(df_cyber[["Ticker", "Archetype", "Quality Score", "Valuation Score", "Verdict"]].to_string(index=False))