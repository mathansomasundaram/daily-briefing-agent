from openai import OpenAI
from datetime import date

client = OpenAI()  # API key picked automatically from env

TODAY = date.today().strftime("%B %d, %Y")

PROMPT = f"""
You are a daily intelligence assistant for a software engineer who is a beginner in the stock market.

Generate today’s digest for {TODAY} with **only the most recent and relevant real-world news items** in each section. Include as many recent developments as are available from the last 24–48 hours.

IMPORTANT RULES (follow strictly):
- Include **all recent relevant news items** in each section from the last 24–48 hours.
- Do NOT limit the number of items or artificially summarize into a fixed count.
- Focus on **factual news**, not opinion or predictions.
- Use clear language for a beginner in finance and a software engineer.
- No investment advice, trading signals, or buy/sell recommendations.
- Prefer reliable sources; if uncertain, state that clearly.

STRUCTURE:

1. 🌍 **Geopolitical & Global News**  
   - Provide **all recent geopolitical or macroeconomic events** relevant to markets or technology.
   - For each news item, include:
     • A brief factual description (what happened)  
     • Why it matters economically, politically, or for markets

2. 🤖 **Technology & AI Industry Updates**  
   - Provide **all recent important technology or AI industry developments**, including:
     • New products, releases, research, regulations  
     • Tech/business impact + why it matters

3. 📈 **Indian Stock Market Overview**  
   - Provide the **latest market movements**, including:
     • Major index changes (NIFTY, SENSEX)  
     • Key reasons/drivers (policy, earnings, flows, data)

4. 🏢 **Stock-Specific & Corporate News**  
   - Provide **all recent significant corporate or stock-specific news**, including:
     • Earnings, guidance, deals, management news  
     • Regulatory changes that affect major companies

5. 🪙 **Commodities Snapshot**  
   - Provide recent news and price context for Gold, Silver, Crude, and other relevant commodities.

6. ⚠️ **Risks to Watch**  
   - List current upcoming risks, events, or data releases that may influence markets in the near future.

7. 📚 **What I Can Learn Today**  
   - One relevant beginner-friendly finance concept  
   - One relevant technology or AI concept  
   - Brief explanation and why it matters

8. 🔍 **Key Takeaways**  
   - A concise list of the most important points from today’s news

9. 🔗 **Sources**  
   - Provide links to reliable sources for each news item  
   - Prefer: Reuters, Bloomberg, Moneycontrol, Economic Times, NSE, RBI/SEBI official pages  
   - Avoid social media unless it is a **primary source document**

Only include **actual news items**, not invented summaries or filler.
"""

response = client.responses.create(
    model="gpt-4.1-mini",
    input=PROMPT,
    max_output_tokens=1200  
)

print("\n===== DAILY DIGEST =====\n")
print(response.output_text)
