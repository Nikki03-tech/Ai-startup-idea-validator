
def generate_validation_report(
    startup_name,
    market_analysis,
    competitor_analysis,
    swot,
    risk,
    mvp,
    gtm,
    score,
):

    report = {
        "Executive Summary": f"{startup_name} has been analysed successfully.",

        "Market Analysis": market_analysis,

        "Competitor Analysis": competitor_analysis,

        "SWOT Analysis": swot,

        "Risk Analysis": risk,

        "MVP Recommendation": mvp,

        "Go-To-Market Strategy": gtm,

        "Final Validation Score": score,
    }

    return report