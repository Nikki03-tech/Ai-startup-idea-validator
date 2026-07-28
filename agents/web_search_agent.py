"""
Web Search Agent

Input:
    SharedMemory

Output:
{
    "status": "success",
    "data": {
        "search_results": [...],
        "references": [...]
    },
    "message": ""
}
"""

from tools.web_search_tool import WebSearchTool


class WebSearchAgent:

    def __init__(self):
        self.search_tool = WebSearchTool()

    def run(self, shared_memory):

        try:

            startup_idea = shared_memory.get("startup_idea", "")
            keywords = shared_memory.get("keywords", [])

            if keywords:
                query = " ".join(keywords)
            else:
                query = startup_idea

            results = self.search_tool.search(query)

            references = [
                result["url"]
                for result in results
                if result.get("url")
            ]

            return {
                "status": "success",
                "data": {
                    "search_results": results,
                    "references": references,
                },
                "message": "Web search completed successfully."
            }

        except Exception as e:

            return {
                "status": "failed",
                "data": None,
                "message": str(e)
            }