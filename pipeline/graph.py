"""
Agent Workflow Graph

LangGraph sequential workflow for the AI Startup Idea Validator.
Each node executes one agent, updates the shared GraphState,
and passes it to the next node.
"""

from typing import TypedDict, Dict, Any

from langgraph.graph import StateGraph, START, END

from agents.web_search_agent import WebSearchAgent
from agents.market_analysis_agent import MarketAnalysisAgent
from agents.competitor_agent import CompetitorAgent
from agents.swot_risk_agent import SWOTRiskAgent
from agents.mvp_recommendation_agent import MVPRecommendationAgent
from agents.gtm_strategy_agent import GTMStrategyAgent
from agents.report_agent import ReportAgent

# ---------------------------------------------------------
# Shared Graph State
# ---------------------------------------------------------

class GraphState(TypedDict):
    startup_idea: str

    idea_extraction: Dict[str, Any]

    web_search_results: Dict[str, Any]

    market_analysis: Dict[str, Any]

    competitor_analysis: Dict[str, Any]

    swot_analysis: Dict[str, Any]

    mvp_recommendation: Dict[str, Any]

    gtm_strategy: Dict[str, Any]

    report: Dict[str, Any]


# ---------------------------------------------------------
# Agent Instances
# ---------------------------------------------------------

web_search_agent = WebSearchAgent()
market_agent = MarketAnalysisAgent()
competitor_agent = CompetitorAgent()
swot_agent = SWOTRiskAgent()
mvp_agent = MVPRecommendationAgent()
gtm_agent = GTMStrategyAgent()
report_agent = ReportAgent()

# ---------------------------------------------------------
# Nodes
# ---------------------------------------------------------

def web_search_node(state: GraphState):

    result = web_search_agent.run(state)

    if result["status"] == "success":

        state["web_search_results"] = result["data"]

        state["search_results"] = result["data"]["search_results"]

        state["references"] = result["data"]["references"]

    return state


def market_analysis_node(state: GraphState):

    result = market_agent.run(state)

    if result["status"] == "success":

        state["market_analysis"] = result["data"]

    return state


def competitor_analysis_node(state: GraphState):

    result = competitor_agent.run(state)

    if result["status"] == "success":

        state["competitor_analysis"] = result["data"]

        # Required by SWOT Agent
        if hasattr(result["data"], "competitors"):
            state["competitors"] = result["data"].competitors

    return state


def swot_analysis_node(state: GraphState):

    result = swot_agent.run(state)

    if result["status"] == "success":

        state["swot_analysis"] = result["data"]

    return state


def mvp_node(state: GraphState):

    result = mvp_agent.run(state)

    if result["status"] == "success":

        state["mvp_recommendation"] = result["data"]

    return state


def gtm_node(state: GraphState):

    result = gtm_agent.run(state)

    if result["status"] == "success":
        state["gtm_strategy"] = result["data"]

    return state


def report_node(state: GraphState):

    result = report_agent.run(state)

    if result["status"] == "success":

        state["report"] = result["data"]

    return state

# ---------------------------------------------------------
# Build Graph
# ---------------------------------------------------------

graph_builder = StateGraph(GraphState)

graph_builder.add_node("web_search", web_search_node)

graph_builder.add_node("market_analysis", market_analysis_node)

graph_builder.add_node("competitor_analysis", competitor_analysis_node)

graph_builder.add_node("swot_analysis", swot_analysis_node)

graph_builder.add_node("mvp_recommendation", mvp_node)

graph_builder.add_node("gtm_strategy", gtm_node)

graph_builder.add_node("report_generation", report_node,)



graph_builder.add_edge(START, "web_search")

graph_builder.add_edge("web_search", "market_analysis")

graph_builder.add_edge("market_analysis", "competitor_analysis")

graph_builder.add_edge("competitor_analysis", "swot_analysis")

graph_builder.add_edge("swot_analysis", "mvp_recommendation")

graph_builder.add_edge("mvp_recommendation", "gtm_strategy")

graph_builder.add_edge("gtm_strategy", "report_generation")

graph_builder.add_edge("report_generation", END)


# Compile graph
graph = graph_builder.compile()