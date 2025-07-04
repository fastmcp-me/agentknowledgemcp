import asyncio
import json
import os
import shutil
from pathlib import Path
from elasticsearch import Elasticsearch

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from pydantic import AnyUrl
import mcp.server.stdio

# Load configuration
def load_config():
    """Load configuration from config.json file."""
    config_path = Path(__file__).parent / "config.json"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Default configuration if file doesn't exist
        return {
            "elasticsearch": {"host": "localhost", "port": 9200},
            "security": {"allowed_base_directory": "/Users/nguyenkimchung/ElasticSearch"},
            "server": {"name": "elasticsearch-mcp", "version": "0.1.0"}
        }

# Load configuration
CONFIG = load_config()

# Elasticsearch client instance
es_client = None

# Security: Define allowed base directory for file operations from config
ALLOWED_BASE_DIR = Path(CONFIG["security"]["allowed_base_directory"]).resolve()

def is_path_allowed(file_path: str) -> bool:
    """Check if the given path is within the allowed base directory."""
    try:
        resolved_path = Path(file_path).resolve()
        return resolved_path.is_relative_to(ALLOWED_BASE_DIR)
    except Exception:
        return False

def get_safe_path(file_path: str) -> Path:
    """Get a safe path within the allowed directory."""
    if not is_path_allowed(file_path):
        raise ValueError(f"Access denied: Path '{file_path}' is outside allowed directory '{ALLOWED_BASE_DIR}'")
    return Path(file_path).resolve()

server = Server(CONFIG["server"]["name"])

def get_es_client():
    """Get or create Elasticsearch client connection."""
    global es_client
    if es_client is None:
        es_host = CONFIG["elasticsearch"]["host"]
        es_port = CONFIG["elasticsearch"]["port"]
        es_client = Elasticsearch([{'host': es_host, 'port': es_port}])
    return es_client

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
    List available Elasticsearch tools.
    """
    return [
        types.Tool(
            name="search",
            description="Search documents in Elasticsearch index",
            inputSchema={
                "type": "object",
                "properties": {
                    "index": {"type": "string", "description": "Index name to search in"},
                    "query": {"type": "string", "description": "Search query text"},
                    "size": {"type": "integer", "description": "Number of results to return", "default": 10},
                    "fields": {"type": "array", "items": {"type": "string"}, "description": "Specific fields to return"}
                },
                "required": ["index", "query"],
            },
        ),
        types.Tool(
            name="index_document",
            description="Index a document into Elasticsearch",
            inputSchema={
                "type": "object",
                "properties": {
                    "index": {"type": "string", "description": "Index name"},
                    "document": {"type": "object", "description": "Document to index"},
                    "doc_id": {"type": "string", "description": "Document ID (optional)"}
                },
                "required": ["index", "document"],
            },
        ),
        types.Tool(
            name="create_index",
            description="Create a new Elasticsearch index with mapping",
            inputSchema={
                "type": "object",
                "properties": {
                    "index": {"type": "string", "description": "Index name"},
                    "mapping": {"type": "object", "description": "Index mapping configuration"},
                    "settings": {"type": "object", "description": "Index settings (optional)"}
                },
                "required": ["index", "mapping"],
            },
        ),
        types.Tool(
            name="get_document",
            description="Get a specific document by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "index": {"type": "string", "description": "Index name"},
                    "doc_id": {"type": "string", "description": "Document ID"}
                },
                "required": ["index", "doc_id"],
            },
        ),
        types.Tool(
            name="delete_document",
            description="Delete a document by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "index": {"type": "string", "description": "Index name"},
                    "doc_id": {"type": "string", "description": "Document ID"}
                },
                "required": ["index", "doc_id"],
            },
        ),
        types.Tool(
            name="list_indices",
            description="List all Elasticsearch indices",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="delete_index",
            description="Delete an Elasticsearch index",
            inputSchema={
                "type": "object",
                "properties": {
                    "index": {"type": "string", "description": "Index name to delete"}
                },
                "required": ["index"],
            },
        ),
        # File system tools
        types.Tool(
            name="read_file",
            description="Read content from a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to the file to read"},
                    "encoding": {"type": "string", "description": "File encoding (default: utf-8)", "default": "utf-8"}
                },
                "required": ["file_path"],
            },
        ),
        types.Tool(
            name="write_file",
            description="Write content to a file (creates new or overwrites existing)",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to the file to write"},
                    "content": {"type": "string", "description": "Content to write to the file"},
                    "encoding": {"type": "string", "description": "File encoding (default: utf-8)", "default": "utf-8"},
                    "create_dirs": {"type": "boolean", "description": "Create parent directories if they don't exist", "default": True}
                },
                "required": ["file_path", "content"],
            },
        ),
        types.Tool(
            name="append_file",
            description="Append content to an existing file",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to the file to append to"},
                    "content": {"type": "string", "description": "Content to append to the file"},
                    "encoding": {"type": "string", "description": "File encoding (default: utf-8)", "default": "utf-8"}
                },
                "required": ["file_path", "content"],
            },
        ),
        types.Tool(
            name="delete_file",
            description="Delete a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to the file to delete"}
                },
                "required": ["file_path"],
            },
        ),
        types.Tool(
            name="move_file",
            description="Move or rename a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "source_path": {"type": "string", "description": "Current path of the file"},
                    "destination_path": {"type": "string", "description": "New path for the file"},
                    "create_dirs": {"type": "boolean", "description": "Create parent directories if they don't exist", "default": True}
                },
                "required": ["source_path", "destination_path"],
            },
        ),
        types.Tool(
            name="copy_file",
            description="Copy a file to a new location",
            inputSchema={
                "type": "object",
                "properties": {
                    "source_path": {"type": "string", "description": "Path of the file to copy"},
                    "destination_path": {"type": "string", "description": "Path for the copied file"},
                    "create_dirs": {"type": "boolean", "description": "Create parent directories if they don't exist", "default": True}
                },
                "required": ["source_path", "destination_path"],
            },
        ),
        types.Tool(
            name="list_directory",
            description="List contents of a directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory_path": {"type": "string", "description": "Path to the directory to list"},
                    "include_hidden": {"type": "boolean", "description": "Include hidden files/directories", "default": False},
                    "recursive": {"type": "boolean", "description": "List contents recursively", "default": False}
                },
                "required": ["directory_path"],
            },
        ),
        types.Tool(
            name="create_directory",
            description="Create a new directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory_path": {"type": "string", "description": "Path of the directory to create"},
                    "parents": {"type": "boolean", "description": "Create parent directories if they don't exist", "default": True}
                },
                "required": ["directory_path"],
            },
        ),
        types.Tool(
            name="delete_directory",
            description="Delete a directory (and optionally its contents)",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory_path": {"type": "string", "description": "Path of the directory to delete"},
                    "recursive": {"type": "boolean", "description": "Delete directory and all its contents", "default": False}
                },
                "required": ["directory_path"],
            },
        ),
        types.Tool(
            name="file_info",
            description="Get information about a file or directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the file or directory"}
                },
                "required": ["path"],
            },
        ),
        types.Tool(
            name="get_allowed_directory",
            description="Get the current allowed base directory for file operations",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="set_allowed_directory",
            description="Set the allowed base directory for file operations (admin function)",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory_path": {"type": "string", "description": "New base directory path to allow"}
                },
                "required": ["directory_path"],
            },
        ),
        types.Tool(
            name="reload_config",
            description="Reload configuration from config.json file",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle Elasticsearch tool execution requests.
    """
    global CONFIG, ALLOWED_BASE_DIR, es_client
    
    if not arguments:
        arguments = {}

    try:
        es = get_es_client()
        
        if name == "search":
            index = arguments.get("index")
            query_text = arguments.get("query")
            size = arguments.get("size", 10)
            fields = arguments.get("fields", [])
            
            # Build search query
            search_body = {
                "query": {
                    "multi_match": {
                        "query": query_text,
                        "fields": ["title^3", "summary^2", "content", "tags^2", "features^2", "tech_stack^2"]
                    }
                },
                "size": size
            }
            
            if fields:
                search_body["_source"] = fields
            
            result = es.search(index=index, body=search_body)
            
            # Format results
            formatted_results = []
            for hit in result['hits']['hits']:
                source = hit['_source']
                score = hit['_score']
                formatted_results.append({
                    "id": hit['_id'],
                    "score": score,
                    "source": source
                })
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Search results for '{query_text}' in index '{index}':\n\n" +
                         json.dumps({
                             "total": result['hits']['total']['value'],
                             "results": formatted_results
                         }, indent=2, ensure_ascii=False)
                )
            ]
            
        elif name == "index_document":
            index = arguments.get("index")
            document = arguments.get("document")
            doc_id = arguments.get("doc_id")
            
            if doc_id:
                result = es.index(index=index, id=doc_id, body=document)
            else:
                result = es.index(index=index, body=document)
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Document indexed successfully:\n{json.dumps(result, indent=2)}"
                )
            ]
            
        elif name == "create_index":
            index = arguments.get("index")
            mapping = arguments.get("mapping")
            settings = arguments.get("settings", {})
            
            body = {"mappings": mapping}
            if settings:
                body["settings"] = settings
            
            result = es.indices.create(index=index, body=body)
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Index '{index}' created successfully:\n{json.dumps(result, indent=2)}"
                )
            ]
            
        elif name == "get_document":
            index = arguments.get("index")
            doc_id = arguments.get("doc_id")
            
            result = es.get(index=index, id=doc_id)
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Document retrieved:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
                )
            ]
            
        elif name == "delete_document":
            index = arguments.get("index")
            doc_id = arguments.get("doc_id")
            
            result = es.delete(index=index, id=doc_id)
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Document deleted:\n{json.dumps(result, indent=2)}"
                )
            ]
            
        elif name == "list_indices":
            indices = es.indices.get_alias(index="*")
            
            # Get stats for each index
            indices_info = []
            for index_name in indices.keys():
                if not index_name.startswith('.'):  # Skip system indices
                    try:
                        stats = es.indices.stats(index=index_name)
                        doc_count = stats['indices'][index_name]['total']['docs']['count']
                        size = stats['indices'][index_name]['total']['store']['size_in_bytes']
                        indices_info.append({
                            "name": index_name,
                            "docs": doc_count,
                            "size_bytes": size
                        })
                    except:
                        indices_info.append({
                            "name": index_name,
                            "docs": "unknown",
                            "size_bytes": "unknown"
                        })
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Available indices:\n{json.dumps(indices_info, indent=2)}"
                )
            ]
            
        elif name == "delete_index":
            index = arguments.get("index")
            
            result = es.indices.delete(index=index)
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Index '{index}' deleted successfully:\n{json.dumps(result, indent=2)}"
                )
            ]
        
        # File system operations
        elif name == "read_file":
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
                        text=f"Error reading file '{file_path}': {str(e)}"
                    )
                ]
        
        elif name == "write_file":
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
                        text=f"Error writing file '{file_path}': {str(e)}"
                    )
                ]
        
        elif name == "append_file":
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
                        text=f"Error appending to file '{file_path}': {str(e)}"
                    )
                ]
        
        elif name == "delete_file":
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
                        text=f"Error deleting file '{file_path}': {str(e)}"
                    )
                ]
        
        elif name == "move_file":
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
                        text=f"Error moving file from '{source_path}' to '{destination_path}': {str(e)}"
                    )
                ]
        
        elif name == "copy_file":
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
                        text=f"Error copying file from '{source_path}' to '{destination_path}': {str(e)}"
                    )
                ]
        
        elif name == "list_directory":
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
                        text=f"Contents of '{directory_path}' (limited to {ALLOWED_BASE_DIR}):\n\n{json.dumps(items, indent=2)}"
                    )
                ]
            except Exception as e:
                return [
                    types.TextContent(
                        type="text",
                        text=f"Error listing directory '{directory_path}': {str(e)}"
                    )
                ]
        
        elif name == "create_directory":
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
                        text=f"Error creating directory '{directory_path}': {str(e)}"
                    )
                ]
        
        elif name == "delete_directory":
            directory_path = arguments.get("directory_path")
            recursive = arguments.get("recursive", False)
            
            try:
                path_obj = get_safe_path(directory_path)
                
                if not path_obj.exists():
                    raise FileNotFoundError(f"Directory not found: {directory_path}")
                
                if not path_obj.is_dir():
                    raise NotADirectoryError(f"'{directory_path}' is not a directory")
                
                # Extra safety: don't allow deleting the base directory itself
                if path_obj.resolve() == ALLOWED_BASE_DIR:
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
                        text=f"Error deleting directory '{directory_path}': {str(e)}"
                    )
                ]
        
        elif name == "file_info":
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
                    "allowed_base_dir": str(ALLOWED_BASE_DIR)
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
                        text=f"Error getting info for '{path}': {str(e)}"
                    )
                ]
        
        elif name == "get_allowed_directory":
            return [
                types.TextContent(
                    type="text",
                    text=f"Current allowed base directory: {ALLOWED_BASE_DIR}"
                )
            ]
        
        elif name == "set_allowed_directory":
            directory_path = arguments.get("directory_path")
            
            try:
                new_path = Path(directory_path).resolve()
                
                if not new_path.exists():
                    raise FileNotFoundError(f"Directory not found: {directory_path}")
                
                if not new_path.is_dir():
                    raise NotADirectoryError(f"Path is not a directory: {directory_path}")
                
                old_path = ALLOWED_BASE_DIR
                ALLOWED_BASE_DIR = new_path
                
                return [
                    types.TextContent(
                        type="text",
                        text=f"Allowed base directory changed from '{old_path}' to '{ALLOWED_BASE_DIR}'"
                    )
                ]
            except Exception as e:
                return [
                    types.TextContent(
                        type="text",
                        text=f"Error setting allowed directory to '{directory_path}': {str(e)}"
                    )
                ]
        
        elif name == "reload_config":
            try:
                # Reload configuration
                CONFIG = load_config()
                ALLOWED_BASE_DIR = Path(CONFIG["security"]["allowed_base_directory"]).resolve()
                
                # Reset Elasticsearch client to use new config
                es_client = None
                
                return [
                    types.TextContent(
                        type="text",
                        text=f"Configuration reloaded successfully.\nNew allowed directory: {ALLOWED_BASE_DIR}\nElasticsearch: {CONFIG['elasticsearch']['host']}:{CONFIG['elasticsearch']['port']}"
                    )
                ]
            except Exception as e:
                return [
                    types.TextContent(
                        type="text",
                        text=f"Error reloading configuration: {str(e)}"
                    )
                ]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
            
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"Error executing {name}: {str(e)}"
            )
        ]

async def main():
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