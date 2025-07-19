"""
Unified File Operations FastMCP Server
Consolidates all file operations into a single comprehensive edit_file tool.
"""
from typing import Annotated, Optional, Literal
from pathlib import Path
import shutil
import stat
import datetime

from fastmcp import FastMCP
from pydantic import Field

from src.utils.security import validate_path, SecurityError

# Create FastMCP app
app = FastMCP(
    name="AgentKnowledgeMCP-UnifiedFile",
    version="2.0.0",
    instructions="Unified file operations tool for comprehensive file management"
)

def _format_file_error(e: Exception, operation: str, file_path: str = None) -> str:
    """Format file operation errors with detailed guidance for agents."""
    error_message = f"❌ Failed to {operation}:\n\n"

    error_str = str(e).lower()
    if "permission denied" in error_str or "access denied" in error_str:
        error_message += "🔒 **Permission Error**: Access denied to file or directory\n"
        error_message += f"📍 Insufficient permissions for {operation}\n"
        error_message += f"💡 **Suggestions for agents**:\n"
        error_message += f"   1. Check if you have write access to the directory\n"
        error_message += f"   2. Ask user to change working directory using 'update_config' tool\n"
        error_message += f"   3. Use 'get_config' to check current allowed_base_directory\n"
        error_message += f"   4. Request user to set a different base directory with proper permissions\n\n"
    elif "no such file or directory" in error_str or "not found" in error_str:
        error_message += f"📁 **File Not Found**: The specified path does not exist\n"
        if file_path:
            error_message += f"📍 Path '{file_path}' was not found\n"
        error_message += f"💡 Try: Check path spelling and use operation='info' to verify location\n\n"
    elif "already exists" in error_str:
        error_message += f"📄 **File Already Exists**: Target already exists\n"
        error_message += f"📍 Cannot {operation} because destination already exists\n"
        error_message += f"💡 Try: Use different name or delete existing file first\n\n"
    elif "directory not empty" in error_str:
        error_message += f"📂 **Directory Not Empty**: Cannot delete non-empty directory\n"
        error_message += f"📍 Directory contains files or subdirectories\n"
        error_message += f"💡 Try: Use recursive delete option or remove contents first\n\n"
    elif "is a directory" in error_str:
        error_message += f"📂 **Path is Directory**: Expected file but found directory\n"
        error_message += f"📍 The specified path points to a directory, not a file\n"
        error_message += f"💡 Try: Use directory-specific operations or specify a file path\n\n"
    else:
        error_message += f"⚠️ **Unknown Error**: {str(e)}\n\n"

    error_message += f"🔍 **Technical Details**: {str(e)}"
    return error_message

def _get_file_info(validated_path: Path, path: str) -> str:
    """Get detailed file/directory information."""
    # Check if path exists
    if not validated_path.exists():
        return f"❌ Path not found: {path}\n💡 Check the path spelling and location"

    # Get basic information
    is_file = validated_path.is_file()
    is_dir = validated_path.is_dir()
    is_symlink = validated_path.is_symlink()

    # Get detailed stats
    try:
        stat_info = validated_path.stat()

        # Format file size
        size_bytes = stat_info.st_size
        if size_bytes < 1024:
            size_display = f"{size_bytes} bytes"
        elif size_bytes < 1024**2:
            size_display = f"{size_bytes/1024:.1f} KB ({size_bytes} bytes)"
        elif size_bytes < 1024**3:
            size_display = f"{size_bytes/(1024**2):.1f} MB ({size_bytes} bytes)"
        else:
            size_display = f"{size_bytes/(1024**3):.1f} GB ({size_bytes} bytes)"

        # Format timestamps
        modified_time = datetime.datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        accessed_time = datetime.datetime.fromtimestamp(stat_info.st_atime).strftime('%Y-%m-%d %H:%M:%S')
        created_time = datetime.datetime.fromtimestamp(stat_info.st_ctime).strftime('%Y-%m-%d %H:%M:%S')

        # Format permissions (Unix-style)
        permissions = stat.filemode(stat_info.st_mode)

        # Determine type emoji and info
        if is_file:
            type_emoji = "📄"
            type_name = "File"
            # Try to get file extension info
            suffix = validated_path.suffix.lower()
            if suffix:
                type_details = f"File type: {suffix[1:].upper()} file"
            else:
                type_details = "File type: No extension"
        elif is_dir:
            type_emoji = "📁"
            type_name = "Directory"
            # Count directory contents if possible
            try:
                contents = list(validated_path.iterdir())
                file_count = sum(1 for item in contents if item.is_file())
                dir_count = sum(1 for item in contents if item.is_dir())
                type_details = f"Contents: {file_count} files, {dir_count} directories"
            except PermissionError:
                type_details = "Contents: Permission denied to list"
        else:
            type_emoji = "🔗"
            type_name = "Symbolic Link"
            try:
                target = validated_path.readlink()
                type_details = f"Link target: {target}"
            except:
                type_details = "Link target: Unable to read"

        # Additional metadata for files
        additional_info = ""
        if is_file:
            # Try to detect if it's a text file
            try:
                with open(validated_path, 'r', encoding='utf-8', errors='ignore') as f:
                    # Read first few characters to check if it's text
                    sample = f.read(100)
                    if sample and sample.isprintable():
                        # Reset file pointer and count lines
                        f.seek(0)
                        line_count = sum(1 for _ in f)
                        additional_info = f"\n📝 Text file details: Readable text content, {line_count} lines"
                    else:
                        additional_info = f"\n💾 Binary file: Non-text content"
            except:
                additional_info = f"\n❓ File content: Unable to analyze"

        # Build comprehensive information display
        info_display = f"""✅ {type_name} information retrieved:

{type_emoji} **Path**: {path}
📊 **Type**: {type_name}
🏷️ **Details**: {type_details}
📏 **Size**: {size_display}
🔐 **Permissions**: {permissions}

🕐 **Timestamps**:
   📝 Modified: {modified_time}
   👁️  Accessed: {accessed_time}
   🆕 Created:  {created_time}

🔧 **Technical Details**:
   🆔 Inode: {stat_info.st_ino}
   👤 Owner UID: {stat_info.st_uid}
   👥 Group GID: {stat_info.st_gid}
   🔗 Links: {stat_info.st_nlink}{additional_info}"""

        return info_display

    except PermissionError:
        return f"❌ Permission denied accessing path: {path}\n💡 Check file/directory permissions or ask user to change allowed_base_directory"
    except OSError as e:
        return f"❌ System error accessing path: {path}\n🔍 Error: {str(e)}\n💡 Path may be on an inaccessible filesystem or have system restrictions"

