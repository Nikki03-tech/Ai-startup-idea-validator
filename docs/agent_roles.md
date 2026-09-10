# Agent Roles & Responsibilities

Reference documentation for every agent in the AI Startup Idea Validator
pipeline. Each entry follows the same structure — **Purpose**, **Input**,
**Output**, **Model / Tools** — so any agent's contract can be looked up
independently of the others.

All agents share one calling convention:

```python
result = agent.run(shared_memory)
# result == {"status": "success" | "error", "data": {...}, "message": "..."}
```

`shared_memory` is the pipeline's single `GraphState` dict
([state/schema.py](../state/schema.py)) — every agent reads the keys it
needs from it and, on success, the pipeline node writes the agent's
`data` back into that same state for the next agent to read. See
[docs/diagrams/pipeline_flow.md](diagrams/pipeline_flow.md) for the full
execution graph.

---

## Web Search Agent

**Module:** [agents/web_search_agent.py](../agents/web_search_agent.py) · **Prompt:** [prompts/web_search_agent.md](../prompts/web_search_agent.md)

**Purpose**
Runs the first research step of the pipeline. Gathers real, citable
facts about the startup idea's market and landscape via live web
search, so every downstream agent has grounded evidence instead of
relying on the LLM's own knowledge.

**Input** (from `shared_memory`)

| Key | Type | Required |
|---|---|---|
| `startup_idea` | `str` | Yes |

**Output** (`data`)

| Key | Type | Description |
|---|---|---|
| `search_results` | `str` | Concatenated raw search snippets plus an LLM summary |
| `references` | `List[str]` | Deduplicated source URLs |

**Model / Tools:** `gemini-3.6-flash` (via `STARTUP_VALIDATOR_MODEL`) as a DeepAgent with the `execute_web_search` tool (DuckDuckGo via `ddgs`). Falls back to a direct `WebSearchTool().search()` call if the agent never invokes the tool itself.

---

## Market Analysis Agent

**Module:** [agents/market_analysis_agent.py](../agents/market_analysis_agent.py) · **Prompt:** [prompts/market_analysis_agent.md](../prompts/market_analysis_agent.md)

**Purpose**
Turns raw search evidence into a structured read on market opportunity:
size, target audience, trends, and overall potential.

**Input**

| Key | Type | Required |
|---|---|---|
| `startup_idea` | `str` | Yes |
| `search_results` | `str` | Recommended (used as evidence) |

**Output** (`data.market_analysis`)

| Key | Type |
|---|---|
| `market_size` | `str` |
| `target_audience` | `str` |
| `industry_trends` | `str` |
| `opportunities` | `str` |
| `market_potential` | `str` |

**Model / Tools:** `gemini-3.6-flash`, structured output via the `MarketAnalysis` Pydantic model.

---

## Competitor Agent

**Module:** [agents/competitor_agent.py](../agents/competitor_agent.py) · **Prompt:** [prompts/competitor_agent.md](../prompts/competitor_agent.md)

**Purpose**
Discovers real direct and indirect competitors and compares them
against the startup idea. Reuses the Web Search Agent's findings as a
starting point, then issues its own follow-up searches for
competitor-specific names, products, and companies.

**Input**

| Key | Type | Required |
|---|---|---|
| `startup_idea` | `str` | Yes |
| `search_results` | `str` | Optional (used as a starting point) |
| `references` | `List[str]` | Optional |

**Output** (`data`)

| Key | Type | Description |
|---|---|---|
| `startup_idea` | `str` | Echoed back for downstream context |
| `competitors` | `List[Competitor]` | See below |

Each `Competitor` ([state/schema.py](../state/schema.py)):

| Field | Type |
|---|---|
| `name` | `str` |
| `website` | `str` |
| `description` | `str` |
| `strengths` | `List[str]` |
| `weaknesses` | `List[str]` |
| `source_urls` | `List[str]` |

Fields the source evidence doesn't support are left empty rather than
guessed — enforced by the system prompt.

**Model / Tools:** `gemini-3.6-flash` as a DeepAgent with the `execute_web_search` tool, structured output via the `CompetitorAnalysis` Pydantic model.

---

## SWOT & Risk Agent

**Module:** [agents/swot_risk_agent.py](../agents/swot_risk_agent.py) · **Prompt:** [prompts/swot_risk_agent.md](../prompts/swot_risk_agent.md)

**Purpose**
Synthesizes the market and competitor findings into a SWOT breakdown
plus an explicit, ranked risk register with mitigations.

**Input**

| Key | Type | Required |
|---|---|---|
| `market_analysis` | `Dict[str, Any]` | Yes |
| `competitors` | `List[Any]` | Yes |

**Output** (`data.swot_analysis`)

| Key | Type |
|---|---|
| `strengths` | `List[str]` |
| `weaknesses` | `List[str]` |
| `opportunities` | `List[str]` |
| `threats` | `List[str]` |
| `risks` | `List[Risk]` — each `{risk, severity, mitigation}` |

**Model / Tools:** `gemini-3.6-flash`, structured output via the `SWOTAnalysis` Pydantic model.

---

## MVP Recommendation Agent

**Module:** [agents/mvp_recommendation_agent.py](../agents/mvp_recommendation_agent.py) · **Prompt:** [prompts/mvp_agent.md](../prompts/mvp_agent.md)

