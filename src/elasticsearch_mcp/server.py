import asyncio
import json
from elasticsearch import Elasticsearch

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from pydantic import AnyUrl
import mcp.server.stdio

# Elasticsearch client instance
es_client = None

server = Server("elasticsearch-mcp")

def get_es_client():
    """Get or create Elasticsearch client connection."""
    global es_client
    if es_client is None:
        es_client = Elasticsearch([{'host': 'localhost', 'port': 9200}])
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
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle Elasticsearch tool execution requests.
    """
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
                server_name="elasticsearch-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )