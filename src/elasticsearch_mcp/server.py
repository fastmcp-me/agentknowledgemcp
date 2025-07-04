"""
Main server module for Elasticsearch MCP Server.
Refactored into smaller, manageable modules.
"""
import asyncio
import json
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
from .tools import get_all_tools

# Import handlers
from .elasticsearch_handlers import (
    handle_search, handle_index_document, handle_create_index,
    handle_get_document, handle_delete_document, handle_list_indices,
    handle_delete_index
)
from .file_handlers import (
    handle_read_file, handle_write_file, handle_append_file,
    handle_delete_file, handle_move_file, handle_copy_file,
    handle_list_directory, handle_create_directory, handle_delete_directory,
    handle_file_info
)
from .admin_handlers import (
    handle_get_allowed_directory, handle_set_allowed_directory,
    handle_reload_config
)

# Load configuration and initialize components
CONFIG = load_config()
init_security(CONFIG["security"]["allowed_base_directory"])
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
    "get_allowed_directory": handle_get_allowed_directory,
    "set_allowed_directory": handle_set_allowed_directory,
    "reload_config": handle_reload_config,
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
    Handle tool execution requests.
    """
    if not arguments:
        arguments = {}

    try:
        # Get the appropriate handler
        handler = TOOL_HANDLERS.get(name)
        if not handler:
            raise ValueError(f"Unknown tool: {name}")
        
        # Call the handler
        return await handler(arguments)
        
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"Error executing {name}: {str(e)}"
            )
        ]


async def main():
    """Main server entry point."""
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
