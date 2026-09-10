# AI Startup Idea Validator — Project Overview

Complete technical reference for the whole codebase in one place: what
it does, how it's structured, how data flows through it, how to run
it, and the full contract for every agent.

## Table of Contents

1. [Overview](#overview)
2. [Setup](#setup)
3. [Project Structure](#project-structure)
4. [Configuration](#configuration)
5. [Architecture](#architecture)
6. [State & Shared Memory](#state--shared-memory)
7. [Agents](#agents)
8. [Tools](#tools)
9. [Orchestrator](#orchestrator)
10. [UI (Streamlit)](#ui-streamlit)
11. [Tests](#tests)
12. [Known Gaps / In-Progress Work](#known-gaps--in-progress-work)

---

## Overview

The AI Startup Idea Validator takes a 2–3 line startup idea and runs it
through a sequential multi-agent pipeline that produces a structured,
evidence-backed validation report: market analysis, competitor
intelligence, SWOT/risk assessment, MVP recommendations, go-to-market
strategy, and a final scored report. A conversational advisor layer
lets a founder ask follow-up questions against the finished report.

Every agent is a Gemini-backed [DeepAgent](https://github.com/langchain-ai/deepagents)
that returns a Pydantic-validated structured output, and every agent
follows the same calling convention:

```python
result = agent.run(shared_memory)
# result == {"status": "success" | "error", "data": {...}, "message": "..."}
```

`shared_memory` is the pipeline's single `GraphState` dict
(`state/schema.py`) — every agent reads the keys it needs from it and,
on success, the pipeline node writes the agent's `data` back into that
same state for the next agent to read.

## Setup

```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt

copy .env.example .env          # then fill in GEMINI_API_KEY
```

Required environment variable (`.env`):

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `GEMINI_API_KEY` | Yes | — | Used by every agent (`ChatGoogleGenerativeAI`) and the Orchestrator's `google.genai` client |
| `TAVILY_API_KEY` | No | — | Reserved for a future Tavily search integration; not currently wired to any tool |
| `SEARCH_ENGINE` | No | `duckduckgo` | Documented but web search is currently hardcoded to DuckDuckGo (`ddgs`) |
| `MAX_RESULTS` | No | `5` | Max results the fallback search tool returns |
| `LOG_LEVEL` | No | `INFO` | — |
| `STARTUP_VALIDATOR_MODEL` | No | `gemini-3.6-flash` | Gemini model used by every agent — read directly via `os.getenv`, not part of `Settings` |

Run the full pipeline from the CLI:

```bash
python -m app.main "An AI platform that helps students prep for interviews"
```

Run the Streamlit UI:

```bash
streamlit run ui/streamlit_app.py
```

## Project Structure

```text
ai-startup-validator/
├── app/                  Entry point + orchestration
│   ├── main.py           CLI entry point
│   ├── config.py         Settings (pydantic-settings)
│   └── orchestrator.py   Orchestrator class
├── agents/                One module per pipeline agent
├── tools/                 Shared tools (web search, planning, file I/O)
├── state/                 Shared state schema + SharedMemory model
├── prompts/               System prompt .md files, one per agent
├── pipeline/              LangGraph workflow (graph.py) + context_passer.py
├── ui/                    Streamlit app + page components
├── reports/generated/     Output reports land here
├── tests/                 Per-agent tests + one E2E test
└── docs/                  This documentation + diagrams
```

## Configuration

`app/config.py` defines a `pydantic-settings` `Settings` class loaded
from `.env`. Only `GEMINI_API_KEY` is required; everything else has a
default. Agents themselves don't import `Settings` — they read
`GEMINI_API_KEY` and `STARTUP_VALIDATOR_MODEL` directly via
`os.getenv`/`os.environ`, so `Settings` is currently only consumed by
`app/orchestrator.py`.

## Architecture

```
Startup Idea
    │
    ▼
Web Search Agent  ──────▶  search_results, references
    │
    ▼
Market Analysis Agent  ─▶  market_analysis
    │
    ▼
Competitor Agent  ──────▶  competitor_analysis, competitors
    │
    ▼
SWOT & Risk Agent  ─────▶  swot_analysis
    │
    ▼
MVP Recommendation Agent ▶ mvp_recommendation
    │
    ▼
GTM Strategy Agent  ────▶  gtm_strategy
    │
    ▼
Report Agent  ──────────▶  report (final validation report)
```

This is a strictly **sequential LangGraph** (`pipeline/graph.py`) — no
branching, no parallelism. Every node:

1. Reads what it needs from the shared `GraphState`.
2. Runs its agent.
3. On success, writes its output back into `GraphState`.
4. On failure (non-`"success"` status or a raised exception),
   `record_error()` appends to `state["errors"]` and sets
   `state["execution_status"] = "failed"` — but **execution continues
   to the next node regardless**. There are no conditional edges that
   stop the graph early, so a single agent failing does not prevent
   the rest of the pipeline (including the final report) from running
   with whatever data is available.

`app/orchestrator.py`'s `Orchestrator` class wraps this graph together
with idea extraction (via a raw `google.genai` client call, independent
of the LangGraph agents) and a simple execution-plan tracker
(`tools/planning_tool.py`) that mirrors each pipeline step's status for
reporting purposes.

## State & Shared Memory

Two related but distinct state representations exist in this codebase:

- **`state/schema.py` → `GraphState`** (a `TypedDict`) is the single
  canonical state object that actually flows through
  `pipeline/graph.py`. This is what every agent node reads from and
  writes to during a real run.
- **`state/memory.py` → `SharedMemory`** (a Pydantic `BaseModel`) is a
  more strictly typed shared-memory model used by
  `pipeline/context_passer.py`'s `update_memory()`/`get_memory()`
  helpers. Its fields are typed loosely (e.g. `search_results:
  Union[str, List[Any]]`) to match what agents actually return in
  practice (plain text/dicts, not validated model instances), avoiding
  Pydantic serialization warnings on real runs.

Key Pydantic models (`state/schema.py`):

| Model | Purpose |
|---|---|
| `StartupIdea` | Raw founder input: idea, target audience, industry, constraints |
| `IdeaExtraction` | LLM-extracted problem/solution/value proposition/keywords |
| `SearchResult` | `{title, url, snippet}` |
| `Competitor` | `{name, website, description, strengths, weaknesses, source_urls}` |
| `CompetitorAgentOutput` | `{startup_idea, competitors}` |
| `ValidationReport` | Full final-report shape (executive summary, all agent outputs, references) |
| `GraphState` | The pipeline's actual shared state (see above) |

## Agents

Every agent in the pipeline, in execution order. Each follows the same
structure — **Purpose**, **Input**, **Output**, **Model / Tools**.

All agents share one calling convention:

```python
result = agent.run(shared_memory)
# result == {"status": "success" | "error", "data": {...}, "message": "..."}
```

### Web Search Agent

**Module:** `agents/web_search_agent.py` · **Prompt:** `prompts/web_search_agent.md`

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

### Market Analysis Agent

**Module:** `agents/market_analysis_agent.py` · **Prompt:** `prompts/market_analysis_agent.md`

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

### Competitor Agent

**Module:** `agents/competitor_agent.py` · **Prompt:** `prompts/competitor_agent.md`

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

Each `Competitor` (`state/schema.py`):

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

### SWOT & Risk Agent

**Module:** `agents/swot_risk_agent.py` · **Prompt:** `prompts/swot_risk_agent.md`

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

### MVP Recommendation Agent

**Module:** `agents/mvp_recommendation_agent.py` · **Prompt:** `prompts/mvp_agent.md`

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

### GTM Strategy Agent

**Module:** `agents/gtm_strategy_agent.py` · **Prompt:** `prompts/gtm_agent.md`

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

### Report Agent

**Module:** `agents/report_agent.py` · **Prompt:** `prompts/report_agent.md`

**Purpose**
The pipeline's final step. Combines every previous agent's output into
one founder-facing validation report with an executive summary and an
overall score. Never invents facts, statistics, or competitors beyond
what earlier agents already produced.

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

### Conversational Advisor

**Module:** `agents/conversational_advisor.py`

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

Every agent except the Conversational Advisor is instantiated once in
`pipeline/graph.py` and reused across the whole process lifetime. All
of them default to `gemini-3.6-flash` and explicitly set
`max_retries=1` on `ChatGoogleGenerativeAI` — the library's own default
of 6 would silently allow up to 7 real API calls per logical request,
which badly multiplies quota usage on 429 rate-limit responses.

## Tools

| Tool | Module | Purpose |
|---|---|---|
| `execute_web_search` / `WebSearchTool` | `tools/web_search_tool.py` | DuckDuckGo search (`ddgs`), used directly by DeepAgents and as a fallback if the agent never calls the tool itself |
| `create_execution_plan` | `tools/planning_tool.py` | Builds an ordered, trackable step list for the Orchestrator (`pending` → `completed`/`failed`) |
| `file_tools.py` | `tools/file_tools.py` | File I/O helpers (report saving) |
| `retrieval_utils.py` | `tools/retrieval_utils.py` | Retrieval helper utilities |

## Orchestrator

`app/orchestrator.py`'s `Orchestrator` class is the single entry point
used by `app/main.py` and (indirectly) the Streamlit UI:

1. `receive_request(idea, ...)` — stores a `StartupIdea` in
   `SharedMemory`.
2. `extract_startup_idea()` — calls Gemini directly (via
   `google.genai`, not a DeepAgent) to produce structured
   `IdeaExtraction`. Failures here are captured in
   `self._idea_extraction_error` rather than raised, so a failed
   extraction doesn't silently disappear when the final output is
   built.
3. `execute_pipeline()` — runs the compiled LangGraph
   (`pipeline.graph.graph`).
4. `get_final_output()` — returns the execution plan with each step's
   real status filled in, rather than a fresh all-`"pending"` plan, so
   completed runs are reported accurately.

`TASK_TO_AGENT_NAME` maps each planning-tool task name to the exact
agent-name prefix that `pipeline/graph.py`'s `record_error()` uses, so
a failure can be attributed back to the specific agent that produced
it instead of being reported generically.

## UI (Streamlit)

`ui/streamlit_app.py` is the entry point (`streamlit run
ui/streamlit_app.py`), wiring together:

| Component | Module | Purpose |
|---|---|---|
| Idea input | `ui/components/idea_input.py` | Startup idea submission form |
| Processing page | `ui/components/processing_page.py` | Real-time pipeline progress display |
| Report viewer | `ui/components/report_viewer.py` | Renders the final validation report |
| Advisor page | `ui/components/advisor_page.py` | Conversational Q&A over the finished report |
| Chat component | `ui/components/chat_component.py` | Global chat widget |
| PDF generator | `ui/components/pdf_generator.py` | Exports the validation report as PDF |

Styling is a dark black/lavender theme applied via injected CSS in
`streamlit_app.py`.

## Tests

| Test file | Covers |
|---|---|
| `tests/test_web_search_agent.py` | Web Search Agent |
| `tests/test_market_agent.py` | Market Analysis Agent |
| `tests/test_competitor_agent.py` | Competitor Agent |
| `tests/test_swot_agent.py` | SWOT & Risk Agent |
| `tests/test_mvp_agent.py` | MVP Recommendation Agent |
| `tests/test_pipeline_e2e.py` | Full pipeline, end-to-end, with mocked agent responses |
| `tests/sample_ideas.json` | Shared sample startup ideas used across tests |
| `test_graph.py` (repo root) | `pipeline/graph.py` |

No dedicated test file exists yet for the GTM Strategy Agent, Report
Agent, or Conversational Advisor.

## Known Gaps / In-Progress Work

- **Conversational Advisor** is implemented (`agents/conversational_advisor.py`,
  `ui/components/advisor_page.py`) but its PR (#7,
  `feature/conversational-advisor`) is closed, not merged — it is not
  part of the current `main` pipeline.
- **`docs/final_report.md`** is currently just a title placeholder; the
  actual report schema is documented under the Report Agent section
  above in the meantime.
- **`TAVILY_API_KEY`/`SEARCH_ENGINE`** are defined in `.env.example`
  and `app/config.py` but not actually wired to any tool — web search
  is hardcoded to DuckDuckGo via `ddgs`.
- The graph has **no failure-stopping logic** — every node runs even
  after an earlier one fails, so a broken web search can still result
  in a "successful" (but evidence-poor) final report. Errors are only
  visible via `state["errors"]`.
- **Database, observability, and guardrails** modules (`database/`,
  `observability/`, `guardrails/`) plus the matching `pipeline/graph.py`
  wiring exist on branch `feature/pipeline-db-observability` (pushed,
  not merged/PR'd yet). They add per-agent execution metrics,
  input/output validation (including secret-leak scanning), and a
  SQLAlchemy-backed persistence layer for future chat history.
- **`app/llm.py`** is missing from `main` even though `agents/*.py` and
  a newly added `api/main.py` already import it — `main` currently
  fails to import at all until this is added.
- **A real Gemini API key was found hardcoded in `.env.example`**,
  exposed on this public GitHub repo since an early commit. It must be
  rotated immediately; do not reuse that key value anywhere.
