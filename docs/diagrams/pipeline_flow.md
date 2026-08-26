# Pipeline Flow (pipeline/graph.py)

Sequential LangGraph pipeline. Each node runs one agent, reads the shared
`GraphState`, and writes its result back into that same state before the
next node runs.

![Pipeline Flow](pipeline_flow.png)

```mermaid
%%{init: {'flowchart': {'nodeSpacing': 45, 'rankSpacing': 70, 'curve': 'basis'}, 'themeVariables': {'fontSize': '20px'}}}%%
flowchart TD
    IN["Startup Idea\n(state.startup_idea)"] --> START(("START"))
    START --> WS["Web Search Agent"]

    subgraph PIPELINE [" "]
        direction TD
        WS -->|"search_results, references"| MA["Market Analysis Agent"]
        MA -->|"market_analysis"| CA["Competitor Agent"]
        CA -->|"competitor_analysis, competitors"| SW["SWOT &amp; Risk Agent"]
        SW -->|"swot_analysis"| MVP["MVP Recommendation Agent"]
        MVP -->|"mvp_recommendation"| GTM["GTM Strategy Agent"]
        GTM -->|"gtm_strategy"| RA["Report Agent"]
    end

    RA -->|"report"| END_(("END"))
    END_ --> OUT["Final GraphState\n(report, errors, execution_status)"]

    PIPELINE -.->|"on failure"| ERR[("state.errors[]\n(run continues)")]

    classDef pink fill:#fdf2f8,stroke:#ec4899,stroke-width:2px,color:#1b1d22;
    classDef teal fill:#f0fdfa,stroke:#14b8a6,stroke-width:2px,color:#1b1d22;
    classDef orange fill:#fff7ed,stroke:#f97316,stroke-width:2px,color:#1b1d22;
    classDef blue fill:#eff6ff,stroke:#3b82f6,stroke-width:2px,color:#1b1d22;
    classDef green fill:#f0fdf4,stroke:#22c55e,stroke-width:2px,color:#1b1d22;
    classDef purple fill:#f5f3ff,stroke:#8b5cf6,stroke-width:2px,color:#1b1d22;
    classDef amber fill:#fefce8,stroke:#eab308,stroke-width:2px,color:#1b1d22;
    classDef cyan fill:#ecfeff,stroke:#06b6d4,stroke-width:2px,color:#1b1d22;
    classDef neutral fill:#f8fafc,stroke:#64748b,stroke-width:2px,color:#1b1d22;
    classDef danger fill:#fef2f2,stroke:#ef4444,stroke-width:2px,color:#7f1d1d;

    class IN pink;
    class START neutral;
    class WS teal;
    class MA orange;
    class CA blue;
    class SW green;
    class MVP purple;
    class GTM amber;
    class RA cyan;
    class END_ neutral;
    class OUT neutral;
    class ERR danger;

    style PIPELINE fill:none,stroke:#cbd5e1,stroke-width:1px,stroke-dasharray: 4 4
```

## Notes

- Nodes run strictly in order: `web_search` &rarr; `market_analysis` &rarr;
  `competitor_analysis` &rarr; `swot_analysis` &rarr; `mvp_recommendation`
  &rarr; `gtm_strategy` &rarr; `report_generation`.
- Every node writes its output into the same shared `GraphState` object,
  which is what carries context forward to the next agent &mdash; agents
  never call each other directly.
- Each node's agent instance (`web_search_agent`, `market_agent`,
  `competitor_agent`, `swot_agent`, `mvp_agent`, `gtm_agent`,
  `report_agent`) is created once at module load and reused for every run.
- If a node's agent call fails (returns a non-`"success"` status, or raises),
  `record_error()` appends the failure to `state["errors"]` and sets
  `state["execution_status"] = "failed"` &mdash; shown above as the dashed
  path every node can take.
- Critically, the graph has **no conditional edges to stop on failure**:
  even after an error is recorded, execution continues on to the next
  node regardless, all the way to `report_generation`.
