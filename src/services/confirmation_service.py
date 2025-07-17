"""
Confirmation Service for FastMCP server composition.
Contains confirmation system tools for managing user confirmations.
"""
from typing import Optional, Annotated

from fastmcp import FastMCP
from pydantic import Field

# Import existing handlers
from src.confirmation.confirmation_handlers import (
    handle_user_response, handle_confirmation_status
)

# Create Confirmation service
confirmation_service = FastMCP(
    name="ConfirmationService",
    instructions="Confirmation system service for managing user confirmations and pending operations"
)

@confirmation_service.tool(
    description="✅ Submit user response to a pending confirmation request",
    tags={"confirmation", "user", "response", "approval"}
)
async def user_response(
    pending_id: Annotated[str, Field(description="Unique ID of the pending operation requiring confirmation")],
    response: Annotated[str, Field(description="User response - 'yes' to approve, 'no' to deny")]
) -> str:
    """Submit user response to a pending confirmation."""
    arguments = {
        "pending_id": pending_id,
        "response": response
    }

    handler_result = await handle_user_response(arguments)
    return handler_result[0].text if handler_result and hasattr(handler_result[0], 'text') else str(handler_result)

@confirmation_service.tool(
    description="📋 Get status of confirmation system and pending operations",
    tags={"confirmation", "status", "pending", "system"}
)
async def confirmation_status(
    pending_id: Annotated[Optional[str], Field(description="Specific pending operation ID to check (optional)")] = None,
    session_id: Annotated[Optional[str], Field(description="Session ID to filter pending operations (optional)")] = None
) -> str:
    """Get status of confirmation system and pending operations."""
    arguments = {
        "pending_id": pending_id,
        "session_id": session_id
    }
    result = await handle_confirmation_status(arguments)
    return result[0].text if result and hasattr(result[0], 'text') else str(result)
