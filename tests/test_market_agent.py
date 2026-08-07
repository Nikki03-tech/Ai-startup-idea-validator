from agents.market_analysis_agent import run

shared_memory = {
    "startup_idea": "AI Startup Idea Validator",
    "search_results": [
        {"title": "AI Market", "snippet": "Growing rapidly"}
    ]
}

result = run(shared_memory)

print(result)