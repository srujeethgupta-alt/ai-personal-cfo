from rate_limit import limiter
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
import json
import re

from database import get_db
from models import User
from schemas import CFOQuestion, CFOAnswer
from services.analytics_service import build_ai_context
from services.ai_service import ask_ai, ask_ai_streaming
from services.agent_tools import (
    create_expense, update_expense, delete_expense,
    create_goal, update_goal, delete_goal,
    create_investment, update_investment, delete_investment,
    create_loan, update_loan, delete_loan,
    create_budget, update_profile, get_financial_summary
)
from fastapi.responses import StreamingResponse
from auth import get_current_user

router = APIRouter(prefix="/api/ai", tags=["ai"])

TOOL_REGISTRY = {
    "create_expense": create_expense,
    "update_expense": update_expense,
    "delete_expense": delete_expense,
    "create_goal": create_goal,
    "update_goal": update_goal,
    "delete_goal": delete_goal,
    "create_investment": create_investment,
    "update_investment": update_investment,
    "delete_investment": delete_investment,
    "create_loan": create_loan,
    "update_loan": update_loan,
    "delete_loan": delete_loan,
    "create_budget": create_budget,
    "update_profile": update_profile,
    "get_financial_summary": get_financial_summary,
}


def _extract_tool_call(text: str) -> dict:
    """Extract tool call JSON from AI response."""
    match = re.search(r"TOOL_CALL:\s*(\{.*?\})", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            return None
    return None


def _execute_tool(db, user_id: int, tool_call: dict) -> dict:
    """Execute a tool from the registry."""
    tool_name = tool_call.get("tool")
    parameters = tool_call.get("parameters", {})
    
    if tool_name not in TOOL_REGISTRY:
        return {"success": False, "error": f"Unknown tool: {tool_name}"}
    
    try:
        func = TOOL_REGISTRY[tool_name]
        # Inject user_id and db into parameters
        parameters["user_id"] = user_id
        parameters["db"] = db
        result = func(**parameters)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


def _sanitize_prompt(text: str) -> str:
    """Sanitize user input to prevent basic prompt injection."""
    if not text:
        return ""
    # Limit length
    max_len = 2000
    text = text[:max_len]
    # Remove common injection patterns (case-insensitive)
    injection_patterns = [
        r"ignore previous instructions",
        r"ignore all prior instructions",
        r"system prompt",
        r"you are now",
        r"new instructions:",
        r"overwrite instructions",
        r"disregard everything",
        r"act as",
        r"pretend you are",
        r"roleplay as",
        r"DAN mode",
        r"jailbreak",
    ]
    for pattern in injection_patterns:
        text = re.sub(pattern, "[REMOVED]", text, flags=re.IGNORECASE)
    return text


@router.post("/ask-cfo", response_model=dict)
@limiter.limit("15/minute")
def ask_cfo(request: Request, data: CFOQuestion, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Ask the AI CFO a question with full financial context and conversation history."""
    sanitized_question = _sanitize_prompt(data.question)
    context = build_ai_context(db, user_id=current_user.id)
    
    # Build conversation history
    conversation_history = ""
    for msg in data.history[-10:]:
        role = "User" if msg.get("sender") == "user" else "AI CFO"
        conversation_history += f"{role}: {msg.get('text')}\n"
    
    prompt = f"""User Financial Context (Currency: {context['currency']}):

Monthly Salary: {context['salary']}
Total Expenses: {context['total_expenses']}
Expense Categories: {context['expense_categories']}
Total Investments: {context['total_investments']}
Total Invested: {context['total_invested']}
Investment Allocation: {context['investment_allocation']}
Total Loans: {context['total_loans']}
Total EMI: {context['total_emi']}
Net Worth: {context['net_worth']['net_worth']}
Health Score: {context['health_score']['health_score']}% ({context['health_score']['rating']})
Goals: {context['goals']}

Conversation History:
{conversation_history}

Current User Question: {sanitized_question}

Instructions:
- Answer ONLY the user's question.
- Do not repeat all financial data unless asked.
- Be conversational, warm, and insightful.
- Use bullet points for lists.
- Give practical, actionable recommendations.
- Use the correct currency symbol ({context['currency']}).
- If the user asks you to create, update, or delete something, output TOOL_CALL: {{"tool": "TOOL_NAME", "parameters": {{...}}}} and nothing else.
"""
    
    answer = ask_ai(prompt)
    
    # Check if the AI requested a tool call
    tool_call = _extract_tool_call(answer)
    if tool_call:
        tool_result = _execute_tool(db, current_user.id, tool_call)
        
        # Second AI call to get natural language response about the tool result
        follow_up_prompt = f"""You just executed a tool for the user. Here is the result:

Tool: {tool_call.get('tool')}
Result: {json.dumps(tool_result)}

Now respond to the user in a natural, conversational way about what was done. Keep it brief and warm."""
        
        final_answer = ask_ai(follow_up_prompt)
        return {
            "success": True,
            "data": {
                "question": data.question,
                "answer": final_answer,
                "tool_executed": tool_call.get("tool"),
                "tool_result": tool_result
            }
        }
    
    return {"success": True, "data": {"question": data.question, "answer": answer}}


@router.post("/ask-cfo/stream")
@limiter.limit("15/minute")
def ask_cfo_stream(request: Request, data: CFOQuestion, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Streaming version of ask-cfo for real-time response."""
    sanitized_question = _sanitize_prompt(data.question)
    context = build_ai_context(db, user_id=current_user.id)
    
    conversation_history = ""
    for msg in data.history[-10:]:
        role = "User" if msg.get("sender") == "user" else "AI CFO"
        conversation_history += f"{role}: {msg.get('text')}\n"
    
    prompt = f"""User Financial Context (Currency: {context['currency']}):

Monthly Salary: {context['salary']}
Total Expenses: {context['total_expenses']}
Expense Categories: {context['expense_categories']}
Total Investments: {context['total_investments']}
Total Invested: {context['total_invested']}
Investment Allocation: {context['investment_allocation']}
Total Loans: {context['total_loans']}
Total EMI: {context['total_emi']}
Net Worth: {context['net_worth']['net_worth']}
Health Score: {context['health_score']['health_score']}% ({context['health_score']['rating']})
Goals: {context['goals']}

Conversation History:
{conversation_history}

Current User Question: {sanitized_question}

Instructions:
- Answer ONLY the user's question.
- Be conversational, warm, and insightful.
- Use bullet points for lists.
- Give practical, actionable recommendations.
- Use the correct currency symbol ({context['currency']}).
"""
    
    return StreamingResponse(
        ask_ai_streaming(prompt),
        media_type="text/plain"
    )


@router.get("/advisor", response_model=dict)
def ai_advisor(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get comprehensive AI financial advisor report."""
    context = build_ai_context(db, user_id=current_user.id)
    
    prompt = f"""You are an elite AI Personal CFO. Provide a comprehensive financial health report.

Financial Context:
{context}

Provide:
1. Financial Health Summary (2-3 sentences)
2. Key Strengths (3 bullet points)
3. Financial Risks (3 bullet points)
4. Actionable Recommendations (5 bullet points)
5. Next Steps (3 bullet points)

Rules:
- Sound like ChatGPT.
- Be conversational and warm.
- Use bullet points.
- Focus on practical actions.
- Use currency: {context['currency']}
"""
    
    advice = ask_ai(prompt)
    return {"success": True, "data": {"financial_advice": advice}}


@router.get("/expense-advisor", response_model=dict)
def ai_expense_advisor(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get AI-powered expense analysis and recommendations."""
    context = build_ai_context(db, user_id=current_user.id)
    
    prompt = f"""You are an AI Expense Advisor. Analyze this spending data.

Expense Data:
Total Expenses: {context['total_expenses']}
Category Breakdown: {context['expense_categories']}
Monthly Trends: {context['monthly_trends']}
Monthly Income: {context['salary']}

Provide:
1. Spending Analysis (2-3 sentences)
2. Biggest Expense Categories (bullet points)
3. Areas to Cut Costs (bullet points)
4. Savings Opportunities (bullet points)
5. Recommended Monthly Budget (bullet points)

Rules:
- Be concise.
- Use bullet points.
- Focus on actionable advice.
- Sound like a helpful financial coach.
- Use currency: {context['currency']}
"""
    
    advice = ask_ai(prompt)
    return {"success": True, "data": {"expense_advice": advice}}


@router.get("/investment-advisor", response_model=dict)
def ai_investment_advisor(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get AI-powered investment portfolio analysis."""
    context = build_ai_context(db, user_id=current_user.id)
    
    prompt = f"""You are an AI Investment Advisor. Review this portfolio.

Portfolio:
Total Invested: {context['total_invested']}
Current Value: {context['total_investments']}
Allocation: {context['investment_allocation']}

Provide:
1. Portfolio Health (2-3 sentences)
2. Diversification Review (bullet points)
3. Risk Assessment (bullet points)
4. Growth Opportunities (bullet points)
5. Recommendations (bullet points)

Rules:
- Explain simply.
- Use bullet points.
- Avoid unnecessary jargon.
- Keep answers practical.
- Use currency: {context['currency']}
"""
    
    advice = ask_ai(prompt)
    return {"success": True, "data": {"investment_advice": advice}}


@router.get("/loan-advisor", response_model=dict)
def ai_loan_advisor(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get AI-powered loan and debt strategy."""
    context = build_ai_context(db, user_id=current_user.id)
    
    prompt = f"""You are an AI Loan Advisor. Analyze this debt profile.

Debt Profile:
Total Remaining: {context['total_loans']}
Total EMI: {context['total_emi']}
Net Worth: {context['net_worth']['net_worth']}

Provide:
1. Debt Burden Analysis (2-3 sentences)
2. EMI Impact Assessment (bullet points)
3. High-Risk Areas (bullet points)
4. Debt Reduction Plan (bullet points)
5. Recommendations (bullet points)

Rules:
- Be realistic.
- Prioritize financial stability.
- Use bullet points.
- Focus on actionable steps.
- Use currency: {context['currency']}
"""
    
    advice = ask_ai(prompt)
    return {"success": True, "data": {"loan_advice": advice}}


@router.get("/goal-advisor", response_model=dict)
def ai_goal_advisor(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get AI-powered goal planning advice."""
    context = build_ai_context(db, user_id=current_user.id)
    
    prompt = f"""You are an AI Goal Planner. Review these goals.

Goals:
{context['goals']}

Forecast:
{context['forecast']}

Provide:
1. Goal Progress Review (bullet points)
2. Timeline Analysis (bullet points)
3. Feasibility Check (bullet points)
4. Savings Recommendations (bullet points)
5. Goal Prioritization (bullet points)

Rules:
- Be encouraging but honest.
- If a goal is unrealistic, say so respectfully.
- Use bullet points.
- Focus on practical next steps.
- Use currency: {context['currency']}
"""
    
    advice = ask_ai(prompt)
    return {"success": True, "data": {"goal_advice": advice}}
