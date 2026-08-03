"""State Schemas

Pydantic models for structured agent outputs and pipeline state data.
"""
"""State Schemas

Pydantic models for structured agent outputs and pipeline state data.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class StartupIdea(BaseModel):
    idea: str
    target_audience: Optional[str] = None
    industry: Optional[str] = None
    constraints: Optional[List[str]] = Field(default_factory=list)


class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str


class Competitor(BaseModel):
    name: str
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)


class ValidationReport(BaseModel):
    executive_summary: str = ""
    market_analysis: Dict[str, Any] = Field(default_factory=dict)
    competitor_analysis: List[Competitor] = Field(default_factory=list)
    swot_analysis: Dict[str, Any] = Field(default_factory=dict)
    mvp_recommendation: Dict[str, Any] = Field(default_factory=dict)
    gtm_strategy: Dict[str, Any] = Field(default_factory=dict)
    references: List[str] = Field(default_factory=list)

class IdeaExtraction(BaseModel):
    problem: str
    solution: str
    target_audience: str
    value_proposition: str
    keywords: List[str]