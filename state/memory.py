"""Shared Memory

Centralized memory object passed across agents in the pipeline.
"""
from typing import Any, List, Union

from pydantic import BaseModel, Field

from state.schema import (
    StartupIdea,
    IdeaExtraction,
)


class SharedMemory(BaseModel):
    startup_idea: StartupIdea | None = None

    # The real pipeline (pipeline/graph.py) stores plain text/dicts
    # here (WebSearchAgent returns a text summary, CompetitorAgent
    # returns a list of competitor dicts, ReportAgent returns a plain
    # dict) rather than validated SearchResult/Competitor/
    # ValidationReport model instances, so these fields are typed
    # loosely to match what's actually assigned - avoiding Pydantic
    # serialization warnings on every real run.
    search_results: Union[str, List[Any]] = ""

    competitors: List[Any] = Field(default_factory=list)

    market_analysis: dict = Field(default_factory=dict)

    swot_analysis: dict = Field(default_factory=dict)

    mvp_recommendation: dict = Field(default_factory=dict)

    gtm_strategy: dict = Field(default_factory=dict)

    report: dict | None = None

    idea_extraction: IdeaExtraction | None = None
