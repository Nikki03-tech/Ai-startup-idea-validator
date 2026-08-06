"""
DDGS Web Search Tool

Performs web searches using DDGS and returns
structured search results for the Web Search Agent.
"""

import os
from ddgs import DDGS


class WebSearchTool:

    def __init__(self):
        self.max_results = int(os.getenv("MAX_RESULTS", 5))

    def search(self, query: str):
        """
        Perform web search using DDGS.

        Args:
            query (str): Search query

        Returns:
            list[dict]
        """

        results = []

        try:
            with DDGS() as ddgs:

                search_results = ddgs.text(
                    query,
                    max_results=self.max_results
                )

                for item in search_results:

                    results.append(
                        {
                            "title": item.get("title", ""),
                            "url": item.get("href", ""),
                            "snippet": item.get("body", ""),
                        }
                    )

        except Exception as e:
            print(f"Web Search Error: {e}")

        return results