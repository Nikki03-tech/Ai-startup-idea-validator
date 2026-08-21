"""
Agent Workflow Graph

LangGraph sequential workflow for the AI Startup Idea Validator.

Each node executes one agent, updates the shared GraphState,
and passes the updated state to the next node.
"""

from langgraph.graph import StateGraph, START, END

from agents.web_search_agent import WebSearchAgent
from agents.market_analysis_agent import MarketAnalysisAgent
from agents.competitor_agent import CompetitorAgent
from agents.swot_risk_agent import SWOTRiskAgent
from agents.mvp_recommendation_agent import MVPRecommendationAgent
from agents.gtm_strategy_agent import GTMStrategyAgent
from agents.report_agent import ReportAgent
from state.schema import GraphState


# =========================================================
# Agent Instances
# =========================================================

web_search_agent = WebSearchAgent()
market_agent = MarketAnalysisAgent()
competitor_agent = CompetitorAgent()
swot_agent = SWOTRiskAgent()
mvp_agent = MVPRecommendationAgent()
gtm_agent = GTMStrategyAgent()
report_agent = ReportAgent()


# =========================================================
# Helper Functions
# =========================================================

def record_error(state: GraphState, agent_name: str, message: str) -> None:
    """
    Record an agent failure without crashing the entire graph.
    """

    errors = state.get("errors", [])

    errors.append(
        f"{agent_name}: {message}"
    )

    state["errors"] = errors
    state["execution_status"] = "failed"


# =========================================================
# Nodes
# =========================================================

def web_search_node(state: GraphState):
    """
    Execute Web Search Agent.
    """

    state["current_agent"] = "web_search"

    try:
        result = web_search_agent.run(state)

        if result.get("status") == "success":

            data = result.get("data") or {}

            state["web_search_results"] = data

            state["search_results"] = data.get(
                "search_results",
                []
            )

            state["references"] = data.get(
                "references",
                []
            )

        else:
            record_error(
                state,
                "Web Search Agent",
                result.get("message", "Unknown error")
            )

    except Exception as e:
        record_error(
            state,
            "Web Search Agent",
            str(e)
        )

    return state


def market_analysis_node(state: GraphState):
    """
    Execute Market Analysis Agent.
    """

    state["current_agent"] = "market_analysis"

    try:
        result = market_agent.run(state)

        if result.get("status") == "success":

            data = result.get("data") or {}

            state["market_analysis"] = data.get(
                "market_analysis",
                {}
            )

        else:
            record_error(
                state,
                "Market Analysis Agent",
                result.get("message", "Unknown error")
            )

    except Exception as e:
        record_error(
            state,
            "Market Analysis Agent",
            str(e)
        )

    return state


def competitor_analysis_node(state: GraphState):
    """
    Execute Competitor Analysis Agent.
    """

    state["current_agent"] = "competitor_analysis"

    try:
        result = competitor_agent.run(state)

        if result.get("status") == "success":

            data = result.get("data")

            state["competitor_analysis"] = data

            # Support Pydantic output such as:
            # CompetitorAgentOutput(..., competitors=[...])
            if hasattr(data, "competitors"):

                state["competitors"] = data.competitors

            # Support dictionary output as well
            elif isinstance(data, dict):

                state["competitors"] = data.get(
                    "competitors",
                    []
                )

        else:
            record_error(
                state,
                "Competitor Agent",
                result.get("message", "Unknown error")
            )

    except Exception as e:
        record_error(
            state,
            "Competitor Agent",
            str(e)
        )

    return state


def swot_analysis_node(state: GraphState):
    """
    Execute SWOT & Risk Agent.
    """
    state["current_agent"] = "swot_analysis"

    try:
        result = swot_agent.run(state)

        if result.get("status") == "success":
            data = result.get("data") or {}

            state["swot_analysis"] = data.get(
                "swot_analysis",
                {}
            )

        else:
            record_error(
                state,
                "SWOT & Risk Agent",
                result.get("message", "Unknown error")
            )

    except Exception as e:
        record_error(
            state,
            "SWOT & Risk Agent",
            str(e)
        )

    return state


def mvp_node(state: GraphState):
    """
    Execute MVP Recommendation Agent.
    """
    state["current_agent"] = "mvp_recommendation"

    try:
        result = mvp_agent.run(state)

        if result.get("status") == "success":
            data = result.get("data") or {}

            state["mvp_recommendation"] = data.get(
                "mvp_recommendation",
                {}
            )

        else:
            record_error(
                state,
                "MVP Recommendation Agent",
                result.get("message", "Unknown error")
            )

    except Exception as e:
        record_error(
            state,
            "MVP Recommendation Agent",
            str(e)
        )

    return state


def gtm_node(state: GraphState):
    """
    Execute GTM Strategy Agent.
    """

    state["current_agent"] = "gtm_strategy"

    try:
        result = gtm_agent.run(state)

        if result.get("status") == "success":

            data = result.get("data") or {}

            state["gtm_strategy"] = data.get(
                "gtm_strategy",
                {}
            )

        else:
            record_error(
                state,
                "GTM Strategy Agent",
                result.get("message", "Unknown error")
            )

    except Exception as e:
        record_error(
            state,
            "GTM Strategy Agent",
            str(e)
        )

    return state


def report_node(state: GraphState):
    """
    Execute Report Agent.
    """

    state["current_agent"] = "report_generation"

    try:
        result = report_agent.run(state)

        if result.get("status") == "success":

            data = result.get("data") or {}

            state["report"] = data.get(
                "validation_report",
                {}
            )

        else:
            record_error(
                state,
                "Report Agent",
                result.get("message", "Unknown error")
            )

    except Exception as e:
        record_error(
            state,
            "Report Agent",
            str(e)
        )

    return state


# =========================================================
# Build Graph
# =========================================================

graph_builder = StateGraph(GraphState)


# Add nodes
graph_builder.add_node(
    "web_search",
    web_search_node
)

graph_builder.add_node(
    "market_analysis",
    market_analysis_node
)

graph_builder.add_node(
    "competitor_analysis",
    competitor_analysis_node
)

graph_builder.add_node(
    "swot_analysis",
    swot_analysis_node
)

graph_builder.add_node(
    "mvp_recommendation",
    mvp_node
)

graph_builder.add_node(
    "gtm_strategy",
    gtm_node
)

graph_builder.add_node(
    "report_generation",
    report_node
)


# =========================================================
# Workflow Edges
# =========================================================

graph_builder.add_edge(
    START,
    "web_search"
)

graph_builder.add_edge(
    "web_search",
    "market_analysis"
)

graph_builder.add_edge(
    "market_analysis",
    "competitor_analysis"
)

graph_builder.add_edge(
    "competitor_analysis",
    "swot_analysis"
)

graph_builder.add_edge(
    "swot_analysis",
    "mvp_recommendation"
)

graph_builder.add_edge(
    "mvp_recommendation",
    "gtm_strategy"
)

graph_builder.add_edge(
    "gtm_strategy",
    "report_generation"
)

graph_builder.add_edge(
    "report_generation",
    END
)


# =========================================================
# Compile Graph
# =========================================================

graph = graph_builder.compile()
