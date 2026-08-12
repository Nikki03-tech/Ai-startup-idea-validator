"""
Competitor Agent

Discovers, analyzes, and compares direct & indirect competitors.
"""

from tools.web_search_tool import WebSearchTool
from state.schema import Competitor, CompetitorAgentOutput


class CompetitorAgent:

    def __init__(self):
        self.search_tool = WebSearchTool()

    def build_search_queries(self, startup_idea: str) -> list[str]:
        return [
            f"top competitors of {startup_idea}",
            f"{startup_idea} alternatives",
            f"companies similar to {startup_idea}",
        ]

    def run(self, shared_memory):

        try:

            startup_idea = shared_memory.get(
                "startup_idea",
                ""
            )

            raw_results = list(
                shared_memory.get(
                    "search_results",
                    []
                )
            )

            for query in self.build_search_queries(
                startup_idea
            ):

                raw_results.extend(
                    self.search_tool.search(query)
                )

            seen_urls = set()
            competitors = []

            for item in raw_results:

                url = item.get("url", "")

                if not url or url in seen_urls:
                    continue

                seen_urls.add(url)

                competitors.append(
                    Competitor(
                        name=item.get(
                            "title",
                            "Unknown"
                        ),
                        website=url,
                        description=item.get(
                            "snippet",
                            ""
                        ),
                        source_urls=[url],
                    )
                )

            output = CompetitorAgentOutput(
                startup_idea=startup_idea,
                competitors=competitors,
            )

            return {
                "status": "success",
                "data": output,
                "message": (
                    "Competitor discovery "
                    "completed successfully."
                )
            }

        except Exception as e:

            return {
                "status": "failed",
                "data": None,
                "message": str(e)
            }