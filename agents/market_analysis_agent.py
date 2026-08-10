from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
import json

load_dotenv()


class MarketAnalysisAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-3.5-flash",
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.3
        )

    def run(self, shared_memory):
        try:
            startup_idea = shared_memory.get("startup_idea", "")
            search_results = shared_memory.get("search_results", [])

            prompt = f"""
            Analyze the following startup idea:

            Startup Idea:
            {startup_idea}

            Search Results:
            {search_results}

            Return ONLY valid JSON:

            {{
                "market_size": "",
                "target_audience": "",
                "industry_trends": "",
                "opportunities": ""
            }}
            """

            response = self.llm.invoke(prompt)

            if isinstance(response.content, list):
                json_text = response.content[0]["text"]
            else:
                json_text = response.content

            analysis = json.loads(json_text)

            return {
                "status": "success",
                "data": analysis,
                "message": "Market analysis completed successfully."
            }

        except Exception as e:
            return {
                "status": "error",
                "data": {},
                "message": str(e)
            }