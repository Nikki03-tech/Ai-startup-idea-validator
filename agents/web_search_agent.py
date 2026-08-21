import os
import re
from typing import Dict, Any

from dotenv import load_dotenv

load_dotenv()

os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]

from deepagents import create_deep_agent
from langchain_core.messages import ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from tools.web_search_tool import execute_web_search, WebSearchTool


PROMPT_PATH = os.path.join(
    os.path.dirname(__file__),
    "../prompts/web_search_agent.md"
)

if os.path.exists(PROMPT_PATH):
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        WEB_SEARCH_PROMPT = f.read()
else:
    WEB_SEARCH_PROMPT = (
        "You are a Web Search Agent. Gather facts and competitors "
        "for the given startup idea."
    )


def _extract_text(content) -> str:
    """
    Normalize a LangChain AIMessage.content value into plain text.

    Older Gemini models (e.g. gemini-2.5-flash) return .content as a
    plain string. Newer, agentic models (e.g. gemini-3.6-flash) can
    return .content as a list of content blocks instead - typically a
    {"type": "text", "text": "..."} block plus non-text metadata such
    as an "extras": {"signature": "..."} thought-signature used to
    keep multi-step tool-calling turns coherent. If that list were
    stringified directly (e.g. via an f-string), the raw block dicts -
    including the long base64 signature - would get dumped into plain
    text and pollute shared_memory["search_results"], which every
    downstream agent (market analysis, competitor, SWOT, report)
    reads as evidence.

    This only normalizes the final AIMessage text used to build the
    "Summary:" tail of search_summary. It does not touch tool_outputs
    (ToolMessage.content), which always come from our own
    execute_web_search tool and are already plain strings - so
    _extract_urls() and the rest of the URL/reference pipeline below
    are unaffected.
    """

    if content is None:
        return ""

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict):
                text = block.get("text")
                if text:
                    parts.append(text)
        return "\n".join(parts)

    return str(content)


class WebSearchAgent:

    def __init__(self, model_name: str = None):

        model_name = model_name or os.getenv(
            "STARTUP_VALIDATOR_MODEL",
            "gemini-2.5-flash"
        )

        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=os.environ.get("GEMINI_API_KEY"),
            # See competitor_agent.py for why this is set explicitly:
            # the library's default (max_retries=6) silently allows up
            # to 7 real API calls per logical request, which badly
            # multiplies quota usage on 429s.
            max_retries=1,
        )

        self.agent = create_deep_agent(
            model=llm,
            tools=[execute_web_search],
            system_prompt=WEB_SEARCH_PROMPT
        )

        self.fallback_tool = WebSearchTool()

    def _extract_urls(self, text: str):
        """
        Extract actual URLs from search tool output.
        """

        if not text:
            return []

        urls = re.findall(
            r"URL:\s*(https?://\S+)",
            text
        )

        return list(dict.fromkeys(urls))

    def run(self, shared_memory: Dict[str, Any]) -> Dict[str, Any]:

        try:

            startup_idea = shared_memory.get(
                "startup_idea",
                ""
            )

            if not startup_idea:

                return {
                    "status": "error",
                    "data": {},
                    "message": "Missing 'startup_idea' in state."
                }

            prompt = (
                f"Conduct web search research for the startup idea: "
                f"'{startup_idea}'. "
                "Call execute_web_search now - do not write a todo list "
                "or delegate this task. Your final answer must contain "
                "the actual findings, not a status update."
            )

            response = self.agent.invoke(
                {
                    "messages": [
                        ("user", prompt)
                    ]
                }
            )

            messages = response.get(
                "messages",
                []
            )

            final_message = (
                _extract_text(messages[-1].content)
                if messages
                else ""
            )

            # ---------------------------------------------------------
            # Collect actual search tool outputs
            # ---------------------------------------------------------

            tool_outputs = [
                m.content
                for m in messages
                if isinstance(m, ToolMessage)
                and m.content
            ]

            # ---------------------------------------------------------
            # Extract real URLs from DeepAgent search results
            # ---------------------------------------------------------

            references = []

            for output in tool_outputs:

                if isinstance(output, str):

                    references.extend(
                        self._extract_urls(output)
                    )

            references = list(
                dict.fromkeys(references)
            )

            # ---------------------------------------------------------
            # Build search summary
            # ---------------------------------------------------------

            if tool_outputs:

                search_summary = "\n\n".join(
                    tool_outputs
                )

                if final_message:

                    search_summary += (
                        f"\n\nSummary: {final_message}"
                    )

                tool_was_used = True

            else:

                search_summary = final_message
                tool_was_used = False

            # ---------------------------------------------------------
            # Fallback search
            # ---------------------------------------------------------

            if not tool_was_used:

                raw_refs = self.fallback_tool.search(
                    startup_idea
                )

                references = [
                    r["url"]
                    for r in raw_refs
                    if isinstance(r, dict)
                    and r.get("url")
                ]

                fallback_snippets = []

                for result in raw_refs:

                    if isinstance(result, dict):

                        title = result.get(
                            "title",
                            ""
                        )

                        snippet = result.get(
                            "snippet",
                            ""
                        )

                        url = result.get(
                            "url",
                            ""
                        )

                        fallback_snippets.append(
                            f"Title: {title}\n"
                            f"URL: {url}\n"
                            f"Snippet: {snippet}"
                        )

                fallback_text = "\n\n".join(
                    fallback_snippets
                )

                if search_summary:

                    search_summary = (
                        f"{search_summary}\n\n"
                        f"{fallback_text}"
                    )

                else:

                    search_summary = fallback_text

            # ---------------------------------------------------------
            # Final deduplication
            # ---------------------------------------------------------

            references = list(
                dict.fromkeys(
                    url for url in references
                    if url
                )
            )

            return {
                "status": "success",

                "data": {
                    "search_results": search_summary,
                    "references": references
                },

                "message": (
                    "Web search agent completed successfully."
                )
            }

        except Exception as e:

            return {
                "status": "error",
                "data": {},
                "message": (
                    f"WebSearchAgent error: {str(e)}"
                )
            }
