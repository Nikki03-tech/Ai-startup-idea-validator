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
    
    # Analysis & Scoring fields for dynamic output
    validation_score: int
    market_potential: str  # High, Medium, or Low
    risk_level: str        # High, Medium, or Low
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    opportunities: List[str] = Field(default_factory=list)
    threats: List[str] = Field(default_factory=list)
    gtm_strategy: str = ""


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

class GraphState(TypedDict):
    """
    Shared state flowing through the LangGraph pipeline.
    """

    startup_idea: StartupIdea
    extracted_idea: Optional[IdeaExtraction]
    search_results: List[SearchResult]
    market_analysis: Dict[str, Any]
    competitor_analysis: List[Competitor]
    swot_analysis: Dict[str, Any]
    mvp_recommendation: Dict[str, Any]
    gtm_strategy: Dict[str, Any]
    validation_report: Optional[ValidationReport]
    current_agent: str
    thread_id: str
    execution_status: str
    errors: List[str]