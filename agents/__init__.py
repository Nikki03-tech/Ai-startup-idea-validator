def run(self, shared_memory):
    try:
        llm = ChatGoogleGenerativeAI(
            model="openai/gpt-oss-20b",
            google_api_key=os.getenv("GEMINI_API_KEY")
        )

        # rest of code

    except Exception as e:
        return {
            "status": "error",
            "data": {},
            "message": str(e)
        }