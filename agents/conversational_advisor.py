"""
Conversational Advisor.

Provides a simple question-answering layer over the
generated startup validation report.

The advisor uses the existing validation report as
context and allows a founder to ask follow-up questions.
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from deepagents import create_deep_agent
from app.llm import get_chat_model


# =========================================================
# Conversational Advisor
# =========================================================

class ConversationalAdvisor:

    def __init__(self, agent=None, model_name=None):
        """
        Initialize the Conversational Advisor.

        Parameters
        ----------
        agent:
            Optional pre-built DeepAgent.

        model_name:
            Optional Gemini model name.
        """

        self.model_name = (
            model_name
            or os.getenv(
                "STARTUP_VALIDATOR_MODEL",
                "openai/gpt-oss-20b"
            )
        )

        self.system_prompt = self._load_prompt()

        if agent is not None:
            self.agent = agent
        else:
            self.agent = self._build_agent()

    # =====================================================
    # Prompt loading
    # =====================================================

    def _load_prompt(self):

        project_root = Path(__file__).resolve().parents[1]

        prompt_path = (
            project_root
            / "prompts"
            / "conversational_advisor.md"
        )

        if prompt_path.exists():
            return prompt_path.read_text(encoding="utf-8")

        return """
You are the AI Conversational Advisor for a startup
validation system.

Your job is to answer founder questions using the
startup validation report provided as context.

Rules:

1. Use the supplied report as the main source.
2. Do not invent facts.
3. If the report does not contain enough information,
   clearly say so.
"""

    # =====================================================
    # Build DeepAgent
    # =====================================================

    def _build_agent(self):

        model = get_chat_model(
            model_name=self.model_name,
            temperature=0.3,
            max_retries=1,
        )

        return create_deep_agent(
            model=model,
            system_prompt=self.system_prompt,
        )

    # =====================================================
    # Ask Question
    # =====================================================

    def answer_question(self, report, question):

        try:

            if not question or not question.strip():
                raise ValueError(
                    "Question cannot be empty."
                )

            report_context = (
                json.dumps(report, indent=2, default=str)
                if report
                else "No validation report has been generated yet."
            )

            user_input = f"""
Here is the startup validation report:

{report_context}

Founder Question:
{question}

Answer the founder's question using the validation report when it is
available. If no report exists yet, answer general startup questions
helpfully and clearly state when a report would be needed for a
report-specific answer.

Do not invent unsupported facts.
"""

            result = self.agent.invoke(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": user_input,
                        }
                    ]
                }
            )

            messages = result.get(
                "messages",
                []
            )

            if not messages:
                raise RuntimeError(
                    "Advisor did not return a response."
                )

            last_message = messages[-1]

            content = getattr(
                last_message,
                "content",
                None
            )

            if content is None:

                if isinstance(
                    last_message,
                    dict
                ):
                    content = last_message.get(
                        "content"
                    )

            if isinstance(content, list):

                text_parts = []

                for item in content:

                    if isinstance(item, dict):

                        text = item.get(
                            "text"
                        )

                        if text:
                            text_parts.append(
                                text
                            )

                    elif isinstance(item, str):
                        text_parts.append(item)

                content = "\n".join(
                    text_parts
                )

            if not content:
                raise RuntimeError(
                    "Advisor returned an empty response."
                )

            return {
                "status": "success",
                "answer": content,
                "message": ""
            }

        except Exception as e:

            return {
                "status": "error",
                "answer": "",
                "message": str(e)
            }


# =========================================================
# Simple Helper Function
# =========================================================

def answer_question(report, question):

    advisor = ConversationalAdvisor()

    return advisor.answer_question(
        report,
        question
    )
