import pandas as pd
from verticals import semis, cloud, saas, cyber
from scoring import score_dataframe
from analyst import analyze_dataframe

FETCH  = {"semis": True, "cloud": True, "saas": True, "cyber": True}
SCORE  = {"semis": True,  "cloud": True,  "saas": True,  "cyber": True}
ANALYZE = {"semis": False,  "cloud": False,  "saas": False,  "cyber": False}

if FETCH["semis"]: semis.run()
if FETCH["cloud"]: cloud.run()
if FETCH["saas"]:  saas.run()
if FETCH["cyber"]: cyber.run()

if SCORE["semis"]:
    df_semis = pd.read_csv("data/semis.csv")
    df_semis = score_dataframe(df_semis)
    if ANALYZE["semis"]:
        df_semis["Vertical"] = "Semiconductors"
        df_semis = analyze_dataframe(df_semis, vertical="Semiconductors")
    df_semis.to_csv("data/semis_scored.csv", index=False)
    print("\nSemis scoring complete.")
    print(df_semis[["Ticker", "Archetype", "Quality Score", "Valuation Score", "Verdict"]].to_string(index=False))

if SCORE["cloud"]:
    df_cloud = pd.read_csv("data/cloud.csv")
    df_cloud = score_dataframe(df_cloud)
    if ANALYZE["cloud"]:
        df_cloud["Vertical"] = "Cloud"
        df_cloud = analyze_dataframe(df_cloud, vertical="Cloud")
    df_cloud.to_csv("data/cloud_scored.csv", index=False)
    print("\nCloud scoring complete.")
    print(df_cloud[["Ticker", "Archetype", "Quality Score", "Valuation Score", "Verdict"]].to_string(index=False))

if SCORE["saas"]:
    df_saas = pd.read_csv("data/saas.csv")
    df_saas = score_dataframe(df_saas)
    if ANALYZE["saas"]:
        df_saas["Vertical"] = "SaaS"
        df_saas = analyze_dataframe(df_saas, vertical="SaaS")
    df_saas.to_csv("data/saas_scored.csv", index=False)
    print("\nSaaS scoring complete.")
    print(df_saas[["Ticker", "Archetype", "Quality Score", "Valuation Score", "Verdict"]].to_string(index=False))

if SCORE["cyber"]:
    df_cyber = pd.read_csv("data/cyber.csv")
    df_cyber = score_dataframe(df_cyber)
    if ANALYZE["cyber"]:
        df_cyber["Vertical"] = "Cybersecurity"
        df_cyber = analyze_dataframe(df_cyber, vertical="Cybersecurity")
    df_cyber.to_csv("data/cyber_scored.csv", index=False)
    print("\nCyber scoring complete.")
    print(df_cyber[["Ticker", "Archetype", "Quality Score", "Valuation Score", "Verdict"]].to_string(index=False))