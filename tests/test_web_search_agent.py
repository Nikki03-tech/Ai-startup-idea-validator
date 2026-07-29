from agents.web_search_agent import WebSearchAgent

agent = WebSearchAgent()

shared_memory = {
    "startup_idea": "AI Startup Idea Validator",
    "keywords": [
        "AI startup validation",
        "market research",
        "startup competitors"
    ]
}

print("Running Web Search Agent...")

result = agent.run(shared_memory)
print("Running Web Search Agent...")
print(result)
