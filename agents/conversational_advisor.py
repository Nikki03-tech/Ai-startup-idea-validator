"""
Conversational Advisor

Provides interactive Q&A over the generated validation report for founders.
"""


def answer_question(report, question):

    question = question.lower()

    if "market" in question:
        return report.get("Market Analysis", "Market analysis not available.")

    elif "competitor" in question:
        return report.get("Competitor Analysis", "Competitor analysis not available.")

    elif "swot" in question:
        return report.get("SWOT Analysis", "SWOT analysis not available.")

    elif "risk" in question:
        return report.get("Risk Analysis", "Risk analysis not available.")

    elif "mvp" in question:
        return report.get("MVP Recommendation", "MVP recommendation not available.")

    elif "gtm" in question or "marketing" in question:
        return report.get("Go-To-Market Strategy", "GTM strategy not available.")

    elif "score" in question:
        return report.get("Final Validation Score", "Score not available.")

    elif "summary" in question:
        return report.get("Executive Summary", "Summary not available.")

    else:
        return (
            "I couldn't understand your question. "
            "Please ask about Market, Competitor, SWOT, Risk, MVP, GTM, Summary, or Score."
        )

    question = question.lower()

    if "market" in question:
        return report["Market Analysis"]

    elif "competitor" in question:
        return report["Competitor Analysis"]

    elif "swot" in question:
        return report["SWOT Analysis"]

    elif "risk" in question:
        return report["Risk Analysis"]

    elif "mvp" in question:
        return report["MVP Recommendation"]

    elif "gtm" in question or "marketing" in question:
        return report["Go-To-Market Strategy"]

    elif "score" in question:
        return report["Final Validation Score"]

    else:
        return (
            "I couldn't find that information in the validation report. "
            "Please ask about market analysis, competitors, SWOT, risk, MVP, GTM, or score."
        )