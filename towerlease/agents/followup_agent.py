"""
Follow-up Q&A agent.

Handles follow-up questions after a negotiation brief has been generated.
Uses the existing conversation history from the session store to maintain
context continuity.

This is a simple single-turn completion -- no tool calls needed for
follow-up since the context is already in the conversation history.

Written by dkim@ as a quick addition when the PM asked "can negotiators
ask follow-up questions?" two days before the demo. It works.
"""
import os

import openai

openai.api_key = os.getenv("OPENAI_API_KEY")


_FOLLOWUP_SYSTEM_ADDENDUM = (
    "\n\nThe user is now asking a follow-up question about the negotiation "
    "brief you previously prepared. Answer based on the context already "
    "gathered. Be specific and actionable. Reference the comparable data "
    "and provider context from the original analysis when relevant."
)


def handle_followup(messages, question):
    """Process a follow-up question using existing conversation context.

    Args:
        messages: list of message dicts from the session store
        question: the user's follow-up question string

    Returns:
        tuple of (answer_text, updated_messages_list)
    """
    # Make a copy so we don't mutate the stored list directly
    # (learned this the hard way -- JIRA-1834)
    updated_messages = list(messages)

    # Inject followup context into system message if not already there
    if updated_messages and updated_messages[0]["role"] == "system":
        if "follow-up question" not in updated_messages[0]["content"]:
            updated_messages[0] = {
                "role": "system",
                "content": updated_messages[0]["content"] + _FOLLOWUP_SYSTEM_ADDENDUM,
            }

    # Add the new user question
    updated_messages.append({
        "role": "user",
        "content": question,
    })

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=updated_messages,
    )

    answer = response["choices"][0]["message"]["content"]

    # Append the assistant response to history
    updated_messages.append({
        "role": "assistant",
        "content": answer,
    })

    return answer, updated_messages
