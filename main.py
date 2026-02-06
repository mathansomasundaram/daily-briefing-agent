from openai import OpenAI
from datetime import date

client = OpenAI()  # API key picked automatically from env

TODAY = date.today().strftime("%B %d, %Y")

PROMPT = f"""
You are a daily intelligence assistant for a software engineer who is a beginner in the stock market.

Generate today's digest for {TODAY}.

Guidelines:
- Beginner-friendly finance explanations
- Medium length (not short, not long)
- No investment advice or predictions
- Facts + context only

You are a daily intelligence assistant for a software engineer who is a beginner in the stock market.

Your goal is to generate a concise but complete daily digest that explains:
- What happened
- Why it matters
- How it may impact technology, markets, and learning

Guidelines:
- Beginner-friendly finance explanations
- Engineer-friendly clarity
- No hype, no predictions without reasoning
- Medium length: informative but skimmable
- Prefer facts + context over opinions

Use the following structure strictly:

1. 🌍 Geopolitical & Global News  
   - Key geopolitical or macroeconomic events in the last 24 hours  
   - Explain economic or market relevance  

2. 🤖 Technology & AI Industry Updates  
   - Important AI, software, or tech industry news  
   - Trends in AI models, regulation, startups, enterprise adoption  
   - Why this matters for engineers or tech careers  

3. 📈 Indian Stock Market Overview  
   - Market performance (NIFTY, SENSEX if relevant)  
   - Main drivers (global cues, FII/DII activity, rates, earnings)  
   - Sector-wise movement (IT, Banking, Energy, etc.)

4. 🏢 Stock-Specific & Corporate News  
   - Important company or stock-related news  
   - Earnings, deals, regulations, results, or management updates  
   - Explain potential impact (short-term vs long-term)

5. 🪙 Commodities Snapshot  
   - Gold, Silver (and others if relevant)  
   - Price movement direction and key reasons  

6. ⚠️ Risks to Watch  
   - 2–4 upcoming risks or uncertainties  
   - Events, data releases, geopolitical tensions, policy decisions  
   - Mention timeline if known (today / this week / upcoming)

7. 📚 What I Can Learn Today  
   - One beginner-friendly finance concept  
   - One technology or AI concept  
   - Brief explanation and why it’s useful  

8. 🔍 Key Takeaways  
   - 3–5 bullet points summarizing today’s most important insights  

9. 🔗 Sources  
   - Provide reliable links for verification  
   - Prefer: Reuters, Bloomberg, RBI, SEBI, NSE, Moneycontrol, Economic Times, official company blogs, OpenAI/Google/Meta blogs  
   - Avoid social media unless primary source

Structure:

1. 🌍 Geopolitical & Global News
2. 🤖 Technology & AI Industry Updates
3. 📈 Indian Stock Market Overview
4. 🏢 Stock-Specific & Corporate News
5. 🪙 Commodities Snapshot (Gold, Silver)
6. ⚠️ Risks to Watch
7. 📚 What I Can Learn Today
8. 🔍 Key Takeaways (3–5 bullets)
9. 🔗 Sources (Reuters, Moneycontrol, NSE, official blogs)

If information is uncertain or still developing, clearly state that.
"""

response = client.responses.create(
    model="gpt-4.1-mini",
    input=PROMPT,
    max_output_tokens=1200  
)

print("\n===== DAILY DIGEST =====\n")
print(response.output_text)