**Purpose**
Converts the SWOT/risk findings into a prioritized feature set for a
first shippable product, so the founder knows what to build first.

**Input**

| Key | Type | Required |
|---|---|---|
| `swot_analysis` | `Dict[str, Any]` | Yes |

**Output** (`data.mvp_recommendation`)

| Key | Type |
|---|---|
| `must_have` | `List[MVPFeature]` |
| `nice_to_have` | `List[MVPFeature]` |
| `future_features` | `List[MVPFeature]` |
| `prioritization_rationale` | `str` |

**Model / Tools:** `gemini-3.6-flash`, structured output via Pydantic models.

---

## GTM Strategy Agent

**Module:** [agents/gtm_strategy_agent.py](../agents/gtm_strategy_agent.py) · **Prompt:** [prompts/gtm_agent.md](../prompts/gtm_agent.md)

**Purpose**
Produces a practical go-to-market plan — positioning, pricing,
acquisition channels, and launch sequencing — using every prior
agent's output as context.

**Input**

| Key | Type | Required |
|---|---|---|
| `startup_idea` | `str` | Yes |
| `market_analysis` | `Dict[str, Any]` | Yes |
| `competitor_analysis` / `competitors` | `Any` | Yes |
| `swot_analysis` | `Dict[str, Any]` | Yes |
| `mvp_recommendation` | `Dict[str, Any]` | Yes |

**Output** (`data.gtm_strategy`)

| Key | Type |
|---|---|
| `positioning_strategy` | `str` |
| `pricing_ideas` | `List[PricingIdea]` |
| `customer_acquisition_channels` | `List[AcquisitionChannel]` |
| `launch_strategy` | `List[str]` |

**Model / Tools:** `gemini-3.6-flash`, structured output via the `GTMStrategy` Pydantic model.

---

## Report Agent

**Module:** [agents/report_agent.py](../agents/report_agent.py) · **Prompt:** [prompts/report_agent.md](../prompts/report_agent.md)

**Purpose**
The pipeline's final step. Combines every previous agent's output into
one founder-facing validation report with an executive summary and an
overall score. Never invents facts, statistics, or competitors beyond
what earlier agents already produced. See
[docs/final_report.md](final_report.md) for the full report structure.

**Input**

| Key | Type | Required |
|---|---|---|
| `startup_idea` | `str` | Yes |
| `market_analysis` | `Dict[str, Any]` | Yes |
| `competitors` | `List[Any]` | Yes |
| `swot_analysis` | `Dict[str, Any]` | Yes |
| `mvp_recommendation` | `Dict[str, Any]` | Yes |
| `gtm_strategy` | `Dict[str, Any]` | Yes |

**Output** (`data.validation_report`) — the LLM only generates the three
starred fields; every other field is passed through unchanged from the
state each upstream agent already populated:

| Key | Type | Source |
|---|---|---|
| `executive_summary` ★ | `str` | LLM |
| `market_analysis` | `Dict[str, Any]` | Market Analysis Agent |
| `competitor_analysis` | `List[Any]` | Competitor Agent |
| `swot_analysis` | `Dict[str, Any]` | SWOT & Risk Agent |
| `risk_analysis` ★ | `list` | LLM |
| `mvp_recommendation` | `Dict[str, Any]` | MVP Recommendation Agent |
| `gtm_strategy` | `Dict[str, Any]` | GTM Strategy Agent |
| `final_validation_score` ★ | `int` (0–100) | LLM |
| `references` | `List[str]` | Web Search Agent |

The LLM is instructed to use only the supplied information and never
invent statistics, competitors, or market data; the score must reflect
that evidence and is explicitly not a guarantee of startup success.

**Model / Tools:** `gemini-3.6-flash` (`temperature=0.2`), structured output via the `ReportAssessment` Pydantic model (covers only the ★ fields above — the rest are assembled in code).

---

## Conversational Advisor

**Module:** [agents/conversational_advisor.py](../agents/conversational_advisor.py)

**Purpose**
A post-pipeline question-answering layer. Once a validation report
exists, the founder can ask follow-up questions and the advisor
answers using the report as context — it does not re-run research.

**Input**

| Key | Type | Required |
|---|---|---|
| Generated validation report | `Dict[str, Any]` | Yes |
| Founder's follow-up question | `str` | Yes |

**Output:** A conversational answer grounded in the existing report.

**Model / Tools:** `gemini-3.6-flash` (via `STARTUP_VALIDATOR_MODEL`), no external tools — it reasons only over the report already produced.

**Status:** Not yet merged to `main` (see closed PR #7,
`feature/conversational-advisor`).

---

## Shared Tools

| Tool | Module | Used by |
|---|---|---|
| `execute_web_search` | [tools/web_search_tool.py](../tools/web_search_tool.py) | Web Search Agent, Competitor Agent |
| `create_execution_plan` | [tools/planning_tool.py](../tools/planning_tool.py) | Orchestrator (`app/orchestrator.py`) |

## Orchestration

`app/orchestrator.py`'s `Orchestrator` class wraps idea extraction, the
`create_execution_plan` task list, and the compiled LangGraph
(`pipeline/graph.py`) into one entry point. It also maps each planning
task name to the agent-name prefix `pipeline/graph.py` uses when
recording a failure, so a failed step can be attributed back to the
specific agent that produced it.
