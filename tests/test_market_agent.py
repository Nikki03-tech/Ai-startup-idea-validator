from agents.market_analysis_agent import MarketAnalysisAgent

agent = MarketAnalysisAgent()

shared_memory = {
    "startup_idea": "AI Startup Idea Validator",
    "search_results": [
        {
            "title": "AI Startup Market Growth",
            "url": "https://example.com",
            "snippet": "The AI startup ecosystem is growing rapidly."
        }
    ]
}

print("=== Running Market Analysis Agent ===")

result = agent.run(shared_memory)

print("\n=== Output ===")
print(result)