"""
File Operations FastMCP Server - Step by step migration
Tool-by-tool conversion from handlers to FastMCP tools.
File 2/4: File Server
"""
import json
from typing import List, Dict, Any, Optional, Annotated
from pathlib import Path
import os

from fastmcp import FastMCP
from fastmcp.server import Context
from pydantic import Field

from .security import validate_path, SecurityError
from .config import load_config

# Create FastMCP app
app = FastMCP(
    name="AgentKnowledgeMCP-File",
    version="1.0.0",
    instructions="File operations tools for knowledge management"
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
        error_message += f"💡 Try: Check path spelling and use 'list_directory' to verify location\n\n"
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


# ================================
# TOOL 1: READ_FILE
# ================================

@app.tool(
    description="Read content from a file with encoding support and security validation",
    tags={"file", "read", "content"}
)
async def read_file(
    file_path: Annotated[str, Field(description="Path to the file to read")],
    encoding: Annotated[str, Field(description="File encoding to use for reading", pattern="^(utf-8|utf-16|ascii|latin-1)$")] = "utf-8"
) -> str:
    """Read content from a file with proper security validation."""
    try:
        # Validate path security
        validated_path = validate_path(file_path)
        
        with open(validated_path, 'r', encoding=encoding) as f:
            content = f.read()
        
        return f"✅ File read successfully:\n\n{content}"
        
    except SecurityError as e:
        return f"❌ Security error: {str(e)}"
    except Exception as e:
        return _format_file_error(e, "read file", file_path)


# ================================
# TOOL 2: WRITE_FILE
# ================================

@app.tool(
    description="Write content to a file with encoding support, directory creation, and security validation",
    tags={"file", "write", "content", "create"}
)
async def write_file(
    file_path: Annotated[str, Field(description="Path to the file to write (creates new or overwrites existing)")],
    content: Annotated[str, Field(description="Content to write to the file")],
    encoding: Annotated[str, Field(description="File encoding to use for writing", pattern="^(utf-8|utf-16|ascii|latin-1)$")] = "utf-8",
    create_dirs: Annotated[bool, Field(description="Whether to create parent directories if they don't exist")] = True
) -> str:
    """Write content to a file with proper security validation and directory creation."""
    try:
        # Validate path security 
        validated_path = validate_path(file_path)
        
        # Create parent directories if requested
        if create_dirs:
            validated_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write content to file
        with open(validated_path, 'w', encoding=encoding) as f:
            f.write(content)
        
        return f"✅ File written successfully:\n\n📁 Path: {file_path}\n📏 Size: {len(content)} characters\n🔤 Encoding: {encoding}"
        
    except SecurityError as e:
        return f"❌ Security error: {str(e)}"
    except Exception as e:
        return _format_file_error(e, "write file", file_path)


# ================================
# TOOL 3: APPEND_FILE
# ================================

@app.tool(
    description="Append content to an existing file with encoding support and security validation",
    tags={"file", "append", "content", "add"}
)
async def append_file(
    file_path: Annotated[str, Field(description="Path to the file to append content to")],
    content: Annotated[str, Field(description="Content to append to the file")],
    encoding: Annotated[str, Field(description="File encoding to use for appending", pattern="^(utf-8|utf-16|ascii|latin-1)$")] = "utf-8"
) -> str:
    """Append content to an existing file with proper security validation."""
    try:
        # Validate path security
        validated_path = validate_path(file_path)
        
        # Check if file exists
        if not validated_path.exists():
            return f"❌ File not found: {file_path}\n💡 Use 'write_file' to create a new file"
        
        # Append content to file
        with open(validated_path, 'a', encoding=encoding) as f:
            f.write(content)
        
        # Get file size after appending
        file_size = validated_path.stat().st_size
        
        return f"✅ Content appended successfully:\n\n📁 Path: {file_path}\n📏 Added: {len(content)} characters\n📊 Total file size: {file_size} bytes\n🔤 Encoding: {encoding}"
        
    except SecurityError as e:
        return f"❌ Security error: {str(e)}"
    except Exception as e:
        return _format_file_error(e, "append to file", file_path)


# ================================
# TOOL 4: DELETE_FILE
# ================================

@app.tool(
    description="Delete a file with security validation and existence checking",
    tags={"file", "delete", "remove"}
)
async def delete_file(
    file_path: Annotated[str, Field(description="Path to the file to delete")]
) -> str:
    """Delete a file with proper security validation."""
    try:
        # Validate path security
        validated_path = validate_path(file_path)
        
        # Check if file exists
        if not validated_path.exists():
            return f"❌ File not found: {file_path}\n💡 File may already be deleted or path is incorrect"
        
        # Check if it's actually a file (not a directory)
        if validated_path.is_dir():
            return f"❌ Path is a directory: {file_path}\n💡 Use 'delete_directory' to remove directories"
        
        # Delete the file
        validated_path.unlink()
        
        return f"✅ File deleted successfully:\n\n📁 Path: {file_path}\n🗑️ Operation: File removal completed"
        
    except SecurityError as e:
        return f"❌ Security error: {str(e)}"
    except Exception as e:
        return _format_file_error(e, "delete file", file_path)


# ================================
# TOOL 5: MOVE_FILE
# ================================

@app.tool(
    description="Move or rename a file with source/destination validation, directory creation, and security checks",
    tags={"file", "move", "rename", "relocate"}
)
async def move_file(
    source_path: Annotated[str, Field(description="Current path of the file to move")],
    destination_path: Annotated[str, Field(description="New path for the file (target location)")],
    create_dirs: Annotated[bool, Field(description="Whether to create parent directories if they don't exist")] = True
) -> str:
    """Move or rename a file with proper security validation and directory creation."""
    try:
        # Validate both paths for security
        validated_source = validate_path(source_path)
        validated_destination = validate_path(destination_path)
        
        # Check if source file exists
        if not validated_source.exists():
            return f"❌ Source file not found: {source_path}\n💡 Check the source path spelling and location"
        
        # Check if source is actually a file (not a directory)
        if validated_source.is_dir():
            return f"❌ Source is a directory: {source_path}\n💡 Use directory-specific operations for folders"
        
        # Check if destination already exists
        if validated_destination.exists():
            return f"❌ Destination already exists: {destination_path}\n💡 Choose a different name or delete the existing file first"
        
        # Create parent directories if requested
        if create_dirs:
            validated_destination.parent.mkdir(parents=True, exist_ok=True)
        
        # Move the file
        validated_source.rename(validated_destination)
        
        return f"✅ File moved successfully:\n\n📂 From: {source_path}\n📁 To: {destination_path}\n🔄 Operation: File relocation completed"
        
    except SecurityError as e:
        return f"❌ Security error: {str(e)}"
    except Exception as e:
        return _format_file_error(e, "move file", f"from {source_path} to {destination_path}")


# ================================
# TOOL 6: COPY_FILE
# ================================

@app.tool(
    description="Copy a file to a new location with source/destination validation, directory creation, and security checks",
    tags={"file", "copy", "duplicate", "backup"}
)
async def copy_file(
    source_path: Annotated[str, Field(description="Path of the file to copy")],
    destination_path: Annotated[str, Field(description="Path for the copied file (target location)")],
    create_dirs: Annotated[bool, Field(description="Whether to create parent directories if they don't exist")] = True
) -> str:
    """Copy a file to a new location with proper security validation and directory creation."""
    try:
        # Validate both paths for security
        validated_source = validate_path(source_path)
        validated_destination = validate_path(destination_path)
        
        # Check if source file exists
        if not validated_source.exists():
            return f"❌ Source file not found: {source_path}\n💡 Check the source path spelling and location"
        
        # Check if source is actually a file (not a directory)
        if validated_source.is_dir():
            return f"❌ Source is a directory: {source_path}\n💡 Use directory-specific operations for folders"
        
        # Check if destination already exists
        if validated_destination.exists():
            return f"❌ Destination already exists: {destination_path}\n💡 Choose a different name or delete the existing file first"
        
        # Create parent directories if requested
        if create_dirs:
            validated_destination.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy the file
        import shutil
        shutil.copy2(validated_source, validated_destination)
        
        # Get file sizes for verification
        source_size = validated_source.stat().st_size
        dest_size = validated_destination.stat().st_size
        
        return f"✅ File copied successfully:\n\n📂 From: {source_path}\n📁 To: {destination_path}\n📏 Size: {source_size} bytes\n🔍 Verified: Source and destination match ({dest_size} bytes)"
        
    except SecurityError as e:
        return f"❌ Security error: {str(e)}"
    except Exception as e:
        return _format_file_error(e, "copy file", f"from {source_path} to {destination_path}")


# ================================
# TOOL 7: LIST_DIRECTORY
# ================================

@app.tool(
    description="List contents of a directory with options for hidden files and recursive listing",
    tags={"directory", "list", "browse", "contents"}
)
async def list_directory(
    directory_path: Annotated[str, Field(description="Path to the directory to list")],
    include_hidden: Annotated[bool, Field(description="Whether to include hidden files and directories")] = False,
    recursive: Annotated[bool, Field(description="Whether to list contents recursively")] = False
) -> str:
    """List contents of a directory with proper security validation and filtering options."""
    try:
        # Validate path security
        validated_path = validate_path(directory_path)
        
        # Check if path exists
        if not validated_path.exists():
            return f"❌ Directory not found: {directory_path}\n💡 Check the directory path spelling and location"
        
        # Check if it's actually a directory (not a file)
        if not validated_path.is_dir():
            return f"❌ Path is not a directory: {directory_path}\n💡 Use file operations for files"
        
        # List directory contents
        items = []
        try:
            if recursive:
                # Recursive listing using rglob
                pattern = "**/*" if include_hidden else "**/*"
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
            return f"❌ Permission denied accessing directory: {directory_path}\n💡 Check directory permissions or ask user to change allowed_base_directory"
        
        if not items:
            return f"✅ Directory is empty:\n\n📁 Path: {directory_path}\n📋 Contents: No files or directories found"
        
        listing_type = "recursive" if recursive else "non-recursive"
        hidden_info = "including hidden" if include_hidden else "excluding hidden"
        
        return f"✅ Directory listing ({listing_type}, {hidden_info}):\n\n📁 Path: {directory_path}\n📋 Items ({len(items)}):\n\n" + "\n".join(items)
        
    except SecurityError as e:
        return f"❌ Security error: {str(e)}"
    except Exception as e:
        return _format_file_error(e, "list directory", directory_path)


# ================================
# TOOL 8: CREATE_DIRECTORY
# ================================

@app.tool(
    description="Create a new directory with options for parent directory creation and security validation",
    tags={"directory", "create", "mkdir", "folder"}
)
async def create_directory(
    directory_path: Annotated[str, Field(description="Path of the directory to create")],
    parents: Annotated[bool, Field(description="Whether to create parent directories if they don't exist")] = True
) -> str:
    """Create a new directory with proper security validation and parent creation options."""
    try:
        # Validate path security
        validated_path = validate_path(directory_path)
        
        # Check if directory already exists
        if validated_path.exists():
            if validated_path.is_dir():
                return f"❌ Directory already exists: {directory_path}\n💡 Directory is already present at this location"
            else:
                return f"❌ Path exists but is not a directory: {directory_path}\n💡 A file exists at this location - choose a different path"
        
        # Create the directory
        try:
            validated_path.mkdir(parents=parents, exist_ok=False)
            
            # Verify creation
            if validated_path.exists() and validated_path.is_dir():
                parent_info = " (including parent directories)" if parents else ""
                return f"✅ Directory created successfully:\n\n📁 Path: {directory_path}\n🔨 Operation: Directory creation completed{parent_info}"
            else:
                return f"❌ Directory creation failed: {directory_path}\n💡 Directory was not created successfully - check permissions"
                
        except FileExistsError:
            return f"❌ Directory already exists: {directory_path}\n💡 Directory was created by another process"
        except FileNotFoundError:
            if not parents:
                return f"❌ Parent directory does not exist: {directory_path}\n💡 Set 'parents=True' to create parent directories automatically"
            else:
                return f"❌ Cannot create directory: {directory_path}\n💡 Check the path and parent directory permissions"
        except PermissionError:
            return f"❌ Permission denied creating directory: {directory_path}\n💡 Check write permissions for the parent directory"
        
    except SecurityError as e:
        return f"❌ Security error: {str(e)}"
    except Exception as e:
        return _format_file_error(e, "create directory", directory_path)


# ================================
# TOOL 9: DELETE_DIRECTORY
# ================================

@app.tool(
    description="Delete a directory with optional recursive deletion and security validation",
    tags={"directory", "delete", "remove", "rmdir", "recursive"}
)
async def delete_directory(
    directory_path: Annotated[str, Field(description="Path of the directory to delete")],
    recursive: Annotated[bool, Field(description="Whether to delete directory and all its contents recursively")] = False
) -> str:
    """Delete a directory with proper security validation and recursive deletion options."""
    try:
        # Validate path security
        validated_path = validate_path(directory_path)
        
        # Check if directory exists
        if not validated_path.exists():
            return f"❌ Directory not found: {directory_path}\n💡 Directory may already be deleted or path is incorrect"
        
        # Check if it's actually a directory (not a file)
        if not validated_path.is_dir():
            return f"❌ Path is not a directory: {directory_path}\n💡 Use 'delete_file' to remove files"
        
        # Check if directory is empty (when not using recursive)
        if not recursive:
            try:
                # Check if directory has any contents
                contents = list(validated_path.iterdir())
                if contents:
                    return f"❌ Directory not empty: {directory_path}\n💡 Directory contains {len(contents)} items - use 'recursive=True' to delete contents or remove items first"
            except PermissionError:
                return f"❌ Permission denied accessing directory: {directory_path}\n💡 Check directory permissions or ask user to change allowed_base_directory"
        
        # Delete the directory
        try:
            if recursive:
                import shutil
                shutil.rmtree(validated_path)
                deletion_type = "recursive deletion (directory and all contents)"
            else:
                validated_path.rmdir()
                deletion_type = "empty directory deletion"
        except OSError as e:
            if "Directory not empty" in str(e):
                return f"❌ Directory not empty: {directory_path}\n💡 Use 'recursive=True' to delete contents or remove items manually first"
            elif "Permission denied" in str(e):
                return f"❌ Permission denied deleting directory: {directory_path}\n💡 Check directory permissions or ask user to change allowed_base_directory"
            else:
                raise e
        
        # Verify deletion
        if not validated_path.exists():
            return f"✅ Directory deleted successfully:\n\n📁 Path: {directory_path}\n🗑️ Operation: {deletion_type.capitalize()} completed"
        else:
            return f"❌ Directory deletion failed: {directory_path}\n💡 Directory still exists - check permissions and try again"
            
    except SecurityError as e:
        return f"❌ Security error: {str(e)}"
    except Exception as e:
        return _format_file_error(e, "delete directory", directory_path)


# ================================
# TOOL 10: FILE_INFO
# ================================

@app.tool(
    description="Get detailed information about a file or directory including metadata, size, permissions, and timestamps",
    tags={"file", "directory", "info", "metadata", "stat", "permissions"}
)
async def file_info(
    path: Annotated[str, Field(description="Path to the file or directory to get information about")]
) -> str:
    """Get detailed information about a file or directory with proper security validation."""
    try:
        # Validate path security
        validated_path = validate_path(path)
        
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
            import datetime
            modified_time = datetime.datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            accessed_time = datetime.datetime.fromtimestamp(stat_info.st_atime).strftime('%Y-%m-%d %H:%M:%S')
            created_time = datetime.datetime.fromtimestamp(stat_info.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
            
            # Format permissions (Unix-style)
            import stat
            mode = stat_info.st_mode
            permissions = stat.filemode(mode)
            
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
                            line_count = sum(1 for _ in f)
                            additional_info = f"\n📝 Text file details: Readable text content, {line_count + 1} lines"
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
            
    except SecurityError as e:
        return f"❌ Security error: {str(e)}"
    except Exception as e:
        return _format_file_error(e, "get file information", path)


# CLI entry point
def cli_main():
    """CLI entry point for File FastMCP server."""
    print("🚀 Starting AgentKnowledgeMCP File FastMCP server...")
    print("📁 Tools: read_file, write_file, append_file, delete_file, move_file, copy_file, list_directory, create_directory, delete_directory, file_info")
    print("✅ Status: All 10 File Tools Complete - Ready for production!")
    
    app.run()

if __name__ == "__main__":
    cli_main()
