"""Competitor Agent

Discovers, analyzes, and compares direct & indirect competitors.

Input:
    SharedMemory (expects "startup_idea", optionally "search_results"
    already gathered upstream by the Web Search Agent)

Output:
{
    "status": "success",
    "data": CompetitorAgentOutput,
    "message": ""
}
"""

import json
import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from tools.web_search_tool import WebSearchTool
from state.schema import Competitor, CompetitorAgentOutput

load_dotenv()


class CompetitorAgent:

    def __init__(self):
        self.search_tool = WebSearchTool()
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-3.5-flash",
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.3
        )

    def build_search_queries(self, startup_idea: str) -> list[str]:
        return [
            f"top competitors of {startup_idea}",
            f"{startup_idea} alternatives",
            f"companies similar to {startup_idea}",
        ]

    def run(self, shared_memory):

        try:

            startup_idea = shared_memory.get("startup_idea", "")

            raw_results = list(shared_memory.get("search_results", []))

            for query in self.build_search_queries(startup_idea):
                raw_results.extend(self.search_tool.search(query))

            seen_urls = set()
            deduped_results = []

            for item in raw_results:

                url = item.get("url", "")

                if not url or url in seen_urls:
                    continue

                seen_urls.add(url)
                deduped_results.append(item)

            prompt = f"""
            You are analyzing competitors for this startup idea:

            Startup Idea:
            {startup_idea}

            Web Search Results:
            {deduped_results}

            From these search results, identify the real companies/products
            that compete directly or indirectly with this startup idea.

            For each competitor, only include details supported by the
            search results above. If pricing, strengths, or weaknesses
            cannot be determined from the sources, leave that field as an
            empty list/string rather than guessing.

            Return ONLY valid JSON in this exact shape:

            {{
                "competitors": [
                    {{
                        "name": "",
                        "website": "",
                        "description": "",
                        "strengths": [],
                        "weaknesses": [],
                        "source_urls": []
                    }}
                ]
            }}
            """

            response = self.llm.invoke(prompt)

            if isinstance(response.content, list):
                json_text = response.content[0]["text"]
            else:
                json_text = response.content

            json_text = json_text.strip()

            if json_text.startswith("```"):
                json_text = json_text.split("```")[1]
                if json_text.startswith("json"):
                    json_text = json_text[4:]
                json_text = json_text.strip()

            parsed = json.loads(json_text)

            competitors = [
                Competitor(**c) for c in parsed.get("competitors", [])
            ]

            output = CompetitorAgentOutput(
                startup_idea=startup_idea,
                competitors=competitors,
            )

            return {
                "status": "success",
                "data": output,
                "message": "Competitor discovery completed successfully."
            }

        except Exception as e:

            return {
                "status": "error",
                "data": None,
                "message": str(e)
            }
