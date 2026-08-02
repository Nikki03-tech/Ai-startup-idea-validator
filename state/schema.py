"""State Schemas

Pydantic models for structured agent outputs and pipeline state data.
"""

from pydantic import BaseModel, Field


class Competitor(BaseModel):
    """A single competitor discovered for the startup idea."""

    name: str = Field(..., description="Company / product name")
    website: str | None = Field(None, description="Official website URL")
    description: str = Field("", description="Short summary of what they do")

    pricing: str | None = Field(None, description="Free-text pricing summary")
    features: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)

    source_urls: list[str] = Field(
        default_factory=list, description="URLs used to identify this competitor"
    )


class MarketGap(BaseModel):
    """An underserved need spotted while researching competitors."""

    description: str
    evidence: list[str] = Field(default_factory=list)


class CompetitorAgentOutput(BaseModel):
    """Structured output produced by the Competitor Agent."""

    startup_idea: str
    competitors: list[Competitor] = Field(default_factory=list)
    market_gaps: list[MarketGap] = Field(default_factory=list)
    summary: str | None = None
