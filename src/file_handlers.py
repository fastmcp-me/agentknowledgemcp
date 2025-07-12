"""
File system tool handlers.
"""
import json
import os
import shutil
from pathlib import Path
from typing import List, Dict, Any

import mcp.types as types
from .security import get_safe_path, is_path_allowed, get_allowed_base_dir
from .config import load_config


def _format_file_error(operation: str, file_path: str, error: Exception) -> str:
    """Format enhanced error messages for file operations with specific guidance."""
    error_str = str(error).lower()
    error_message = f"❌ {operation} failed for '{file_path}':\n\n"
    
    if "permission" in error_str or "access" in error_str or "denied" in error_str:
        error_message += "🔒 **Permission Error**: Access denied to file or directory\n"
        error_message += f"📍 Insufficient permissions for {operation.lower()}\n"
        error_message += f"💡 **Suggestions for agents**:\n"
        error_message += f"   1. Check if you have write access to the directory\n"
        error_message += f"   2. Ask user to change working directory using 'update_config' tool\n"
        error_message += f"   3. Use 'get_config' to check current allowed_base_directory\n"
        error_message += f"   4. Request user to set a different base directory with proper permissions\n\n"
    elif "not found" in error_str or "no such file" in error_str:
        error_message += f"📁 **File Not Found**: The specified path does not exist\n"
        error_message += f"📍 File or directory not found: {file_path}\n"
        error_message += f"💡 Check the path and ensure it exists\n\n"
    elif "directory" in error_str and "not empty" in error_str:
        error_message += f"📂 **Directory Not Empty**: Cannot delete non-empty directory\n"
        error_message += f"📍 Directory contains files or subdirectories\n"
        error_message += f"💡 Use recursive=true parameter to delete directory and contents\n\n"
    elif "exists" in error_str:
        error_message += f"📄 **File Exists**: File or directory already exists\n"
        error_message += f"📍 Cannot create because path already exists\n"
        error_message += f"💡 Choose a different name or delete existing file first\n\n"
    elif "outside allowed" in error_str:
        error_message += f"🚫 **Security Error**: Path is outside allowed directory\n"
        error_message += f"📍 File operations are restricted to the configured base directory\n"
        error_message += f"💡 **Suggestions for agents**:\n"
        error_message += f"   1. Ask user about expanding allowed directory with 'update_config' tool\n"
        error_message += f"   2. Use 'get_config' to see current security settings\n"
        error_message += f"   3. Request user to change allowed_base_directory setting\n\n"
    else:
        error_message += f"⚠️ **Unknown Error**: {str(error)}\n\n"
    
    error_message += f"🔍 **Technical Details**: {str(error)}"
    return error_message


async def handle_read_file(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle read_file tool."""
    file_path = arguments.get("file_path")
    encoding = arguments.get("encoding", "utf-8")
    
    try:
        path_obj = get_safe_path(file_path)
        
        if not path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(path_obj, 'r', encoding=encoding) as f:
            content = f.read()
        
        return [
            types.TextContent(
                type="text",
                text=f"Content of '{file_path}':\n\n{content}"
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=_format_file_error("Read", file_path, e)
            )
        ]


async def handle_write_file(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle write_file tool."""
    file_path = arguments.get("file_path")
    content = arguments.get("content")
    encoding = arguments.get("encoding", "utf-8")
    create_dirs = arguments.get("create_dirs", True)
    
    try:
        path_obj = get_safe_path(file_path)
        
        if create_dirs:
            path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path_obj, 'w', encoding=encoding) as f:
            f.write(content)
        
        return [
            types.TextContent(
                type="text",
                text=f"File '{file_path}' written successfully. Size: {len(content)} characters."
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=_format_file_error("Write", file_path, e)
            )
        ]


async def handle_append_file(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle append_file tool."""
    file_path = arguments.get("file_path")
    content = arguments.get("content")
    encoding = arguments.get("encoding", "utf-8")
    
    try:
        path_obj = get_safe_path(file_path)
        
        with open(path_obj, 'a', encoding=encoding) as f:
            f.write(content)
        
        return [
            types.TextContent(
                type="text",
                text=f"Content appended to '{file_path}' successfully. Added: {len(content)} characters."
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=_format_file_error("Append", file_path, e)
            )
        ]


async def handle_delete_file(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle delete_file tool."""
    file_path = arguments.get("file_path")
    
    try:
        path_obj = get_safe_path(file_path)
        
        if not path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if path_obj.is_file():
            path_obj.unlink()
            return [
                types.TextContent(
                    type="text",
                    text=f"File '{file_path}' deleted successfully."
                )
            ]
        else:
            raise IsADirectoryError(f"'{file_path}' is a directory, not a file.")
            
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=_format_file_error("Delete", file_path, e)
            )
        ]


