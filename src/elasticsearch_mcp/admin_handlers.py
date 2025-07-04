"""
Admin tool handlers.
"""
from pathlib import Path
from typing import List, Dict, Any

import mcp.types as types
from .config import load_config
from .security import get_allowed_base_dir, set_allowed_base_dir, init_security
from .elasticsearch_client import reset_es_client, init_elasticsearch


async def handle_get_allowed_directory(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle get_allowed_directory tool."""
    return [
        types.TextContent(
            type="text",
            text=f"Current allowed base directory: {get_allowed_base_dir()}"
        )
    ]


async def handle_set_allowed_directory(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle set_allowed_directory tool."""
    directory_path = arguments.get("directory_path")
    
    try:
        new_path = Path(directory_path).resolve()
        
        if not new_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        if not new_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {directory_path}")
        
        old_path = set_allowed_base_dir(new_path)
        
        return [
            types.TextContent(
                type="text",
                text=f"Allowed base directory changed from '{old_path}' to '{get_allowed_base_dir()}'"
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"Error setting allowed directory to '{directory_path}': {str(e)}"
            )
        ]


async def handle_reload_config(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle reload_config tool."""
    try:
        # Reload configuration
        config = load_config()
        
        # Reinitialize security with new allowed directory
        init_security(config["security"]["allowed_base_directory"])
        
        # Reinitialize Elasticsearch with new config
        init_elasticsearch(config)
        reset_es_client()
        
        return [
            types.TextContent(
                type="text",
                text=f"Configuration reloaded successfully.\nNew allowed directory: {get_allowed_base_dir()}\nElasticsearch: {config['elasticsearch']['host']}:{config['elasticsearch']['port']}"
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"Error reloading configuration: {str(e)}"
            )
        ]
