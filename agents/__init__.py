def run(self, shared_memory):
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-3.6-flash-lite",
            google_api_key=os.getenv("GEMINI_API_KEY")
        )

        # rest of code

    except Exception as e:
        return {
            "status": "error",
            "data": {},
            "message": str(e)
        }