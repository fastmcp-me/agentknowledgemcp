"""
FastMCP server implementation for AgentKnowledgeMCP.
Migration from Standard MCP to FastMCP for enhanced elicitation capabilities.
"""
import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from fastmcp import FastMCP
from fastmcp.server import Context
from pydantic import BaseModel, Field
import mcp.types as types

# Import our existing modules
from .config import load_config
from .security import init_security
from .elasticsearch_client import init_elasticsearch, get_es_client
from .elasticsearch_setup import auto_setup_elasticsearch
from .confirmation import initialize_confirmation_manager, get_confirmation_manager

# Import handlers - we'll convert these to FastMCP decorators
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

# Create FastMCP app
app = FastMCP(
    name=CONFIG["server"]["name"],
    version=CONFIG["server"]["version"],
    instructions="AgentKnowledgeMCP with FastMCP and elicitation support for knowledge management"
)

# ================================
# ELASTICSEARCH TOOLS (FastMCP)
# ================================

@app.tool()
async def search(
    index: str,
    query: str,
    size: int = 10,
    fields: Optional[List[str]] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    time_period: Optional[str] = None,
    sort_by_time: str = "desc"
) -> str:
    """Search documents in Elasticsearch index with optional time-based filtering."""
    arguments = {
        "index": index,
        "query": query,
        "size": size,
        "fields": fields,
        "date_from": date_from,
        "date_to": date_to,
        "time_period": time_period,
        "sort_by_time": sort_by_time
    }
    result = await handle_search(arguments)
    return result[0].text if result and hasattr(result[0], 'text') else str(result)

@app.tool()
async def index_document(
    index: str,
    document: Dict[str, Any],
    doc_id: Optional[str] = None,
    validate_schema: bool = True
) -> str:
    """Index a document into Elasticsearch with optional schema validation."""
    arguments = {
        "index": index,
        "document": document,
        "doc_id": doc_id,
        "validate_schema": validate_schema
    }
    
    # For now, just call the handler directly
    handler_result = await handle_index_document(arguments)
    return handler_result[0].text if handler_result and hasattr(handler_result[0], 'text') else str(handler_result)

@app.tool()
async def delete_document(
    index: str,
    doc_id: str
) -> str:
    """Delete a document from Elasticsearch index."""
    arguments = {
        "index": index,
        "doc_id": doc_id
    }
    
    # For now, just call the handler directly
    # We'll add elicitation later when we understand FastMCP Context better
    handler_result = await handle_delete_document(arguments)
    return handler_result[0].text if handler_result and hasattr(handler_result[0], 'text') else str(handler_result)

@app.tool()
async def get_document(
    index: str,
    doc_id: str
) -> str:
    """Get a specific document by ID."""
    arguments = {
        "index": index,
        "doc_id": doc_id
    }
    result = await handle_get_document(arguments)
    return result[0].text if result and hasattr(result[0], 'text') else str(result)

@app.tool()
async def create_index(
    index: str,
    mapping: Dict[str, Any],
    settings: Optional[Dict[str, Any]] = None
) -> str:
    """Create a new Elasticsearch index with mapping."""
    arguments = {
        "index": index,
        "mapping": mapping,
        "settings": settings
    }
    
    handler_result = await handle_create_index(arguments)
    return handler_result[0].text if handler_result and hasattr(handler_result[0], 'text') else str(handler_result)

@app.tool()
async def list_indices() -> str:
    """List all Elasticsearch indices."""
    result = await handle_list_indices({})
    return result[0].text if result and hasattr(result[0], 'text') else str(result)

@app.tool()
async def delete_index(
    index: str
) -> str:
    """Delete an Elasticsearch index."""
    arguments = {
        "index": index
    }
    
    handler_result = await handle_delete_index(arguments)
    return handler_result[0].text if handler_result and hasattr(handler_result[0], 'text') else str(handler_result)

# ================================
# FILE OPERATION TOOLS (FastMCP)
# ================================

@app.tool()
async def read_file(
    file_path: str,
    encoding: str = "utf-8"
) -> str:
    """Read content from a file."""
    arguments = {
        "file_path": file_path,
        "encoding": encoding
    }
    result = await handle_read_file(arguments)
    return result[0].text if result and hasattr(result[0], 'text') else str(result)

@app.tool()
async def write_file(
    file_path: str,
    content: str,
    encoding: str = "utf-8",
    create_dirs: bool = True
) -> str:
    """Write content to a file (creates new or overwrites existing)."""
    arguments = {
        "file_path": file_path,
        "content": content,
        "encoding": encoding,
        "create_dirs": create_dirs
    }
    
    # For now, just call the handler directly
    handler_result = await handle_write_file(arguments)
    return handler_result[0].text if handler_result and hasattr(handler_result[0], 'text') else str(handler_result)

@app.tool()
async def delete_file(
    file_path: str
) -> str:
    """Delete a file."""
    arguments = {
        "file_path": file_path
    }
    
    handler_result = await handle_delete_file(arguments)
    return handler_result[0].text if handler_result and hasattr(handler_result[0], 'text') else str(handler_result)

# ================================
# ADMIN TOOLS (FastMCP)
# ================================

@app.tool()
async def update_config(
    config_section: Optional[str] = None,
    config_key: Optional[str] = None,
    config_value: Optional[str] = None,
    full_config: Optional[Dict[str, Any]] = None
) -> str:
    """Update the configuration file with new values."""
    arguments = {
        "config_section": config_section,
        "config_key": config_key,
        "config_value": config_value,
        "full_config": full_config
    }
    
    handler_result = await handle_update_config(arguments)
    return handler_result[0].text if handler_result and hasattr(handler_result[0], 'text') else str(handler_result)

@app.tool()
async def get_config() -> str:
    """Get the complete configuration from config.json file."""
    result = await handle_get_config({})
    return result[0].text if result and hasattr(result[0], 'text') else str(result)

# ================================
# CONFIRMATION TOOLS (FastMCP)
# ================================

@app.tool()
async def confirmation_status(
    pending_id: Optional[str] = None,
    session_id: Optional[str] = None
) -> str:
    """Get status of confirmation system and pending operations."""
    arguments = {
        "pending_id": pending_id,
        "session_id": session_id
    }
    result = await handle_confirmation_status(arguments)
    return result[0].text if result and hasattr(result[0], 'text') else str(result)

def cli_main():
    """CLI entry point for FastMCP server."""
    print("🚀 Starting AgentKnowledgeMCP FastMCP server...")
    print(f"📊 Server: {CONFIG['server']['name']}")
    print(f"🔧 Version: {CONFIG['server']['version']}")
    print("🌟 Architecture: FastMCP with Elicitation Support")
    
    # Start the FastMCP app using the run method
    app.run()

if __name__ == "__main__":
    cli_main()
