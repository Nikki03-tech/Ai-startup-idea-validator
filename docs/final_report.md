# Final Validation Report Structure

Reference for the report produced by the **Report Agent**
(`agents/report_agent.py`), the last node in the pipeline
(`pipeline/graph.py`). This is the object the Streamlit report viewer
(`ui/components/report_viewer.py`) and PDF exporter
(`ui/components/pdf_generator.py`) render, and what `GraphState["report"]`
holds once a run completes.

## Where it comes from

`report_node` in `pipeline/graph.py` calls the Report Agent, which
combines every prior agent's output with three new LLM-generated
fields into one dict, returned as `data["validation_report"]`.

The Report Agent's LLM call is deliberately narrow: it only generates
the **executive summary**, **risk analysis**, and **final validation
score** — every other field is passed straight through from state
already populated by earlier agents, unchanged. The prompt explicitly
instructs it to use only the supplied information and never invent
statistics, competitors, or market data; the score must reflect that
evidence and is explicitly not a guarantee of startup success.

## Structure

| Key | Type | Source | Description |
|---|---|---|---|
| `executive_summary` | `str` | LLM | Concise startup validation summary |
| `market_analysis` | `Dict[str, Any]` | Market Analysis Agent | `market_size`, `target_audience`, `industry_trends`, `opportunities`, `market_potential` |
| `competitor_analysis` | `List[Competitor]` | Competitor Agent | Each competitor's `name`, `website`, `description`, `strengths`, `weaknesses`, `source_urls` |
| `swot_analysis` | `Dict[str, Any]` | SWOT & Risk Agent | `strengths`, `weaknesses`, `opportunities`, `threats`, `risks` |
| `risk_analysis` | `list` | LLM | Important startup risks, each with severity and mitigation |
| `mvp_recommendation` | `Dict[str, Any]` | MVP Recommendation Agent | `must_have`, `nice_to_have`, `future_features`, `prioritization_rationale` |
| `gtm_strategy` | `Dict[str, Any]` | GTM Strategy Agent | `positioning_strategy`, `pricing_ideas`, `customer_acquisition_channels`, `launch_strategy` |
| `final_validation_score` | `int` (0–100) | LLM | Overall validation score, grounded in the evidence above |
| `references` | `List[str]` | Web Search Agent | Deduplicated source URLs collected across the whole run |

## Example shape

```json
{
  "executive_summary": "...",
  "market_analysis": {
    "market_size": "...",
    "target_audience": "...",
    "industry_trends": "...",
    "opportunities": "...",
    "market_potential": "..."
  },
  "competitor_analysis": [
    {
      "name": "...",
      "website": "...",
      "description": "...",
      "strengths": ["..."],
      "weaknesses": ["..."],
      "source_urls": ["..."]
    }
  ],
  "swot_analysis": {
    "strengths": ["..."],
    "weaknesses": ["..."],
    "opportunities": ["..."],
    "threats": ["..."],
    "risks": [
      {"risk": "...", "severity": "...", "mitigation": "..."}
    ]
  },
  "risk_analysis": [
    {"risk": "...", "severity": "...", "mitigation": "..."}
  ],
  "mvp_recommendation": {
    "must_have": ["..."],
    "nice_to_have": ["..."],
    "future_features": ["..."],
    "prioritization_rationale": "..."
  },
  "gtm_strategy": {
    "positioning_strategy": "...",
    "pricing_ideas": ["..."],
    "customer_acquisition_channels": ["..."],
    "launch_strategy": ["..."]
  },
  "final_validation_score": 72,
  "references": ["https://..."]
}
```

## Related models

`state/schema.py` defines `ValidationReport`, a Pydantic model with the
same shape as this report (used for validation/typing elsewhere in the
codebase); the Report Agent itself builds and returns a plain `dict`
matching this structure rather than an instance of that model.

See [agent_roles.md](agent_roles.md#report-agent) for the Report
Agent's full input/output contract, and
[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) for how this fits into the
rest of the pipeline.
