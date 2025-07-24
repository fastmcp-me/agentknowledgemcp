"""
Confirmation Middleware for AgentKnowledgeMCP
Provides confirmation for destructive operations based on configuration rules.
"""
from typing import Tuple

from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.exceptions import ToolError

from src.config.config import load_config


class ConfirmationMiddleware(Middleware):
    """Middleware that provides confirmation for destructive operations based on configuration rules."""

    def __init__(self):
        super().__init__()
        self.config = None
        self._load_config()

    def _load_config(self):
        """Load confirmation configuration from config.json."""
        try:
            self.config = load_config()
        except Exception as e:
            print(f"Warning: Could not load config for confirmation middleware: {e}")
            self.config = {}

    def _get_confirmation_rules(self) -> dict:
        """Get confirmation rules from configuration."""
        if not self.config:
            self._load_config()
        
        confirmation_config = self.config.get("confirmation", {})
        if not confirmation_config.get("enabled", False):
            return {}
        
        return confirmation_config.get("rules", {})

    def _requires_confirmation(self, tool_name: str) -> Tuple[bool, dict]:
        """Check if tool requires confirmation based on configuration rules."""
        rules = self._get_confirmation_rules()
        
        for rule_name, rule_config in rules.items():
            if not rule_config.get("require_confirmation", False):
                continue
                
            tools_list = rule_config.get("tools", [])
            if tool_name in tools_list:
                return True, rule_config
        
        return False, {}

    async def on_call_tool(self, context: MiddlewareContext, call_next):
        """Hook called when tools are being executed - check for confirmation requirements."""
        tool_name = context.message.name
        
        # Check if this tool requires confirmation
        requires_confirmation, rule_config = self._requires_confirmation(tool_name)
        
        if not requires_confirmation:
            # No confirmation needed, proceed with tool execution
            return await call_next(context)
        
        # Get FastMCP context to access elicitation
        if not context.fastmcp_context:
            # No FastMCP context available, skip confirmation
            return await call_next(context)
        
        try:
            # Build confirmation message
            rule_name = rule_config.get("description", "Unknown Rule")
            
            confirmation_message = f"""🔒 **Confirmation Required: {rule_name}**

📋 **Tool:** {tool_name}

⚠️ **This operation requires confirmation before proceeding.**

🤔 **Do you want to continue with this operation?**"""

            # Request confirmation from user
            ctx = context.fastmcp_context
            result = await ctx.elicit(
                message=confirmation_message,
                response_type=None  # Simple accept/decline confirmation
            )
            
            if result.action == "accept":
                # User confirmed, proceed with tool execution
                await ctx.info(f"✅ User confirmed execution of {tool_name}")
                return await call_next(context)
            elif result.action == "decline":
                # User declined
                await ctx.warning(f"❌ User declined execution of {tool_name}")
                raise ToolError(f"Operation cancelled: User declined to confirm {tool_name} execution")
            else:  # cancel
                # User cancelled
                await ctx.warning(f"🚫 User cancelled execution of {tool_name}")
                raise ToolError(f"Operation cancelled: User cancelled {tool_name} execution")
                
        except Exception as e:
            # If confirmation fails, default to blocking the operation for security
            if context.fastmcp_context:
                await context.fastmcp_context.error(f"❌ Confirmation failed for {tool_name}: {str(e)}")
            raise ToolError(f"Confirmation failed for {tool_name}: {str(e)}")
