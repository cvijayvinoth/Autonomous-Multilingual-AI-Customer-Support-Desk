"""Multi-Agent Support Desk Team Orchestration with AutoGen v0.4+ and Multilingual Support."""

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient

from tools.kb_tool import search_kb
from tools.db_tool import log_ticket_to_db


def build_support_team(model_client: OpenAIChatCompletionClient) -> RoundRobinGroupChat:
    # 1. Customer Query Agent
    query_agent = AssistantAgent(
        name="Customer_Query_Agent",
        model_client=model_client,
        system_message=(
            "You are a Customer Query Agent. Analyze the incoming customer message and any prior thread context. "
            "Output strictly in this format:\n"
            "- Detected_Language: [e.g., English, Tamil, Hindi, Spanish, French]\n"
            "- Category: [Shipping / Refund / Billing / Account / Product / Other]\n"
            "- Urgency: [Low / Medium / High]\n"
            "- Sentiment: [Positive / Neutral / Frustrated / Angry]\n"
            "- English_Summary: [One sentence in English summarizing the customer's latest request for knowledge search]"
        ),
    )

    # 2. Knowledge Base Agent
    knowledge_agent = AssistantAgent(
        name="Knowledge_Base_Agent",
        model_client=model_client,
        tools=[search_kb],
        reflect_on_tool_use=True,
        system_message=(
            "You are a Knowledge Base Agent. Call the search_kb tool using English keywords from "
            "the English_Summary and Category. Present the retrieved excerpts and cite their source files. "
            "If search_kb returns NO_MATCH, clearly state that no company policy was found."
        ),
    )

    # 3. Resolution Agent
    resolution_agent = AssistantAgent(
        name="Resolution_Agent",
        model_client=model_client,
        system_message=(
            "You are an empathetic Resolution Agent. Write a courteous, reassuring customer reply based "
            "ONLY on the facts retrieved by the Knowledge_Base_Agent and mindful of previous thread messages.\n"
            "- LANGUAGE REQUIREMENT: Write the customer reply in the exact 'Detected_Language' identified "
            "by the Customer_Query_Agent.\n"
            "- TONE: Always use warm, reassuring, and professional phrasing. Acknowledge customer feelings directly.\n"
            "- ZERO HALLUCINATION: If no matching documents were found or search returned NO_MATCH, state honestly "
            "that our standard policies do not cover this specific case and a senior specialist is reviewing it.\n"
            "- Never invent refund windows or warranty policies.\n"
            "At the end of your reply, add: 'Confidence: [High / Low]'"
        ),
    )

    # 4. Log Agent
    log_agent = AssistantAgent(
        name="Log_Agent",
        model_client=model_client,
        tools=[log_ticket_to_db],
        reflect_on_tool_use=True,
        system_message=(
            "You are a Log Agent. Determine the escalation status and persist the ticket via log_ticket_to_db.\n"
            "Escalate to 'Escalated' if ANY condition holds:\n"
            "  1. Urgency is High\n"
            "  2. Customer Sentiment is Angry\n"
            "  3. Knowledge Agent found no matching document\n"
            "  4. Issue involves fraud, billing disputes, or legal threats\n"
            "  5. Resolution Agent confidence is Low\n"
            "Otherwise, set status to 'Resolved'.\n"
            "CRITICAL:\n"
            "- Extract 'Customer Email' from task prompt and pass to customer_email parameter.\n"
            "- If an 'Existing Ticket ID' (e.g., TKT-1234) is present in the task prompt, pass it to existing_ticket_id.\n"
            "Always conclude your final reply with the word 'LOGGED'."
        ),
    )

    termination = TextMentionTermination("LOGGED") | MaxMessageTermination(8)

    team = RoundRobinGroupChat(
        participants=[query_agent, knowledge_agent, resolution_agent, log_agent],
        termination_condition=termination,
    )

    return team