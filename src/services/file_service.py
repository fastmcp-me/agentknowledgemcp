"""
File Operations Service for FastMCP server composition.
Contains all file system operation tools with enhanced parameter descriptions.
"""
from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

# Import existing handlers
from ..file_handlers import (
    handle_read_file, handle_write_file, handle_delete_file,
    handle_list_directory, handle_create_directory, handle_delete_directory,
    handle_file_info, handle_move_file, handle_copy_file, handle_append_file
)

# Create File Operations service
file_service = FastMCP(
    name="FileOperationsService", 
    instructions="File system operations service for reading, writing, and managing files and directories"
)

@file_service.tool(
    description="📖 Read content from a file with specified encoding",
    tags={"file", "read", "content", "text"}
)
async def read_file(
    file_path: Annotated[str, Field(description="Absolute or relative path to the file to read")],
    encoding: Annotated[str, Field(description="Text encoding format (utf-8, ascii, etc.)")] = "utf-8"
) -> str:
    """Read content from a file."""
    arguments = {
        "file_path": file_path,
        "encoding": encoding
    }
    result = await handle_read_file(arguments)
    return result[0].text if result and hasattr(result[0], 'text') else str(result)

@file_service.tool(
    description="✍️ Write content to a file (creates new or overwrites existing)",
    tags={"file", "write", "content", "create"}
)
async def write_file(
    file_path: Annotated[str, Field(description="Absolute or relative path to the file to write")],
    content: Annotated[str, Field(description="Content to write to the file")],
    encoding: Annotated[str, Field(description="Text encoding format for writing")] = "utf-8",
    create_dirs: Annotated[bool, Field(description="Whether to create parent directories if they don't exist")] = True
) -> str:
    """Write content to a file (creates new or overwrites existing)."""
    arguments = {
        "file_path": file_path,
        "content": content,
        "encoding": encoding,
        "create_dirs": create_dirs
    }
    
    handler_result = await handle_write_file(arguments)
    return handler_result[0].text if handler_result and hasattr(handler_result[0], 'text') else str(handler_result)

@file_service.tool(
    description="➕ Append content to an existing file without overwriting",
    tags={"file", "append", "content", "add"}
)
async def append_file(
    file_path: Annotated[str, Field(description="Path to the file to append content to")],
    content: Annotated[str, Field(description="Content to append to the file")],
    encoding: Annotated[str, Field(description="Text encoding format")] = "utf-8"
) -> str:
    """Append content to an existing file."""
    arguments = {
        "file_path": file_path,
        "content": content,
        "encoding": encoding
    }
    
    handler_result = await handle_append_file(arguments)
    return handler_result[0].text if handler_result and hasattr(handler_result[0], 'text') else str(handler_result)

@file_service.tool(
    description="🗑️ Delete a file from the file system",
    tags={"file", "delete", "remove", "destructive"}
)
async def delete_file(
    file_path: Annotated[str, Field(description="Path to the file to delete")]
) -> str:
    """Delete a file."""
    arguments = {
        "file_path": file_path
    }
    
    handler_result = await handle_delete_file(arguments)
    return handler_result[0].text if handler_result and hasattr(handler_result[0], 'text') else str(handler_result)

@file_service.tool(
    description="📁 Move or rename a file from source to destination",
    tags={"file", "move", "rename", "relocate"}
)
async def move_file(
    source_path: Annotated[str, Field(description="Current path of the file to move")],
    destination_path: Annotated[str, Field(description="New path where the file will be moved")]
) -> str:
    """Move or rename a file."""
    arguments = {
        "source_path": source_path,
        "destination_path": destination_path
    }
    
    handler_result = await handle_move_file(arguments)
    return handler_result[0].text if handler_result and hasattr(handler_result[0], 'text') else str(handler_result)

@file_service.tool(
    description="📋 Copy a file from source to destination",
    tags={"file", "copy", "duplicate", "backup"}
)
async def copy_file(
    source_path: Annotated[str, Field(description="Path of the file to copy")],
    destination_path: Annotated[str, Field(description="Path where the copy will be created")]
) -> str:
    """Copy a file."""
    arguments = {
        "source_path": source_path,
        "destination_path": destination_path
    }
    
    handler_result = await handle_copy_file(arguments)
    return handler_result[0].text if handler_result and hasattr(handler_result[0], 'text') else str(handler_result)

@file_service.tool(
    description="📂 List contents of a directory",
    tags={"directory", "list", "contents", "files"}
)
async def list_directory(
    directory_path: Annotated[str, Field(description="Path to the directory to list")],
    recursive: Annotated[bool, Field(description="Whether to list contents recursively")] = False
) -> str:
    """List directory contents."""
    arguments = {
        "directory_path": directory_path,
        "recursive": recursive
    }
    
    handler_result = await handle_list_directory(arguments)
    return handler_result[0].text if handler_result and hasattr(handler_result[0], 'text') else str(handler_result)

@file_service.tool(
    description="🏗️ Create a new directory",
    tags={"directory", "create", "mkdir", "folder"}
)
async def create_directory(
    directory_path: Annotated[str, Field(description="Path of the directory to create")],
    parents: Annotated[bool, Field(description="Whether to create parent directories if they don't exist")] = True
) -> str:
    """Create a new directory."""
    arguments = {
        "directory_path": directory_path,
        "parents": parents
    }
    
    handler_result = await handle_create_directory(arguments)
    return handler_result[0].text if handler_result and hasattr(handler_result[0], 'text') else str(handler_result)

@file_service.tool(
    description="🗂️ Delete a directory and optionally its contents",
    tags={"directory", "delete", "remove", "destructive"}
)
async def delete_directory(
    directory_path: Annotated[str, Field(description="Path of the directory to delete")],
    recursive: Annotated[bool, Field(description="Whether to delete directory contents recursively")] = False
) -> str:
    """Delete a directory."""
    arguments = {
        "directory_path": directory_path,
        "recursive": recursive
    }
    
    handler_result = await handle_delete_directory(arguments)
    return handler_result[0].text if handler_result and hasattr(handler_result[0], 'text') else str(handler_result)

@file_service.tool(
    description="ℹ️ Get detailed information about a file or directory",
    tags={"file", "info", "metadata", "stats"}
)
async def file_info(
    path: Annotated[str, Field(description="Path to the file or directory to get information about")]
) -> str:
    """Get file or directory information."""
    arguments = {
        "path": path
    }
    
    handler_result = await handle_file_info(arguments)
    return handler_result[0].text if handler_result and hasattr(handler_result[0], 'text') else str(handler_result)
