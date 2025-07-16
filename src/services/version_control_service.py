"""
Version Control Service for FastMCP server composition.
Contains all version control and file history management tools.
"""
from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

# Import existing handlers
from ..version_control_handlers import (
    handle_setup_version_control, handle_commit_file, 
    handle_get_previous_file_version
)

# Create Version Control service
version_control_service = FastMCP(
    name="VersionControlService",
    instructions="Version control service for file history management, commits, and version tracking"
)

@version_control_service.tool(
    description="🔧 Setup version control system for tracking file changes",
    tags={"version", "control", "setup", "git", "tracking"}
)
async def setup_version_control(
    repository_path: Annotated[str, Field(description="Path where to initialize version control repository")]
) -> str:
    """Setup version control system."""
    arguments = {
        "repository_path": repository_path
    }
    
    handler_result = await handle_setup_version_control(arguments)
    return handler_result[0].text if handler_result and hasattr(handler_result[0], 'text') else str(handler_result)

@version_control_service.tool(
    description="💾 Commit a file to version control with a descriptive message",
    tags={"version", "control", "commit", "save", "history"}
)
async def commit_file(
    file_path: Annotated[str, Field(description="Path to the file to commit to version control")],
    commit_message: Annotated[str, Field(description="Descriptive message explaining the changes made")]
) -> str:
    """Commit a file to version control."""
    arguments = {
        "file_path": file_path,
        "commit_message": commit_message
    }
    
    handler_result = await handle_commit_file(arguments)
    return handler_result[0].text if handler_result and hasattr(handler_result[0], 'text') else str(handler_result)

@version_control_service.tool(
    description="📜 Get a previous version of a file from version control history",
    tags={"version", "control", "history", "retrieve", "previous"}
)
async def get_previous_file_version(
    file_path: Annotated[str, Field(description="Path to the file to retrieve previous version")],
    version: Annotated[str, Field(description="Version identifier (commit hash, tag, or relative reference like 'HEAD~1')")]
) -> str:
    """Get a previous version of a file."""
    arguments = {
        "file_path": file_path,
        "version": version
    }
    
    handler_result = await handle_get_previous_file_version(arguments)
    return handler_result[0].text if handler_result and hasattr(handler_result[0], 'text') else str(handler_result)
