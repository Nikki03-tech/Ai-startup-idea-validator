"""Tests for Competitor Agent."""

import sys

sys.stdout.reconfigure(encoding="utf-8")

from agents.competitor_agent import CompetitorAgent

agent = CompetitorAgent()

shared_memory = {
    "startup_idea": "AI-powered meal planning app for people with dietary restrictions",
    "search_results": [],
}

print("=== Running Competitor Agent ===")

result = agent.run(shared_memory)

print("\n=== Output ===")
print(result)
