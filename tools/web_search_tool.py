from langchain_core.tools import tool
from langchain_community.tools.ddg_search.tool import DuckDuckGoSearchRun

_ddg = DuckDuckGoSearchRun()
class WebSearchTool:
    """Wrapper class providing structured web search operations."""
    def search(self, query: str):
        try:
            res = _ddg.run(query)
            return [{"snippet": res, "url": "https://duckduckgo.com"}]
        except Exception as e:
            return [{"snippet": f"Search error: {str(e)}", "url": ""}]

@tool
def execute_web_search(query: str) -> str:
    """Performs a live web search to retrieve real-time market data, competitors, and trends."""
    try:
        return _ddg.run(query)
    except Exception as e:
        return f"Error executing search tool: {str(e)}"