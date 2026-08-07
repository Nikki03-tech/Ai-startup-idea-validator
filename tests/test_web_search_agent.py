from agents.web_search_agent import run

shared_memory = {
    "startup_idea": "AI-powered startup idea validation platform"
}

result = run(shared_memory)
print(result)