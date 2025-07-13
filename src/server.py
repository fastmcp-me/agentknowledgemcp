"""
Main server module for Elasticsearch MCP Server.
Refactored into smaller, manageable modules.
"""
import asyncio
import json
from pathlib import Path
from typing import Dict, Any, List

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from pydantic import AnyUrl
import mcp.server.stdio

# Import our modules
from .config import load_config
from .security import init_security
from .elasticsearch_client import init_elasticsearch, get_es_client
from .elasticsearch_setup import auto_setup_elasticsearch
from .tools import get_all_tools
from .confirmation import initialize_confirmation_manager, get_confirmation_manager

# Import handlers
from .elasticsearch_handlers import (
    handle_search, handle_index_document, handle_create_index,
    handle_get_document, handle_delete_document, handle_list_indices,
    handle_delete_index, handle_validate_document_schema, 
    handle_create_document_template
)
from .file_handlers import (
    handle_read_file, handle_write_file, handle_append_file,
    handle_delete_file, handle_move_file, handle_copy_file,
    handle_list_directory, handle_create_directory, handle_delete_directory,
    handle_file_info
)
from .admin_handlers import (
    handle_get_allowed_directory, handle_set_allowed_directory,
    handle_reload_config, handle_setup_elasticsearch, handle_elasticsearch_status,
    handle_get_config, handle_update_config, handle_validate_config, handle_reset_config,
    handle_server_status, handle_server_upgrade, handle_get_comprehensive_usage_guide
)
from .version_control_handlers import (
    handle_setup_version_control, handle_commit_file, 
    handle_get_previous_file_version
)
from .confirmation_handlers import (
    handle_user_response, handle_confirmation_status
)

# Load configuration and initialize components
CONFIG = load_config()
init_security(CONFIG["security"]["allowed_base_directory"])

# Initialize confirmation manager
confirmation_manager = initialize_confirmation_manager(CONFIG)
print(f"✅ Confirmation system initialized (enabled: {CONFIG.get('confirmation', {}).get('enabled', True)})")

# Auto-setup Elasticsearch if needed
print("Checking Elasticsearch configuration")
config_path = Path(__file__).parent / "config.json"
setup_result = auto_setup_elasticsearch(config_path, CONFIG)

if setup_result["status"] == "setup_completed":
    # Reload config after setup
    CONFIG = load_config()
    print("✅ Elasticsearch auto-setup completed")
elif setup_result["status"] == "already_configured":
    print("Elasticsearch already configured")
elif setup_result["status"] == "setup_failed":
    print(f"⚠️  Elasticsearch auto-setup failed: {setup_result.get('error', 'Unknown error')}")
    print("📝 You can manually setup using the 'setup_elasticsearch' tool")

init_elasticsearch(CONFIG)

# Create server
server = Server(CONFIG["server"]["name"])

# Tool handler mapping
TOOL_HANDLERS = {
    # Elasticsearch tools
    "search": handle_search,
    "index_document": handle_index_document,
    "create_index": handle_create_index,
    "get_document": handle_get_document,
    "delete_document": handle_delete_document,
    "list_indices": handle_list_indices,
    "delete_index": handle_delete_index,
    "validate_document_schema": handle_validate_document_schema,
    "create_document_template": handle_create_document_template,
    
    # File system tools
    "read_file": handle_read_file,
    "write_file": handle_write_file,
    "append_file": handle_append_file,
    "delete_file": handle_delete_file,
    "move_file": handle_move_file,
    "copy_file": handle_copy_file,
    "list_directory": handle_list_directory,
    "create_directory": handle_create_directory,
    "delete_directory": handle_delete_directory,
    "file_info": handle_file_info,
    
    # Admin tools
    "get_config": handle_get_config,
    "update_config": handle_update_config,
    "validate_config": handle_validate_config,
    "reset_config": handle_reset_config,
    "get_allowed_directory": handle_get_allowed_directory,
    "set_allowed_directory": handle_set_allowed_directory,
    "reload_config": handle_reload_config,
    "setup_elasticsearch": handle_setup_elasticsearch,
    "elasticsearch_status": handle_elasticsearch_status,
    "server_status": handle_server_status,
    "server_upgrade": handle_server_upgrade,
    "get_comprehensive_usage_guide": handle_get_comprehensive_usage_guide,
    
    # Version control tools
    "setup_version_control": handle_setup_version_control,
    "commit_file": handle_commit_file,
    "get_previous_file_version": handle_get_previous_file_version,
    
    # Confirmation tools
    "user_response": handle_user_response,
    "confirmation_status": handle_confirmation_status,
}


