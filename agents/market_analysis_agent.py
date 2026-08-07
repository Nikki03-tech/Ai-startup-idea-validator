class MarketAnalysisAgent:

    def run(self, shared_memory):
        try:
            startup_idea = shared_memory.get("startup_idea", "")
            web_results = shared_memory.get("web_search_results", [])

            analysis = self.analyze(
                startup_idea,
                web_results
            )

            return {
                "status": "success",
                "data": analysis,
                "message": "Market analysis completed successfully"
            }

        except Exception as e:
            return {
                "status": "error",
                "data": {},
                "message": str(e)
            }
