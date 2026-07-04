import pandas as pd
from verticals import semis, cloud, saas, cyber
from scoring import score_dataframe, score_saas_dataframe

# semis.run()
# cloud.run()
saas.run()
cyber.run()

# Semis scoring
df_semis = pd.read_csv("data/semis.csv")
df_semis = score_dataframe(df_semis)
df_semis.to_csv("data/semis_scored.csv", index=False)
print("\nSemis scoring complete.")
print(df_semis[["Ticker", "Archetype", "Quality Score", "Valuation Score", "Verdict"]].to_string(index=False))

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