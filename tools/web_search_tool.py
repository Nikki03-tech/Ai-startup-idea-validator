from langchain_core.tools import tool
from ddgs import DDGS


class WebSearchTool:
    """Wrapper class providing structured web search operations."""

    def search(self, query: str):
        try:
            results = []

            with DDGS() as ddgs:
                search_results = ddgs.text(
                    query,
                    max_results=5
                )

                for result in search_results:
                    results.append({
                        "title": result.get("title", ""),
                        "snippet": result.get("body", ""),
                        "url": result.get("href", "")
                    })

            return results

        except Exception as e:
            return [{
                "title": "",
                "snippet": f"Search error: {str(e)}",
                "url": ""
            }]


@tool
def execute_web_search(query: str) -> str:
    """Performs a live web search and returns source titles, URLs, and snippets."""

    try:
        results = []

        with DDGS() as ddgs:
            search_results = ddgs.text(
                query,
                max_results=5
            )

            for result in search_results:
                results.append(
                    f"Title: {result.get('title', '')}\n"
                    f"URL: {result.get('href', '')}\n"
                    f"Snippet: {result.get('body', '')}"
                )

        return "\n\n".join(results)

    except Exception as e:
        return f"Error executing search tool: {str(e)}"
