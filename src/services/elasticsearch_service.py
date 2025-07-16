"""
Elasticsearch Service for FastMCP server composition.
Contains all Elasticsearch-related tools with enhanced parameter descriptions.
"""
from typing import Dict, Any, List, Optional, Annotated

from fastmcp import FastMCP
from fastmcp.server import Context
from pydantic import Field

# Import existing handlers
from ..elasticsearch_handlers import (
    handle_search, handle_index_document, handle_create_index,
    handle_get_document, handle_delete_document, handle_list_indices,
    handle_delete_index
)

# Create Elasticsearch service
elasticsearch_service = FastMCP(
    name="ElasticsearchService",
    instructions="Elasticsearch operations service for document storage, search, and index management"
)

@elasticsearch_service.tool(
    description="🔍 Search documents in Elasticsearch index with advanced filtering, pagination, and time-based sorting capabilities",
    tags={"elasticsearch", "search", "query", "filter"}
)
async def search(
    index: Annotated[str, Field(description="Name of the Elasticsearch index to search")],
    query: Annotated[str, Field(description="Search query text to find matching documents")],
    size: Annotated[int, Field(description="Maximum number of results to return", ge=1, le=1000)] = 10,
    fields: Annotated[Optional[List[str]], Field(description="Specific fields to include in search results")] = None,
    date_from: Annotated[Optional[str], Field(description="Start date filter in ISO format (YYYY-MM-DD)")] = None,
    date_to: Annotated[Optional[str], Field(description="End date filter in ISO format (YYYY-MM-DD)")] = None,
    time_period: Annotated[Optional[str], Field(description="Predefined time period filter (e.g., '7d', '1m', '1y')")] = None,
    sort_by_time: Annotated[str, Field(description="Sort order by timestamp", regex="^(asc|desc)$")] = "desc"
) -> str:
    """Search documents in Elasticsearch index with optional time-based filtering."""
    arguments = {
        "index": index,
        "query": query,
        "size": size,
        "fields": fields,
        "date_from": date_from,
        "date_to": date_to,
        "time_period": time_period,
        "sort_by_time": sort_by_time
    }
    result = await handle_search(arguments)
    return result[0].text if result and hasattr(result[0], 'text') else str(result)

@elasticsearch_service.tool(
    description="📝 Index/store a document in Elasticsearch with automatic schema validation and content processing",
    tags={"elasticsearch", "indexing", "document", "storage"}
)
async def index_document(
    index: Annotated[str, Field(description="Name of the Elasticsearch index to store the document")],
    document: Annotated[Dict[str, Any], Field(description="Document content as JSON object/dictionary")],
    doc_id: Annotated[Optional[str], Field(description="Custom document ID (auto-generated if not provided)")] = None,
    validate_schema: Annotated[bool, Field(description="Whether to validate document against index schema")] = True
) -> str:
    """Index a document into Elasticsearch with optional schema validation."""
    arguments = {
        "index": index,
        "document": document,
        "doc_id": doc_id,
        "validate_schema": validate_schema
    }
    
    handler_result = await handle_index_document(arguments)
    return handler_result[0].text if handler_result and hasattr(handler_result[0], 'text') else str(handler_result)

@elasticsearch_service.tool(
    description="🚨 DESTRUCTIVE: Delete a document from Elasticsearch index with user confirmation via interactive elicitation",
    tags={"elasticsearch", "delete", "destructive", "elicitation"}
)
async def delete_document(
    ctx: Context,
    index: Annotated[str, Field(description="Name of the Elasticsearch index containing the document")],
    doc_id: Annotated[str, Field(description="Unique ID of the document to delete")]
) -> str:
    """Delete a document from Elasticsearch index with user confirmation."""
    
    # Step 1: Ask for user confirmation using FastMCP elicitation
    result = await ctx.elicit(
        message=f"🚨 DESTRUCTIVE OPERATION\n"
               f"Are you sure you want to delete document '{doc_id}' from index '{index}'?\n"
               f"This action cannot be undone.\n\n"
               f"Type 'yes' to confirm deletion or 'no' to cancel:",
        response_type=str
    )
    
    # Step 2: Check user response
    if result.action == "decline":
        return f"❌ Deletion declined by user. Document '{doc_id}' was NOT deleted."
    elif result.action == "cancel":
        return f"❌ Deletion cancelled by user. Document '{doc_id}' was NOT deleted."
    elif result.action == "accept":
        # Check if user confirmed with 'yes'
        user_response = result.data.lower().strip()
        if user_response not in ['yes', 'y']:
            return f"❌ Deletion not confirmed (user said '{result.data}'). Document '{doc_id}' was NOT deleted."
        
        # Step 3: User confirmed, proceed with deletion
        arguments = {
            "index": index,
            "doc_id": doc_id
        }
        
        handler_result = await handle_delete_document(arguments)
        
        # Step 4: Add confirmation note to result
        if handler_result and hasattr(handler_result[0], 'text'):
            result_text = handler_result[0].text
            return f"✅ User confirmed deletion with '{result.data}'.\n{result_text}"
        else:
            return f"✅ User confirmed deletion with '{result.data}'.\n{str(handler_result)}"
    
    return f"❌ Unexpected elicitation result: {result.action}"

@elasticsearch_service.tool(
    description="📋 Get a specific document by its unique ID from Elasticsearch index",
    tags={"elasticsearch", "retrieve", "document"}
)
async def get_document(
    index: Annotated[str, Field(description="Name of the Elasticsearch index containing the document")],
    doc_id: Annotated[str, Field(description="Unique ID of the document to retrieve")]
) -> str:
    """Get a specific document by ID."""
    arguments = {
        "index": index,
        "doc_id": doc_id
    }
    result = await handle_get_document(arguments)
    return result[0].text if result and hasattr(result[0], 'text') else str(result)

@elasticsearch_service.tool(
    description="🏗️ Create a new Elasticsearch index with custom mapping and settings",
    tags={"elasticsearch", "index", "creation", "mapping"}
)
async def create_index(
    index: Annotated[str, Field(description="Name of the new Elasticsearch index to create")],
    mapping: Annotated[Dict[str, Any], Field(description="Index mapping definition (field types and properties)")],
    settings: Annotated[Optional[Dict[str, Any]], Field(description="Index settings (shards, replicas, analyzers, etc.)")] = None
) -> str:
    """Create a new Elasticsearch index with mapping."""
    arguments = {
        "index": index,
        "mapping": mapping,
        "settings": settings
    }
    
    handler_result = await handle_create_index(arguments)
    return handler_result[0].text if handler_result and hasattr(handler_result[0], 'text') else str(handler_result)

@elasticsearch_service.tool(
    description="📑 List all available Elasticsearch indices with their metadata",
    tags={"elasticsearch", "indices", "list", "metadata"}
)
async def list_indices() -> str:
    """List all Elasticsearch indices."""
    result = await handle_list_indices({})
    return result[0].text if result and hasattr(result[0], 'text') else str(result)

@elasticsearch_service.tool(
    description="🗑️ Delete an entire Elasticsearch index and all its documents (DESTRUCTIVE)",
    tags={"elasticsearch", "index", "delete", "destructive"}
)
async def delete_index(
    index: Annotated[str, Field(description="Name of the Elasticsearch index to delete")]
) -> str:
    """Delete an Elasticsearch index."""
    arguments = {
        "index": index
    }
    
    handler_result = await handle_delete_index(arguments)
    return handler_result[0].text if handler_result and hasattr(handler_result[0], 'text') else str(handler_result)