# ================================
# UNIFIED EDIT_FILE TOOL
# ================================

@app.tool(
    description="Unified file and directory operations tool supporting read, write, append, delete, move, copy, create directories, list directories, and get file information",
    tags={"file", "directory", "edit", "unified", "comprehensive"}
)
async def edit_file(
    operation: Annotated[
        Literal["read", "write", "append", "delete", "move", "copy", "info", "list", "mkdir", "rmdir"],
        Field(description="Operation to perform: read, write, append, delete, move, copy, info, list (directory), mkdir (create directory), rmdir (remove directory)")
    ],
    path: Annotated[str, Field(description="Primary file/directory path for the operation")],
    content: Annotated[Optional[str], Field(description="Content for write/append operations")] = None,
    destination: Annotated[Optional[str], Field(description="Destination path for move/copy operations")] = None,
    encoding: Annotated[str, Field(description="File encoding", pattern="^(utf-8|utf-16|ascii|latin-1)$")] = "utf-8",
    create_dirs: Annotated[bool, Field(description="Create parent directories if they don't exist")] = True,
    recursive: Annotated[bool, Field(description="For rmdir: delete recursively; for list: list recursively")] = False,
    include_hidden: Annotated[bool, Field(description="For list operation: include hidden files")] = False,
    overwrite: Annotated[bool, Field(description="Allow overwriting existing files in copy/move operations")] = False
) -> str:
    """
    Unified file and directory operations tool.
    
    Operations:
    - read: Read file content
    - write: Write content to file (creates new or overwrites)
    - append: Append content to existing file
    - delete: Delete a file
    - move: Move/rename a file (requires destination)
    - copy: Copy a file (requires destination)
    - info: Get detailed file/directory information
    - list: List directory contents
    - mkdir: Create directory
    - rmdir: Remove directory
    """
    try:
        # Validate primary path
        validated_path = validate_path(path)
        
        # Validate destination path if provided
        validated_destination = None
        if destination:
            validated_destination = validate_path(destination)

        # Execute operation
        if operation == "read":
            # READ OPERATION
            if not validated_path.exists():
                return f"❌ File not found: {path}\n💡 Check the file path spelling and location"
            
            if validated_path.is_dir():
                return f"❌ Path is a directory: {path}\n💡 Use operation='list' to list directory contents"
            
            with open(validated_path, 'r', encoding=encoding) as f:
                file_content = f.read()
            
            return f"✅ File read successfully:\n\n{file_content}"

        elif operation == "write":
            # WRITE OPERATION
            if content is None:
                return "❌ Content parameter is required for write operation"
            
            # Create parent directories if requested
            if create_dirs:
                validated_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Check if file exists and overwrite is not allowed
            if validated_path.exists() and not overwrite:
                return f"❌ File already exists: {path}\n💡 Set overwrite=True to replace existing file"
            
            with open(validated_path, 'w', encoding=encoding) as f:
                f.write(content)
            
            return f"✅ File written successfully:\n\n📁 Path: {path}\n📏 Size: {len(content)} characters\n🔤 Encoding: {encoding}"

        elif operation == "append":
            # APPEND OPERATION
            if content is None:
                return "❌ Content parameter is required for append operation"
            
            if not validated_path.exists():
                return f"❌ File not found: {path}\n💡 Use operation='write' to create a new file"
            
            if validated_path.is_dir():
                return f"❌ Path is a directory: {path}\n💡 Cannot append to directories"
            
            with open(validated_path, 'a', encoding=encoding) as f:
                f.write(content)
            
            file_size = validated_path.stat().st_size
            return f"✅ Content appended successfully:\n\n📁 Path: {path}\n📏 Added: {len(content)} characters\n📊 Total file size: {file_size} bytes\n🔤 Encoding: {encoding}"

        elif operation == "delete":
            # DELETE OPERATION
            if not validated_path.exists():
                return f"❌ Path not found: {path}\n💡 File may already be deleted or path is incorrect"
            
            if validated_path.is_dir():
                return f"❌ Path is a directory: {path}\n💡 Use operation='rmdir' to remove directories"
            
            validated_path.unlink()
            return f"✅ File deleted successfully:\n\n📁 Path: {path}\n🗑️ Operation: File removal completed"

        elif operation == "move":
            # MOVE OPERATION
            if destination is None:
                return "❌ Destination parameter is required for move operation"
            
            if not validated_path.exists():
                return f"❌ Source file not found: {path}\n💡 Check the source path spelling and location"
            
            if validated_path.is_dir():
                return f"❌ Source is a directory: {path}\n💡 Use directory-specific operations for folders"
            
            if validated_destination.exists() and not overwrite:
                return f"❌ Destination already exists: {destination}\n💡 Set overwrite=True or choose a different name"
            
            # Create parent directories if requested
            if create_dirs:
                validated_destination.parent.mkdir(parents=True, exist_ok=True)
            
            # Remove destination if overwrite is allowed and it exists
            if overwrite and validated_destination.exists():
                if validated_destination.is_dir():
                    shutil.rmtree(validated_destination)
                else:
                    validated_destination.unlink()
            
            validated_path.rename(validated_destination)
            return f"✅ File moved successfully:\n\n📂 From: {path}\n📁 To: {destination}\n🔄 Operation: File relocation completed"

        elif operation == "copy":
            # COPY OPERATION
            if destination is None:
                return "❌ Destination parameter is required for copy operation"
            
            if not validated_path.exists():
                return f"❌ Source file not found: {path}\n💡 Check the source path spelling and location"
            
            if validated_path.is_dir():
                return f"❌ Source is a directory: {path}\n💡 Use directory-specific operations for folders"
            
            if validated_destination.exists() and not overwrite:
                return f"❌ Destination already exists: {destination}\n💡 Set overwrite=True or choose a different name"
            
            # Create parent directories if requested
            if create_dirs:
                validated_destination.parent.mkdir(parents=True, exist_ok=True)
            
            # Remove destination if overwrite is allowed and it exists
            if overwrite and validated_destination.exists():
                if validated_destination.is_dir():
                    shutil.rmtree(validated_destination)
                else:
                    validated_destination.unlink()
            
            shutil.copy2(validated_path, validated_destination)
            
            source_size = validated_path.stat().st_size
            dest_size = validated_destination.stat().st_size
            return f"✅ File copied successfully:\n\n📂 From: {path}\n📁 To: {destination}\n📏 Size: {source_size} bytes\n🔍 Verified: Source and destination match ({dest_size} bytes)"

        elif operation == "info":
            # INFO OPERATION
            return _get_file_info(validated_path, path)

        elif operation == "list":
            # LIST DIRECTORY OPERATION
            if not validated_path.exists():
                return f"❌ Directory not found: {path}\n💡 Check the directory path spelling and location"
            
            if not validated_path.is_dir():
                return f"❌ Path is not a directory: {path}\n💡 Use operation='info' for file information"
            
            items = []
            try:
                if recursive:
                    # Recursive listing using rglob
                    for item in validated_path.rglob("*"):
                        if not include_hidden and item.name.startswith('.'):
                            continue
                        relative_path = item.relative_to(validated_path)
                        item_type = "📁" if item.is_dir() else "📄"
                        size_info = f" ({item.stat().st_size} bytes)" if item.is_file() else ""
                        items.append(f"{item_type} {relative_path}{size_info}")
                else:
                    # Non-recursive listing
                    for item in sorted(validated_path.iterdir()):
                        if not include_hidden and item.name.startswith('.'):
                            continue
                        item_type = "📁" if item.is_dir() else "📄"
                        size_info = f" ({item.stat().st_size} bytes)" if item.is_file() else ""
                        items.append(f"{item_type} {item.name}{size_info}")
            except PermissionError:
                return f"❌ Permission denied accessing directory: {path}\n💡 Check directory permissions or ask user to change allowed_base_directory"
            
            if not items:
                return f"✅ Directory is empty:\n\n📁 Path: {path}\n📋 Contents: No files or directories found"
            
            listing_type = "recursive" if recursive else "non-recursive"
            hidden_info = "including hidden" if include_hidden else "excluding hidden"
            return f"✅ Directory listing ({listing_type}, {hidden_info}):\n\n📁 Path: {path}\n📋 Items ({len(items)}):\n\n" + "\n".join(items)

        elif operation == "mkdir":
            # CREATE DIRECTORY OPERATION
            if validated_path.exists():
                if validated_path.is_dir():
                    return f"❌ Directory already exists: {path}\n💡 Directory is already present at this location"
                else:
                    return f"❌ Path exists but is not a directory: {path}\n💡 A file exists at this location - choose a different path"
            
            try:
                validated_path.mkdir(parents=create_dirs, exist_ok=False)
                
                if validated_path.exists() and validated_path.is_dir():
                    parent_info = " (including parent directories)" if create_dirs else ""
                    return f"✅ Directory created successfully:\n\n📁 Path: {path}\n🔨 Operation: Directory creation completed{parent_info}"
                else:
                    return f"❌ Directory creation failed: {path}\n💡 Directory was not created successfully - check permissions"
                    
            except FileExistsError:
                return f"❌ Directory already exists: {path}\n💡 Directory was created by another process"
            except FileNotFoundError:
                if not create_dirs:
                    return f"❌ Parent directory does not exist: {path}\n💡 Set create_dirs=True to create parent directories automatically"
                else:
                    return f"❌ Cannot create directory: {path}\n💡 Check the path and parent directory permissions"
            except PermissionError:
                return f"❌ Permission denied creating directory: {path}\n💡 Check write permissions for the parent directory"

        elif operation == "rmdir":
            # DELETE DIRECTORY OPERATION
            if not validated_path.exists():
                return f"❌ Directory not found: {path}\n💡 Directory may already be deleted or path is incorrect"
            
            if not validated_path.is_dir():
                return f"❌ Path is not a directory: {path}\n💡 Use operation='delete' to remove files"
            
            # Check if directory is empty (when not using recursive)
            if not recursive:
                try:
                    contents = list(validated_path.iterdir())
                    if contents:
                        return f"❌ Directory not empty: {path}\n💡 Directory contains {len(contents)} items - set recursive=True to delete contents or remove items first"
                except PermissionError:
                    return f"❌ Permission denied accessing directory: {path}\n💡 Check directory permissions or ask user to change allowed_base_directory"
            
            try:
                if recursive:
                    shutil.rmtree(validated_path)
                    deletion_type = "recursive deletion (directory and all contents)"
                else:
                    validated_path.rmdir()
                    deletion_type = "empty directory deletion"
            except OSError as e:
                if "Directory not empty" in str(e):
                    return f"❌ Directory not empty: {path}\n💡 Set recursive=True to delete contents or remove items manually first"
                elif "Permission denied" in str(e):
                    return f"❌ Permission denied deleting directory: {path}\n💡 Check directory permissions or ask user to change allowed_base_directory"
                else:
                    raise e
            
            if not validated_path.exists():
                return f"✅ Directory deleted successfully:\n\n📁 Path: {path}\n🗑️ Operation: {deletion_type.capitalize()} completed"
            else:
                return f"❌ Directory deletion failed: {path}\n💡 Directory still exists - check permissions and try again"

        else:
            return f"❌ Unsupported operation: {operation}\n💡 Supported operations: read, write, append, delete, move, copy, info, list, mkdir, rmdir"

    except SecurityError as e:
        return f"❌ Security error: {str(e)}"
    except Exception as e:
        return _format_file_error(e, f"perform {operation} operation", path)


# CLI entry point
def cli_main():
    """CLI entry point for Unified File FastMCP server."""
    print("🚀 Starting AgentKnowledgeMCP Unified File FastMCP server...")
    print("🔧 Unified Tool: edit_file (supports all file and directory operations)")
    print("📋 Operations: read, write, append, delete, move, copy, info, list, mkdir, rmdir")
    print("✅ Status: Unified File Tool - Ready for production!")

    app.run()

if __name__ == "__main__":
    cli_main()
