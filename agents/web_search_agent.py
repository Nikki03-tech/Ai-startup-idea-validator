class WebSearchAgent:

    def run(self, shared_memory):
        try:
            startup_idea = shared_memory.get("startup_idea", "")

            results = self.search_web(startup_idea)

            return {
                "status": "success",
                "data": {
                    "search_results": results
                },
                "message": "Web search completed successfully"
            }

        except Exception as e:
            return {
                "status": "error",
                "data": {},
                "message": str(e)
            }
