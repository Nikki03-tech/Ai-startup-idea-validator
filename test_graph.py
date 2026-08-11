from pipeline.graph import graph


def print_section(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def print_bullets(items):
    if not items:
        print("  • None")
        return

    for item in items:
        if isinstance(item, dict):
            # Print the most useful field if available
            text = (
                item.get("feature")
                or item.get("name")
                or item.get("risk")
                or item.get("title")
                or str(item)
            )
            print(f"  • {text}")
        else:
            print(f"  • {item}")


def print_market_analysis(data):
    print_section("1. MARKET ANALYSIS")

    if not data:
        print("No market analysis available.")
        return

    print("\nMarket Size:")
    print(data.get("market_size", "N/A"))

    print("\nTarget Audience:")
    print(data.get("target_audience", "N/A"))

    print("\nIndustry Trends:")
    print(data.get("industry_trends", "N/A"))

    print("\nOpportunities:")
    print(data.get("opportunities", "N/A"))


def print_competitor_analysis(data):
    print_section("2. COMPETITOR ANALYSIS")

    if not data:
        print("No competitor analysis available.")
        return

    # Handles Pydantic-style object
    competitors = getattr(data, "competitors", None)

    # Handles dictionary-style output
    if competitors is None and isinstance(data, dict):
        competitors = data.get("competitors", [])

    if not competitors:
        print("No competitors found.")
        return

    for i, competitor in enumerate(competitors, 1):

        if hasattr(competitor, "model_dump"):
            competitor = competitor.model_dump()

        if isinstance(competitor, dict):
            name = competitor.get("name", "Unknown")
            website = competitor.get("website", "N/A")
            description = competitor.get("description", "N/A")

            print(f"\n{i}. {name}")
            print(f"   Website: {website}")
            print(f"   Description: {description}")

            strengths = competitor.get("strengths", [])
            weaknesses = competitor.get("weaknesses", [])

            if strengths:
                print("   Strengths:")
                print_bullets(strengths)

            if weaknesses:
                print("   Weaknesses:")
                print_bullets(weaknesses)

        else:
            print(f"\n{i}. {competitor}")


def print_swot(data):
    print_section("3. SWOT & RISK ANALYSIS")

    if not data:
        print("No SWOT analysis available.")
        return

    print("\nStrengths:")
    print_bullets(data.get("strengths", []))

    print("\nWeaknesses:")
    print_bullets(data.get("weaknesses", []))

    print("\nOpportunities:")
    print_bullets(data.get("opportunities", []))

    print("\nThreats:")
    print_bullets(data.get("threats", []))

    risks = data.get("risks", [])

    if risks:
        print("\nRisks & Mitigation:")

        for i, risk in enumerate(risks, 1):
            print(f"\n  {i}. {risk.get('risk', 'Unknown risk')}")
            print(f"     Severity: {risk.get('severity', 'N/A')}")
            print(f"     Mitigation: {risk.get('mitigation', 'N/A')}")


def print_mvp(data):
    print_section("4. MVP RECOMMENDATION")

    if not data:
        print("No MVP recommendation available.")
        return

    print("\nMust Have:")
    for item in data.get("must_have", []):
        print(f"  • {item.get('feature', 'N/A')}")
        print(f"    Reason: {item.get('reason', 'N/A')}")
        print(f"    Validation Goal: {item.get('validation_goal', 'N/A')}")

    print("\nNice to Have:")
    for item in data.get("nice_to_have", []):
        print(f"  • {item.get('feature', 'N/A')}")
        print(f"    Reason: {item.get('reason', 'N/A')}")
        print(f"    Validation Goal: {item.get('validation_goal', 'N/A')}")

    print("\nFuture Features:")
    for item in data.get("future_features", []):
        print(f"  • {item.get('feature', 'N/A')}")
        print(f"    Reason: {item.get('reason', 'N/A')}")

    rationale = data.get("prioritization_rationale")

    if rationale:
        print("\nPrioritization Rationale:")
        print(rationale)


def print_gtm(data):
    print_section("5. GO-TO-MARKET STRATEGY")

    if not data:
        print("No GTM strategy available.")
        return

    # Your current output has a nested gtm_strategy structure.
    strategy = data.get("gtm_strategy", data)

    if not isinstance(strategy, dict):
        print(strategy)
        return

    print("\nStartup Idea:")
    print(strategy.get("startup_idea", "N/A"))

    market = strategy.get("market_analysis", {})

    if market:
        print("\nTarget Market:")
        print(market.get("target_audience", "N/A"))

        print("\nMarket Opportunity:")
        print(market.get("opportunities", "N/A"))

    mvp = strategy.get("mvp_recommendation", {})

    if mvp:
        print("\nMVP Focus:")
        for item in mvp.get("must_have", []):
            print(f"  • {item.get('feature', 'N/A')}")


def print_report(data):
    print_section("6. FINAL VALIDATION REPORT")

    if not data:
        print("No report available.")
        return

    if isinstance(data, dict):
        for key, value in data.items():

            if key == "system_prompt":
                continue

            print(f"\n{key.replace('_', ' ').title()}:")

            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if sub_key == "system_prompt":
                        continue

                    print(f"\n  {sub_key.replace('_', ' ').title()}:")
                    print(f"  {sub_value}")

            else:
                print(value)

    else:
        print(data)


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

    print("\n")
    print("=" * 70)
    print("        AI STARTUP IDEA VALIDATOR")
    print("=" * 70)

    print("\nStartup Idea:")
    print(initial_state["startup_idea"])

    print("\nRunning validation pipeline...")

    try:

        final_state = graph.invoke(initial_state)

        # ---------------------------------------------------------
        # MARKET ANALYSIS
        # ---------------------------------------------------------
        print_market_analysis(
            final_state.get("market_analysis", {})
        )

        # ---------------------------------------------------------
        # COMPETITOR ANALYSIS
        # ---------------------------------------------------------
        print_competitor_analysis(
            final_state.get("competitor_analysis", {})
        )

        # ---------------------------------------------------------
        # SWOT
        # ---------------------------------------------------------
        print_swot(
            final_state.get("swot_analysis", {})
        )

        # ---------------------------------------------------------
        # MVP
        # ---------------------------------------------------------
        print_mvp(
            final_state.get("mvp_recommendation", {})
        )

        # ---------------------------------------------------------
        # GTM
        # ---------------------------------------------------------
        print_gtm(
            final_state.get("gtm_strategy", {})
        )

        # ---------------------------------------------------------
        # REPORT
        # ---------------------------------------------------------
        print_report(
            final_state.get("report", {})
        )

        # ---------------------------------------------------------
        # PIPELINE STATUS
        # ---------------------------------------------------------
        print_section("PIPELINE COMPLETED")

        print("✓ Web Search")
        print("✓ Market Analysis")
        print("✓ Competitor Analysis")
        print("✓ SWOT & Risk Analysis")
        print("✓ MVP Recommendation")
        print("✓ GTM Strategy")
        print("✓ Report Generation")

        print("\nValidation pipeline executed successfully.")

    except Exception as e:

        print("\n")
        print("=" * 70)
        print("PIPELINE FAILED")
        print("=" * 70)

        print(f"\nError: {e}")


if __name__ == "__main__":
    main()