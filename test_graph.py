from pipeline.graph import graph


def main():

    initial_state = {
        "startup_idea": (
            "An AI platform that validates startup ideas "
            "using market research and competitor analysis."
        ),
        "idea_extraction": {},
        "web_search_results": {},
        "market_analysis": {},
        "competitor_analysis": {},
        "swot_analysis": {},
        "mvp_recommendation": {},
        "gtm_strategy": {},
        "report": {},
    }

    print("\n========== RUNNING AI STARTUP IDEA VALIDATOR ==========\n")

    try:
        final_state = graph.invoke(initial_state)

        print("\n========== FINAL STATE ==========\n")

        for key, value in final_state.items():
            print(f"\n{key}:")
            print(value)

        print("\n========== PIPELINE COMPLETED ==========\n")

    except Exception as e:
        print("\n========== PIPELINE FAILED ==========\n")
        print(f"Error: {e}")


if __name__ == "__main__":
    main()