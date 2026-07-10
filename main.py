import pandas as pd
from verticals import semis, cloud, saas, cyber
from scoring import score_dataframe

FETCH = {
    "semis": True,
    "cloud": False,
    "saas":  False,
    "cyber": False,
}

SCORE = {
    "semis": True,
    "cloud": False,
    "saas":  False,
    "cyber": False,
}

if FETCH["semis"]: semis.run()
if FETCH["cloud"]: cloud.run()
if FETCH["saas"]:  saas.run()
if FETCH["cyber"]: cyber.run()

if SCORE["semis"]:
    df_semis = pd.read_csv("data/semis.csv")
    df_semis = score_dataframe(df_semis)
    df_semis.to_csv("data/semis_scored.csv", index=False)
    print("\nSemis scoring complete.")
    print(df_semis[["Ticker", "Archetype", "Quality Score", "Valuation Score", "Verdict"]].to_string(index=False))

if SCORE["cloud"]:
    df_cloud = pd.read_csv("data/cloud.csv")
    df_cloud = score_dataframe(df_cloud)
    df_cloud.to_csv("data/cloud_scored.csv", index=False)
    print("\nCloud scoring complete.")
    print(df_cloud[["Ticker", "Archetype", "Quality Score", "Valuation Score", "Verdict"]].to_string(index=False))

if SCORE["saas"]:
    df_saas = pd.read_csv("data/saas.csv")
    df_saas = score_dataframe(df_saas)
    df_saas.to_csv("data/saas_scored.csv", index=False)
    print("\nSaaS scoring complete.")
    print(df_saas[["Ticker", "Archetype", "Quality Score", "Valuation Score", "Verdict"]].to_string(index=False))

if SCORE["cyber"]:
    df_cyber = pd.read_csv("data/cyber.csv")
    df_cyber = score_dataframe(df_cyber)
    df_cyber.to_csv("data/cyber_scored.csv", index=False)
    print("\nCyber scoring complete.")
    print(df_cyber[["Ticker", "Archetype", "Quality Score", "Valuation Score", "Verdict"]].to_string(index=False))