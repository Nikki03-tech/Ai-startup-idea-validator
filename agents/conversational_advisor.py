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
from langchain_google_genai import ChatGoogleGenerativeAI


PROMPT_PATH = os.path.join(os.path.dirname(__file__), "../prompts/conversational_advisor.md")
if os.path.exists(PROMPT_PATH):
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        ADVISOR_SYSTEM_PROMPT = f.read()
else:
    ADVISOR_SYSTEM_PROMPT = (
        "You are the AI Conversational Advisor for a startup validation "
        "system. Answer founder questions using the supplied validation "
        "report as context. Do not invent facts."
    )


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
                "gemini-2.5-flash"
            )
        )

        self.system_prompt = ADVISOR_SYSTEM_PROMPT

        if agent is not None:
            self.agent = agent
        else:
            self.agent = self._build_agent()

    # =====================================================
    # Build DeepAgent
    # =====================================================

    def _build_agent(self):

        api_key = (
            os.getenv("GOOGLE_API_KEY")
            or os.getenv("GEMINI_API_KEY")
        )

        if not api_key:
            raise RuntimeError(
                "Gemini API key not found. "
                "Set GOOGLE_API_KEY or GEMINI_API_KEY."
            )

        model = ChatGoogleGenerativeAI(
            model=self.model_name,
            google_api_key=api_key,
            temperature=0.3,
            max_retries=2,
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

            if not report:
                raise ValueError(
                    "Validation report cannot be empty."
                )

            if not question or not question.strip():
                raise ValueError(
                    "Question cannot be empty."
                )

            user_input = f"""
Here is the startup validation report:

{json.dumps(report, indent=2, default=str)}

Founder Question:
{question}

Answer the founder's question using the validation
report as the primary source.

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
                "status": "failed",
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