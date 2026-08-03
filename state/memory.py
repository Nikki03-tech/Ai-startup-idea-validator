"""Shared Memory

Centralized memory object passed across agents in the pipeline.
"""
"""Shared Memory

Centralized memory object passed across agents in the pipeline.
"""
from pydantic import BaseModel, Field
from typing import List

from state.schema import (
    StartupIdea,
    SearchResult,
    ValidationReport,
    Competitor,
    IdeaExtraction,
)


class SharedMemory(BaseModel):
    startup_idea: StartupIdea | None = None

    search_results: List[SearchResult] = Field(default_factory=list)

    competitors: List[Competitor] = Field(default_factory=list)

    market_analysis: dict = Field(default_factory=dict)

    swot_analysis: dict = Field(default_factory=dict)

    mvp_recommendation: dict = Field(default_factory=dict)

    gtm_strategy: dict = Field(default_factory=dict)

    report: ValidationReport | None = None
    
    idea_extraction: IdeaExtraction | None = None