@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """
    List available Elasticsearch indices as resources.
    Each index is exposed as a resource with a custom es:// URI scheme.
    """
    try:
        es = get_es_client()
        # Get all indices
        indices = es.indices.get_alias(index="*")
        return [
            types.Resource(
                uri=AnyUrl(f"es://index/{index_name}"),
                name=f"Index: {index_name}",
                description=f"Elasticsearch index containing {indices[index_name].get('settings', {}).get('index', {}).get('number_of_docs', 'unknown')} documents",
                mimeType="application/json",
            )
            for index_name in indices.keys()
            if not index_name.startswith('.')  # Skip system indices
        ]
    except Exception as e:
        return [
            types.Resource(
                uri=AnyUrl("es://error/connection"),
                name="Connection Error",
                description=f"Failed to connect to Elasticsearch: {str(e)}",
                mimeType="text/plain",
            )
        ]


@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    """
    Read a specific index's mapping and settings by its URI.
    """
    if uri.scheme != "es":
        raise ValueError(f"Unsupported URI scheme: {uri.scheme}")

    path_parts = uri.path.strip("/").split("/")
    if len(path_parts) < 2:
        raise ValueError("Invalid URI path")
    
    resource_type = path_parts[0]
    resource_name = path_parts[1]
    
    if resource_type == "index":
        try:
            es = get_es_client()
            mapping = es.indices.get_mapping(index=resource_name)
            settings = es.indices.get_settings(index=resource_name)
            stats = es.indices.stats(index=resource_name)
            
            return json.dumps({
                "index": resource_name,
                "mapping": mapping,
                "settings": settings,
                "stats": stats
            }, indent=2)
        except Exception as e:
            raise ValueError(f"Failed to read index {resource_name}: {str(e)}")
    elif resource_type == "error":
        return f"Elasticsearch connection error: {resource_name}"
    else:
        raise ValueError(f"Unknown resource type: {resource_type}")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    """
    return get_all_tools()


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests with sophisticated confirmation system.
    """
    if not arguments:
        arguments = {}

    try:
        # Handle confirmation tools first (they bypass confirmation)
        if name in ["user_response", "confirmation_status"]:
            handler = TOOL_HANDLERS.get(name)
            if handler:
                return await handler(arguments)
            else:
                raise ValueError(f"Handler not found for confirmation tool: {name}")

        # Check if tool requires confirmation
        confirmation_mgr = get_confirmation_manager()
        if confirmation_mgr:
            requires_confirm, rule_details = await confirmation_mgr.requires_confirmation(name)
            
            if requires_confirm:
                # Store the operation and request confirmation
                try:
                    pending_id = await confirmation_mgr.store_operation(
                        tool_name=name,
                        arguments=arguments,
                        session_id=None  # Could extract from request context if needed
                    )
                    
                    return [types.TextContent(
                        type="text",
                        text=f"🚨 **CONFIRMATION REQUIRED** 🚨\n\n"
                             f"**Operation**: {name}\n"
                             f"**Rule**: {rule_details.get('rule_name', 'default')}\n"
                             f"**Timeout**: {rule_details.get('timeout_minutes', 30)} minutes\n"
                             f"**Pending ID**: {pending_id}\n\n"
                             f"⚠️ This operation requires user approval before execution.\n\n"
                             f"**Required Action**:\n"
                             f"Please ask user to confirm this operation, then call:\n"
                             f"• **To Approve**: user_response(pending_id='{pending_id}', response='yes')\n"
                             f"• **To Deny**: user_response(pending_id='{pending_id}', response='no')\n\n"
                             f"⏰ **This request will expire in {rule_details.get('timeout_minutes', 30)} minutes**"
                    )]
                    
                except ValueError as e:
                    # If confirmation system has issues, fall back to normal execution with warning
                    print(f"⚠️ Confirmation system error: {e}")
                    return [types.TextContent(
                        type="text",
                        text=f"⚠️ **Confirmation System Warning**: {str(e)}\n\n"
                             f"Proceeding with operation without confirmation..."
                    )] + await _execute_tool_directly(name, arguments)

        # Normal tool execution (no confirmation required or confirmation disabled)
        return await _execute_tool_directly(name, arguments)
        
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"❌ **Error executing {name}**: {str(e)}"
            )
        ]


async def _execute_tool_directly(name: str, arguments: dict) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Execute tool directly without confirmation.
    
    Args:
        name: Tool name
        arguments: Tool arguments
        
    Returns:
        Tool execution result
    """
    handler = TOOL_HANDLERS.get(name)
    if not handler:
        raise ValueError(f"Unknown tool: {name}")
    
    return await handler(arguments)


async def main():
    """Main server entry point."""
    confirmation_mgr = get_confirmation_manager()
    
    try:
        # Start confirmation cleanup task now that we're in async context
        if confirmation_mgr:
            await confirmation_mgr.start_cleanup_task()
        
        # Run the server using stdin/stdout streams
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name=CONFIG["server"]["name"],
                    server_version=CONFIG["server"]["version"],
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
    finally:
        # Graceful shutdown of confirmation system
        if confirmation_mgr:
            print("🧹 Shutting down confirmation system...")
            await confirmation_mgr.shutdown()


def cli_main():
    """CLI entry point that handles async execution."""
    import asyncio
    asyncio.run(main())


if __name__ == "__main__":
    cli_main()
