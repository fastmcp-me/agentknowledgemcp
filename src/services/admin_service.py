"""
Admin Service for FastMCP server composition.
Contains all administrative and configuration management tools.
"""
from typing import Dict, Any, Optional, Annotated

from fastmcp import FastMCP
from pydantic import Field

# Import existing handlers
from ..admin_handlers import (
    handle_get_config, handle_update_config, handle_validate_config, handle_reset_config,
    handle_get_allowed_directory, handle_set_allowed_directory,
    handle_reload_config, handle_setup_elasticsearch, handle_elasticsearch_status,
    handle_server_status, handle_server_upgrade, handle_get_comprehensive_usage_guide
)

# Create Admin service
admin_service = FastMCP(
    name="AdminService",
    instructions="Administrative service for configuration management, system status, and server operations"
)

@admin_service.tool(
    description="⚙️ Get the complete configuration from config.json file",
    tags={"admin", "config", "settings", "view"}
)
async def get_config() -> str:
    """Get the complete configuration from config.json file."""
    result = await handle_get_config({})
    return result[0].text if result and hasattr(result[0], 'text') else str(result)

@admin_service.tool(
    description="✏️ Update configuration values with section-specific or full configuration changes",
    tags={"admin", "config", "update", "settings"}
)
async def update_config(
    config_section: Annotated[Optional[str], Field(description="Configuration section to update (e.g., 'server', 'elasticsearch')")] = None,
    config_key: Annotated[Optional[str], Field(description="Specific configuration key within the section")] = None,
    config_value: Annotated[Optional[str], Field(description="New value for the configuration key")] = None,
    full_config: Annotated[Optional[Dict[str, Any]], Field(description="Complete configuration object to replace current config")] = None
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

@admin_service.tool(
    description="✅ Validate configuration file structure and values",
    tags={"admin", "config", "validate", "check"}
)
async def validate_config() -> str:
    """Validate the current configuration."""
    result = await handle_validate_config({})
    return result[0].text if result and hasattr(result[0], 'text') else str(result)

@admin_service.tool(
    description="🔄 Reset configuration to default values",
    tags={"admin", "config", "reset", "default"}
)
async def reset_config() -> str:
    """Reset configuration to default values."""
    result = await handle_reset_config({})
    return result[0].text if result and hasattr(result[0], 'text') else str(result)

@admin_service.tool(
    description="📁 Get the currently allowed base directory for file operations",
    tags={"admin", "security", "directory", "permissions"}
)
async def get_allowed_directory() -> str:
    """Get the allowed base directory."""
    result = await handle_get_allowed_directory({})
    return result[0].text if result and hasattr(result[0], 'text') else str(result)

@admin_service.tool(
    description="🔒 Set the allowed base directory for file operations security",
    tags={"admin", "security", "directory", "permissions"}
)
async def set_allowed_directory(
    directory_path: Annotated[str, Field(description="New base directory path to set as allowed")]
) -> str:
    """Set the allowed base directory."""
    arguments = {
        "directory_path": directory_path
    }
    
    handler_result = await handle_set_allowed_directory(arguments)
    return handler_result[0].text if handler_result and hasattr(handler_result[0], 'text') else str(handler_result)

@admin_service.tool(
    description="🔁 Reload configuration from config.json file",
    tags={"admin", "config", "reload", "refresh"}
)
async def reload_config() -> str:
    """Reload configuration from file."""
    result = await handle_reload_config({})
    return result[0].text if result and hasattr(result[0], 'text') else str(result)

@admin_service.tool(
    description="🔧 Setup Elasticsearch connection and configuration",
    tags={"admin", "elasticsearch", "setup", "connection"}
)
async def setup_elasticsearch() -> str:
    """Setup Elasticsearch connection."""
    result = await handle_setup_elasticsearch({})
    return result[0].text if result and hasattr(result[0], 'text') else str(result)

@admin_service.tool(
    description="📊 Check Elasticsearch connection status and health",
    tags={"admin", "elasticsearch", "status", "health"}
)
async def elasticsearch_status() -> str:
    """Check Elasticsearch status."""
    result = await handle_elasticsearch_status({})
    return result[0].text if result and hasattr(result[0], 'text') else str(result)

@admin_service.tool(
    description="🖥️ Get comprehensive server status and system information",
    tags={"admin", "server", "status", "system"}
)
async def server_status() -> str:
    """Get server status information."""
    result = await handle_server_status({})
    return result[0].text if result and hasattr(result[0], 'text') else str(result)

@admin_service.tool(
    description="⬆️ Upgrade the server to the latest version",
    tags={"admin", "server", "upgrade", "update"}
)
async def server_upgrade() -> str:
    """Upgrade the server to latest version."""
    result = await handle_server_upgrade({})
    return result[0].text if result and hasattr(result[0], 'text') else str(result)

@admin_service.tool(
    description="📚 Get comprehensive usage guide and documentation",
    tags={"admin", "help", "documentation", "guide"}
)
async def get_comprehensive_usage_guide() -> str:
    """Get comprehensive usage guide."""
    result = await handle_get_comprehensive_usage_guide({})
    return result[0].text if result and hasattr(result[0], 'text') else str(result)
