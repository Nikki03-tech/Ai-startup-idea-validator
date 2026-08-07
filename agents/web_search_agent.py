from tools.web_search_tool import WebSearchTool

def run(shared_memory):
    try:
        startup_idea = shared_memory.get("startup_idea", "")

        search_tool = WebSearchTool()
        results = search_tool.search(startup_idea)

        return {
            "status": "success",
            "data": {
                "search_results": results,
                "references": [r["url"] for r in results]
            },
            "message": "Web search completed successfully."
        }

    except Exception as e:
        return {
            "status": "error",
            "data": {},
            "message": str(e)
        }