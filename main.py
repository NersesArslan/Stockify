import pandas as pd
from verticals import semis, cloud, saas, cyber
from scoring import score_dataframe

semis.run()
# cloud.run()
# saas.run()
# cyber.run()

# Apply scoring to semis
df = pd.read_csv("data/semis.csv")
df = score_dataframe(df)
df.to_csv("data/semis_scored.csv", index=False)
print("\nScoring complete. Saved to data/semis_scored.csv")

# Preview results
print(df[["Ticker", "Archetype", "Quality Score", "Valuation Score", "Verdict"]].to_string(index=False))