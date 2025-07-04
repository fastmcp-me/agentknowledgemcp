"""
Elasticsearch tool handlers.
"""
import json
from typing import List, Dict, Any, Optional

import mcp.types as types
from .elasticsearch_client import get_es_client


async def handle_search(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle search tool."""
    es = get_es_client()
    
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


async def handle_index_document(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle index_document tool."""
    es = get_es_client()
    
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


async def handle_create_index(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle create_index tool."""
    es = get_es_client()
    
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


async def handle_get_document(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle get_document tool."""
    es = get_es_client()
    
    index = arguments.get("index")
    doc_id = arguments.get("doc_id")
    
    result = es.get(index=index, id=doc_id)
    
    return [
        types.TextContent(
            type="text",
            text=f"Document retrieved:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
        )
    ]


async def handle_delete_document(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle delete_document tool."""
    es = get_es_client()
    
    index = arguments.get("index")
    doc_id = arguments.get("doc_id")
    
    result = es.delete(index=index, id=doc_id)
    
    return [
        types.TextContent(
            type="text",
            text=f"Document deleted:\n{json.dumps(result, indent=2)}"
        )
    ]


async def handle_list_indices(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle list_indices tool."""
    es = get_es_client()
    
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


async def handle_delete_index(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle delete_index tool."""
    es = get_es_client()
    
    index = arguments.get("index")
    
    result = es.indices.delete(index=index)
    
    return [
        types.TextContent(
            type="text",
            text=f"Index '{index}' deleted successfully:\n{json.dumps(result, indent=2)}"
        )
    ]
