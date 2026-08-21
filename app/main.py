"""Main application entry point (FastAPI / CLI) for AI Startup Validator.

Triggers the multi-agent validation pipeline and orchestrates workflow execution.

This is a minimal CLI entrypoint (no new dependencies added). It goes
through the Orchestrator, which now delegates real execution to the
LangGraph pipeline in pipeline/graph.py.

Usage:
    python -m app.main "An AI platform that helps students prep for interviews"
"""

import json
import sys

from app.orchestrator import Orchestrator


def run(idea: str) -> dict:
    """Run the full validation pipeline for a single startup idea."""

    orchestrator = Orchestrator()
    orchestrator.receive_request(idea)
    orchestrator.execute_pipeline()

    return orchestrator.get_final_output()


def main() -> None:
    if len(sys.argv) < 2:
        print('Usage: python -m app.main "<startup idea>"')
        sys.exit(1)

    idea = " ".join(sys.argv[1:])
    output = run(idea)

    print(json.dumps(output, indent=2, default=str))


if __name__ == "__main__":
    main()
