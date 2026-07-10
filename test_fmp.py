# test_fmp.py
from data_fetcher import get_metrics

result = get_metrics("NVDA", "Fabless")
for k, v in result.items():
    print(f"{k}: {v}")