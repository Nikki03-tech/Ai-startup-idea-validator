"""
State Schemas

Pydantic models for structured agent outputs and pipeline state data.
"""

from typing import List, Dict, Any, Optional, TypedDict
from pydantic import BaseModel, Field


# ==========================================================
# Input Models
# ==========================================================

class StartupIdea(BaseModel):
    idea: str
    target_audience: Optional[str] = None
    industry: Optional[str] = None
    constraints: List[str] = Field(default_factory=list)


class IdeaExtraction(BaseModel):
    problem: str
    solution: str
    target_audience: str
    value_proposition: str
    keywords: List[str] = Field(default_factory=list)


class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str


# ==========================================================
# Competitor Models
# ==========================================================

class Competitor(BaseModel):
    name: str
    website: str = ""
    description: str = ""
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    source_urls: List[str] = Field(default_factory=list)


class CompetitorAgentOutput(BaseModel):
    startup_idea: str
    competitors: List[Competitor] = Field(default_factory=list)


# ==========================================================
# Final Report
# ==========================================================

class ValidationReport(BaseModel):
    executive_summary: str = ""

    market_analysis: Dict[str, Any] = Field(default_factory=dict)

    competitor_analysis: List[Competitor] = Field(default_factory=list)

    swot_analysis: Dict[str, Any] = Field(default_factory=dict)

    mvp_recommendation: Dict[str, Any] = Field(default_factory=dict)

    gtm_strategy: Dict[str, Any] = Field(default_factory=dict)

    references: List[str] = Field(default_factory=list)


# ==========================================================
# LangGraph Shared State
# ==========================================================

class GraphState(TypedDict, total=False):
    """
    Shared state that flows through the LangGraph pipeline
    (pipeline/graph.py). This is the single canonical definition -
    every node reads the information it needs from this state and
    writes its output back into it.
    """

    # Original user input
    startup_idea: str

    # Idea extraction
    idea_extraction: Dict[str, Any]

    # Web search
    web_search_results: Dict[str, Any]
    search_results: List[Dict[str, Any]]
    references: List[str]

    # Agent outputs
    market_analysis: Dict[str, Any]
    competitor_analysis: Any
    competitors: List[Any]
    swot_analysis: Dict[str, Any]
    mvp_recommendation: Dict[str, Any]
    gtm_strategy: Dict[str, Any]

    # Final report
    report: Dict[str, Any]

    # Execution metadata
    current_agent: str
    execution_status: str
    execution_plan: Dict[str, str]
    errors: List[str]