async def handle_move_file(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle move_file tool."""
    source_path = arguments.get("source_path")
    destination_path = arguments.get("destination_path")
    create_dirs = arguments.get("create_dirs", True)
    
    try:
        source_obj = get_safe_path(source_path)
        dest_obj = get_safe_path(destination_path)
        
        if not source_obj.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")
        
        if create_dirs:
            dest_obj.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.move(str(source_obj), str(dest_obj))
        
        return [
            types.TextContent(
                type="text",
                text=f"File moved successfully from '{source_path}' to '{destination_path}'"
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=_format_file_error("Move", source_path, e)
            )
        ]


async def handle_copy_file(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle copy_file tool."""
    source_path = arguments.get("source_path")
    destination_path = arguments.get("destination_path")
    create_dirs = arguments.get("create_dirs", True)
    
    try:
        source_obj = get_safe_path(source_path)
        dest_obj = get_safe_path(destination_path)
        
        if not source_obj.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")
        
        if create_dirs:
            dest_obj.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copy2(str(source_obj), str(dest_obj))
        
        return [
            types.TextContent(
                type="text",
                text=f"File copied successfully from '{source_path}' to '{destination_path}'"
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=_format_file_error("Copy", source_path, e)
            )
        ]


async def handle_list_directory(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle list_directory tool."""
    directory_path = arguments.get("directory_path")
    include_hidden = arguments.get("include_hidden", False)
    recursive = arguments.get("recursive", False)
    
    try:
        path_obj = get_safe_path(directory_path)
        
        if not path_obj.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        if not path_obj.is_dir():
            raise NotADirectoryError(f"'{directory_path}' is not a directory")
        
        items = []
        
        if recursive:
            pattern = "**/*" if include_hidden else "**/[!.]*"
            for item in path_obj.glob(pattern):
                # Double check each item is still within allowed directory
                if is_path_allowed(str(item)):
                    relative_path = item.relative_to(path_obj)
                    items.append({
                        "name": str(relative_path),
                        "type": "directory" if item.is_dir() else "file",
                        "size": item.stat().st_size if item.is_file() else None
                    })
        else:
            for item in path_obj.iterdir():
                if not include_hidden and item.name.startswith('.'):
                    continue
                items.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None
                })
        
        return [
            types.TextContent(
                type="text",
                text=f"Contents of '{directory_path}' (limited to {get_allowed_base_dir()}):\n\n{json.dumps(items, indent=2)}"
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=_format_file_error("List", directory_path, e)
            )
        ]


async def handle_create_directory(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle create_directory tool."""
    directory_path = arguments.get("directory_path")
    parents = arguments.get("parents", True)
    
    try:
        path_obj = get_safe_path(directory_path)
        path_obj.mkdir(parents=parents, exist_ok=False)
        
        return [
            types.TextContent(
                type="text",
                text=f"Directory '{directory_path}' created successfully."
            )
        ]
    except FileExistsError:
        return [
            types.TextContent(
                type="text",
                text=f"Directory '{directory_path}' already exists."
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=_format_file_error("Create", directory_path, e)
            )
        ]


async def handle_delete_directory(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle delete_directory tool."""
    directory_path = arguments.get("directory_path")
    recursive = arguments.get("recursive", False)
    
    try:
        path_obj = get_safe_path(directory_path)
        
        if not path_obj.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        if not path_obj.is_dir():
            raise NotADirectoryError(f"'{directory_path}' is not a directory")
        
        # Extra safety: don't allow deleting the base directory itself
        if path_obj.resolve() == get_allowed_base_dir():
            raise ValueError("Cannot delete the base allowed directory")
        
        if recursive:
            shutil.rmtree(str(path_obj))
            message = f"Directory '{directory_path}' and all its contents deleted successfully."
        else:
            path_obj.rmdir()  # Only works if directory is empty
            message = f"Empty directory '{directory_path}' deleted successfully."
        
        return [
            types.TextContent(
                type="text",
                text=message
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=_format_file_error("Delete", directory_path, e)
            )
        ]


async def handle_file_info(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle file_info tool."""
    path = arguments.get("path")
    
    try:
        path_obj = get_safe_path(path)
        
        if not path_obj.exists():
            raise FileNotFoundError(f"Path not found: {path}")
        
        stat = path_obj.stat()
        info = {
            "path": str(path_obj.absolute()),
            "name": path_obj.name,
            "type": "directory" if path_obj.is_dir() else "file",
            "size": stat.st_size,
            "created": stat.st_ctime,
            "modified": stat.st_mtime,
            "permissions": oct(stat.st_mode)[-3:],
            "is_readable": os.access(path_obj, os.R_OK),
            "is_writable": os.access(path_obj, os.W_OK),
            "is_executable": os.access(path_obj, os.X_OK),
            "allowed_base_dir": str(get_allowed_base_dir())
        }
        
        if path_obj.is_file():
            info["extension"] = path_obj.suffix
        
        return [
            types.TextContent(
                type="text",
                text=f"Information for '{path}' (within allowed directory):\n\n{json.dumps(info, indent=2)}"
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=_format_file_error("Info", path, e)
            )
        ]
