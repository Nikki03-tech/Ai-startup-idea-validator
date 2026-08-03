"""Agent Workflow Graph

Defines the multi-agent graph, node execution sequence, and conditional routing.
"""
from typing import TypedDict

from langgraph.graph import StateGraph, START, END


class GraphState(TypedDict):
    startup_idea: str
    idea_extraction: dict
    web_search_results: dict
    market_analysis: dict
    competitor_analysis: dict
    swot_analysis: dict
    mvp_recommendation: dict
    gtm_strategy: dict
    report: dict


graph_builder = StateGraph(GraphState)