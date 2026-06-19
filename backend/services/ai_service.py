import os
import logging
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

logger = logging.getLogger(__name__)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def ask_ai(prompt: str, temperature: float = 0.7, max_tokens: int = 1500) -> str:
    """
    Send a prompt to the Groq AI API with robust error handling and fallback.
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=0.9,
            frequency_penalty=0.2,
            presence_penalty=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"AI service error: {str(e)}")
        return FALLBACK_RESPONSE


SYSTEM_PROMPT = """You are an elite AI Personal CFO — a warm, intelligent, and highly experienced financial advisor who speaks with the clarity of a top-tier wealth manager and the conversational ease of a trusted friend.

YOUR PERSONALITY:
- You are sharp, thoughtful, and genuinely care about the user's financial well-being.
- You speak naturally and confidently, never robotic.
- You adapt your tone to the question: casual for simple questions, detailed for complex analysis.
- You are honest about risks and never sugarcoat bad financial situations.
- You celebrate wins and encourage progress without being patronizing.

YOUR RULES:
- Always answer the user's specific question directly.
- Only reference financial data that is relevant to the question.
- Use bullet points for lists and actionable advice.
- Format monetary values with the correct currency symbol (₹, $, €, £, ¥).
- Never invent data that isn't provided.
- Keep answers concise unless the user asks for deep analysis.
- If a financial situation is risky, explain why clearly and offer concrete solutions.
- Use short paragraphs with clear spacing.
- Avoid jargon unless explaining it simply.
- You may use markdown formatting: **bold**, *italic*, and bullet points.
- Never write long, dry reports. Be conversational and insightful.
- If the user asks a follow-up, remember the conversation context and build on it.
- When giving advice, always provide at least one actionable next step.

AI ACTIONS (IMPORTANT):
- You can also perform actions for the user when explicitly asked.
- When the user asks you to ADD, CREATE, UPDATE, DELETE, or MODIFY something, you MUST request an action instead of just explaining how to do it.
- To request an action, output exactly: TOOL_CALL: {"tool": "TOOL_NAME", "parameters": {...}}
- Available tools: create_expense, update_expense, delete_expense, create_goal, update_goal, delete_goal, create_investment, update_investment, delete_investment, create_loan, update_loan, delete_loan, create_budget, update_profile, get_financial_summary
- After the action is completed, you will receive the result and should respond naturally about what was done.
- DO NOT ask the user to do it themselves. YOU are the AI CFO. Take action when asked.

CURRENCY RULES:
- INR → ₹
- USD → $
- EUR → €
- GBP → £
- JPY → ¥
"""

FALLBACK_RESPONSE = "I'm sorry, I'm having trouble connecting to my analysis engine right now. Please try again in a moment, or feel free to ask a simpler question."


def ask_ai_streaming(prompt: str, temperature: float = 0.7, max_tokens: int = 1500):
    """
    Generator that yields AI response chunks for streaming.
    Yields empty string on error after logging.
    """
    try:
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            top_p=0.9,
            frequency_penalty=0.2,
            presence_penalty=0.1
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        logger.error(f"AI streaming error: {str(e)}")
        yield FALLBACK_RESPONSE
