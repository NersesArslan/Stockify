# analyst.py
import anthropic
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are an investment analyst assistant helping evaluate stocks based on a specific investment philosophy.

The philosophy is:
- Quality-first, valuation second
- Focus on structurally necessary companies in the AI infrastructure buildout
- Industry-relative benchmarking — metrics are only meaningful within archetypes
- Avoid narrative-dependent companies where valuation relies on charismatic CEOs or hype
- Prefer companies with strong moats: pricing power, switching costs, structural necessity

Scoring system:
- Quality Score (0-100): measures business quality — profitability, cash generation, growth, balance sheet
- Valuation Score (0-100): measures cheapness — higher score means cheaper
- Verdicts: Buy (high quality + cheap), Watch (high quality + expensive), Avoid (low quality + cheap), Pass (low quality + expensive)

When analyzing a company, be concise and direct. Focus on:
1. What the metrics tell you about business quality
2. Whether the valuation is justified
3. Any notable risks or red flags
4. A clear one-sentence investment takeaway

Keep each analysis to 3-4 sentences maximum. Be specific about the numbers. Do not use generic financial advice disclaimers."""


def build_prompt(row):
    """Build a prompt for a single company row."""
    return f"""Analyze this company based on the metrics and scores below:

Company: {row.get('Name', row.get('Ticker'))} ({row.get('Ticker')})
Vertical: {row.get('Vertical', 'Unknown')}
Archetype: {row.get('Archetype')}
Verdict: {row.get('Verdict')}
Quality Score: {row.get('Quality Score')}
Valuation Score: {row.get('Valuation Score')}

Key Metrics:
- EV/FCF: {row.get('EV/FCF')}
- EV/Revenue: {row.get('EV/Revenue')}
- FCF Margin: {row.get('FCF Margin')}%
- Op Margin: {row.get('Op Margin')}%
- Gross Margin: {row.get('Gross Margin')}%
- Rev Growth (YoY): {row.get('Rev Growth (YoY)')}%
- ROIC: {row.get('ROIC')}%
- Rule of 40: {row.get('Rule of 40')}
- Net Debt/EBITDA: {row.get('Net Debt/EBITDA')}

Provide a 3-4 sentence analysis and a one-sentence investment takeaway."""


def analyze_row(row):
    """Send a single row to Claude for analysis."""
    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": build_prompt(row)}
            ]
        )
        return message.content[0].text.strip()
    except Exception as e:
        return f"Analysis error: {str(e)}"


def analyze_dataframe(df, vertical="", verdicts_to_analyze=None):
    """
    Analyze companies in a dataframe.
    Only analyzes Buy and Watch by default to save API calls.
    """
    if verdicts_to_analyze is None:
        verdicts_to_analyze = ["Buy", "Watch"]

    df = df.copy()
    df["AI Analysis"] = None

    mask = df["Verdict"].isin(verdicts_to_analyze)
    candidates = df[mask]

    print(f"\nAnalyzing {len(candidates)} {vertical} companies ({', '.join(verdicts_to_analyze)})...")

    for idx, row in candidates.iterrows():
        ticker = row.get("Ticker")
        print(f"  Analyzing {ticker}...")
        df.at[idx, "AI Analysis"] = analyze_row(row)

    return df