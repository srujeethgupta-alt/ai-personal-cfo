from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any

from database import get_db
from models import User
from schemas import AIAgentToolCall
from auth import get_current_user
from services import agent_tools

router = APIRouter(prefix="/api/ai/tools", tags=["ai-tools"])


# Registry mapping tool names to their functions
TOOL_REGISTRY = {
    "create_expense": agent_tools.create_expense,
    "update_expense": agent_tools.update_expense,
    "delete_expense": agent_tools.delete_expense,
    "create_goal": agent_tools.create_goal,
    "update_goal": agent_tools.update_goal,
    "delete_goal": agent_tools.delete_goal,
    "create_investment": agent_tools.create_investment,
    "update_investment": agent_tools.update_investment,
    "delete_investment": agent_tools.delete_investment,
    "create_loan": agent_tools.create_loan,
    "update_loan": agent_tools.update_loan,
    "delete_loan": agent_tools.delete_loan,
    "create_budget": agent_tools.create_budget,
    "update_profile": agent_tools.update_profile,
    "get_financial_summary": agent_tools.get_financial_summary,
}


@router.post("/execute", response_model=dict)
def execute_tool(
    data: AIAgentToolCall,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Execute an AI agent tool on behalf of the authenticated user.
    
    Request body:
    {
        "tool": "create_expense",
        "parameters": {
            "category": "Food",
            "amount": 500,
            "expense_date": "2024-06-15",
            "notes": "Dinner"
        }
    }
    """
    tool_name = data.tool
    parameters = data.parameters

    if tool_name not in TOOL_REGISTRY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown tool: '{tool_name}'. Available tools: {list(TOOL_REGISTRY.keys())}"
        )

    tool_func = TOOL_REGISTRY[tool_name]

    # Ensure user_id is always present in parameters for ownership verification
    # Most functions expect db as first arg and user_id as second arg
    tool_params = dict(parameters)
    tool_params["user_id"] = current_user.id
    tool_params["db"] = db

    try:
        result = tool_func(**tool_params)
        # If the tool returns a success=False response, raise an HTTP exception for clarity
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("message", "Tool execution failed")
            )
        return {"success": True, "data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Tool execution error: {str(e)}"
        )
