"""
Elasticsearch tool handlers.
"""
import json
from typing import List, Dict, Any, Optional

import mcp.types as types
from .elasticsearch_client import get_es_client
from .document_schema import (
    validate_document_structure, 
    DocumentValidationError, 
    create_document_template,
    format_validation_error
)
from .config import load_config


async def handle_search(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle search tool."""
    try:
        es = get_es_client()
        
        index = arguments.get("index")
        query_text = arguments.get("query")
        size = arguments.get("size", 10)
        fields = arguments.get("fields", [])
        
        # Build search query with date sorting consideration
        search_body = {
            "query": {
                "multi_match": {
                    "query": query_text,
                    "fields": ["title^3", "summary^2", "content", "tags^2", "features^2", "tech_stack^2"]
                }
            },
            "sort": [
                "_score",  # Primary sort by relevance
                {"last_modified": {"order": "desc"}}  # Secondary sort by recency
            ],
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
        
        total_results = result['hits']['total']['value']
        
        # Check if no results found and provide helpful suggestions
        if total_results == 0:
            return [
                types.TextContent(
                    type="text",
                    text=f"🔍 No results found for '{query_text}' in index '{index}'\n\n" +
                         f"💡 **Search Optimization Suggestions for Agents**:\n\n" +
                         f"🎯 **Try Different Keywords**:\n" +
                         f"   • Use synonyms and related terms\n" +
                         f"   • Try shorter, more general keywords\n" +
                         f"   • Break complex queries into simpler parts\n" +
                         f"   • Use different language variations if applicable\n\n" +
                         f"📅 **Consider Recency**:\n" +
                         f"   • Recent documents may use different terminology\n" +
                         f"   • Try searching with current date/time related terms\n" +
                         f"   • Look for latest trends or recent updates\n\n" +
                         f"🤝 **Ask User for Help**:\n" +
                         f"   • Request user to suggest related keywords\n" +
                         f"   • Ask about specific topics or domains they're interested in\n" +
                         f"   • Get context about what they're trying to find\n" +
                         f"   • Ask for alternative ways to describe their query\n\n" +
                         f"🔧 **Technical Tips**:\n" +
                         f"   • Try searching in different indices with 'list_indices'\n" +
                         f"   • Use broader search terms first, then narrow down\n" +
                         f"   • Check for typos in search terms\n" +
                         f"   • Consider partial word matches"
                )
            ]
        
        return [
            types.TextContent(
                type="text",
                text=f"Search results for '{query_text}' in index '{index}' (sorted by relevance and recency):\n\n" +
                     json.dumps({
                         "total": total_results,
                         "results": formatted_results
                     }, indent=2, ensure_ascii=False) +
                     (f"\n\n💡 **Limited Results Found** ({total_results} matches):\n" +
                      f"   • Try broader or alternative keywords for more results\n" +
                      f"   • Ask user for related terms or different perspectives\n" +
                      f"   • Consider searching in other indices with 'list_indices'\n" +
                      f"   • Results are sorted by relevance first, then by recency"
                      if total_results > 0 and total_results <= 3 else "")
            )
        ]
    except Exception as e:
        # Provide detailed error messages for different types of Elasticsearch errors
        error_message = "❌ Search failed:\n\n"
        
        error_str = str(e).lower()
        if "connection" in error_str or "refused" in error_str:
            error_message += "🔌 **Connection Error**: Cannot connect to Elasticsearch server\n"
            error_message += f"📍 Check if Elasticsearch is running at the configured address\n"
            error_message += f"💡 Try: Use 'setup_elasticsearch' tool to start Elasticsearch\n\n"
        elif "index" in error_str and "not found" in error_str:
            error_message += f"📁 **Index Error**: Index '{index}' does not exist\n"
            error_message += f"📍 The search index has not been created yet\n"
            error_message += f"💡 **Suggestions for agents**:\n"
            error_message += f"   1. Use 'list_indices' tool to see all available indices\n"
            error_message += f"   2. Check which indices contain your target data\n"
            error_message += f"   3. Use the correct index name from the list\n"
            error_message += f"   4. If no suitable index exists, create one with 'create_index' tool\n\n"
        elif "timeout" in error_str:
            error_message += "⏱️ **Timeout Error**: Search query timed out\n"
            error_message += f"📍 Query may be too complex or index too large\n"
            error_message += f"💡 Try: Simplify query or reduce search size\n\n"
        elif "parse" in error_str or "query" in error_str:
            error_message += f"🔍 **Query Error**: Invalid search query format\n"
            error_message += f"📍 Search query syntax is not valid\n"
            error_message += f"💡 Try: Use simpler search terms\n\n"
        else:
            error_message += f"⚠️ **Unknown Error**: {str(e)}\n\n"
        
        error_message += f"🔍 **Technical Details**: {str(e)}"
        
        return [
            types.TextContent(
                type="text",
                text=error_message
            )
        ]


async def handle_index_document(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle index_document tool with document validation."""
    es = get_es_client()
    
    index = arguments.get("index")
    document = arguments.get("document")
    doc_id = arguments.get("doc_id")
    validate_schema = arguments.get("validate_schema", True)  # Default to True
    
    # Validate document structure if requested
    if validate_schema:
        try:
            # Get base directory from config
            config = load_config()
            base_directory = config.get("security", {}).get("allowed_base_directory")
            
            # Check if this looks like a knowledge base document
            if isinstance(document, dict) and "id" in document and "title" in document:
                validated_doc = validate_document_structure(document, base_directory)
                document = validated_doc
                
                # Use the document ID from the validated document if not provided
                if not doc_id:
                    doc_id = document.get("id")
                    
                # THIS IS THE FIX: REMOVED THE PREMATURE RETURN
                # The function will now proceed to the indexing block
                
            else:
                # For non-knowledge base documents, still validate with strict mode if enabled
                validated_doc = validate_document_structure(document, base_directory, is_knowledge_doc=False)
                document = validated_doc
        except DocumentValidationError as e:
            return [
                types.TextContent(
                    type="text",
                    text=format_validation_error(e)
                )
            ]
        except Exception as e:
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ Validation error: {str(e)}"
                )
            ]
    
    # Index the document
    try:
        if doc_id:
            result = es.index(index=index, id=doc_id, body=document)
        else:
            result = es.index(index=index, body=document)
        
        return [
            types.TextContent(
                type="text",
                text=f"Document indexed successfully:\n{json.dumps(result, indent=2)}\n\n" +
                     f"💡 **Best Practices for Agents**:\n" +
                     f"   • For SHORT content: Store directly in document 'content' field (recommended)\n" +
                     f"   • For LONG content: Create separate files only when necessary\n" +
                     f"   • Before creating new documents: Check if existing ones can be updated\n" +
                     f"   • Consider deleting outdated documents to keep knowledge base clean\n" +
                     f"   • Use 'search' tool to find and update existing relevant content"
            )
        ]
    except Exception as e:
        # Provide detailed error messages for different types of Elasticsearch errors
        error_message = "❌ Failed to index document:\n\n"
        
        error_str = str(e).lower()
        if "connection" in error_str or "refused" in error_str:
            error_message += "🔌 **Connection Error**: Cannot connect to Elasticsearch server\n"
            error_message += f"📍 Check if Elasticsearch is running at the configured address\n"
            error_message += f"💡 Try: Use 'setup_elasticsearch' tool to start Elasticsearch\n"
            error_message += f"🔧 Or check configuration with 'get_config' tool\n\n"
        elif "timeout" in error_str:
            error_message += "⏱️ **Timeout Error**: Elasticsearch server is not responding\n"
            error_message += f"📍 Server may be overloaded or slow to respond\n"
            error_message += f"💡 Try: Wait and retry, or check server status\n\n"
        elif "index" in error_str and "not found" in error_str:
            error_message += f"📁 **Index Error**: Index '{index}' does not exist\n"
            error_message += f"📍 The target index has not been created yet\n"
            error_message += f"💡 Try: Use 'create_index' tool to create the index first\n\n"
        elif "mapping" in error_str or "field" in error_str:
            error_message += "📝 **Document Structure Error**: Document doesn't match index mapping\n"
            error_message += f"📍 Document fields may be incompatible with existing index structure\n"
            error_message += f"💡 Try: Validate document schema before indexing\n\n"
        elif "permission" in error_str or "forbidden" in error_str:
            error_message += "🔒 **Permission Error**: Access denied to Elasticsearch\n"
            error_message += f"📍 Authentication or authorization failed\n"
            error_message += f"💡 Try: Check Elasticsearch security settings\n\n"
        else:
            error_message += f"⚠️ **Unknown Error**: {str(e)}\n\n"
        
        error_message += f"🔍 **Technical Details**: {str(e)}"
        
        return [
            types.TextContent(
                type="text",
                text=error_message
            )
        ]


async def handle_create_index(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle create_index tool."""
    try:
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
    except Exception as e:
        # Provide detailed error messages for different types of Elasticsearch errors
        error_message = "❌ Failed to create index:\n\n"
        
        error_str = str(e).lower()
        if "connection" in error_str or "refused" in error_str:
            error_message += "🔌 **Connection Error**: Cannot connect to Elasticsearch server\n"
            error_message += f"📍 Check if Elasticsearch is running at the configured address\n"
            error_message += f"💡 Try: Use 'setup_elasticsearch' tool to start Elasticsearch\n\n"
        elif "already exists" in error_str or "resource_already_exists" in error_str:
            error_message += f"📁 **Index Exists**: Index '{index}' already exists\n"
            error_message += f"📍 Cannot create an index that already exists\n"
            error_message += f"💡 Try: Use 'delete_index' first, or choose a different name\n\n"
        elif "mapping" in error_str or "invalid" in error_str:
            error_message += f"📝 **Mapping Error**: Invalid index mapping or settings\n"
            error_message += f"📍 The provided mapping/settings are not valid\n"
            error_message += f"💡 Try: Check mapping syntax and field types\n\n"
        elif "permission" in error_str or "forbidden" in error_str:
            error_message += "🔒 **Permission Error**: Not allowed to create index\n"
            error_message += f"📍 Insufficient permissions for index creation\n"
            error_message += f"💡 Try: Check Elasticsearch security settings\n\n"
        else:
            error_message += f"⚠️ **Unknown Error**: {str(e)}\n\n"
        
        error_message += f"🔍 **Technical Details**: {str(e)}"
        
        return [
            types.TextContent(
                type="text",
                text=error_message
            )
        ]


async def handle_get_document(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle get_document tool."""
    try:
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
    except Exception as e:
        # Provide detailed error messages for different types of Elasticsearch errors
        error_message = "❌ Failed to get document:\n\n"
        
        error_str = str(e).lower()
        if "connection" in error_str or "refused" in error_str:
            error_message += "🔌 **Connection Error**: Cannot connect to Elasticsearch server\n"
            error_message += f"📍 Check if Elasticsearch is running at the configured address\n"
            error_message += f"💡 Try: Use 'setup_elasticsearch' tool to start Elasticsearch\n\n"
        elif "not_found" in error_str or "not found" in error_str:
            if "index" in error_str:
                error_message += f"📁 **Index Not Found**: Index '{index}' does not exist\n"
                error_message += f"📍 The target index has not been created yet\n"
                error_message += f"💡 **Suggestions for agents**:\n"
                error_message += f"   1. Use 'list_indices' tool to see all available indices\n"
                error_message += f"   2. Check which indices contain your target data\n"
                error_message += f"   3. Use the correct index name from the list\n"
                error_message += f"   4. If no suitable index exists, create one with 'create_index' tool\n\n"
            else:
                error_message += f"📄 **Document Not Found**: Document ID '{doc_id}' does not exist\n"
                error_message += f"📍 The requested document was not found in index '{index}'\n"
                error_message += f"💡 Try: Check document ID or use 'search' to find documents\n\n"
        else:
            error_message += f"⚠️ **Unknown Error**: {str(e)}\n\n"
        
        error_message += f"🔍 **Technical Details**: {str(e)}"
        
        return [
            types.TextContent(
                type="text",
                text=error_message
            )
        ]


async def handle_delete_document(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle delete_document tool."""
    try:
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
    except Exception as e:
        # Provide detailed error messages for different types of Elasticsearch errors
        error_message = "❌ Failed to delete document:\n\n"
        
        error_str = str(e).lower()
        if "connection" in error_str or "refused" in error_str:
            error_message += "🔌 **Connection Error**: Cannot connect to Elasticsearch server\n"
            error_message += f"📍 Check if Elasticsearch is running at the configured address\n"
            error_message += f"💡 Try: Use 'setup_elasticsearch' tool to start Elasticsearch\n\n"
        elif "not_found" in error_str or "not found" in error_str:
            error_message += f"📄 **Document Not Found**: Document ID '{doc_id}' does not exist\n"
            error_message += f"📍 Cannot delete a document that doesn't exist\n"
            error_message += f"💡 Try: Check document ID or use 'search' to find documents\n\n"
        elif "index" in error_str and ("not found" in error_str or "not_found" in error_str):
            error_message += f"📁 **Index Not Found**: Index '{index}' does not exist\n"
            error_message += f"📍 The target index has not been created yet\n"
            error_message += f"💡 Try: Use 'list_indices' to see available indices\n\n"
        else:
            error_message += f"⚠️ **Unknown Error**: {str(e)}\n\n"
        
        error_message += f"🔍 **Technical Details**: {str(e)}"
        
        return [
            types.TextContent(
                type="text",
                text=error_message
            )
        ]
    
    return [
        types.TextContent(
            type="text",
            text=f"Document deleted:\n{json.dumps(result, indent=2)}"
        )
    ]


async def handle_list_indices(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle list_indices tool."""
    try:
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
    except Exception as e:
        # Provide detailed error messages for different types of Elasticsearch errors
        error_message = "❌ Failed to list indices:\n\n"
        
        error_str = str(e).lower()
        if "connection" in error_str or "refused" in error_str:
            error_message += "🔌 **Connection Error**: Cannot connect to Elasticsearch server\n"
            error_message += f"📍 Check if Elasticsearch is running at the configured address\n"
            error_message += f"💡 Try: Use 'setup_elasticsearch' tool to start Elasticsearch\n\n"
        elif "timeout" in error_str:
            error_message += "⏱️ **Timeout Error**: Elasticsearch server is not responding\n"
            error_message += f"📍 Server may be overloaded or slow to respond\n"
            error_message += f"💡 Try: Wait and retry, or check server status\n\n"
        else:
            error_message += f"⚠️ **Unknown Error**: {str(e)}\n\n"
        
        error_message += f"🔍 **Technical Details**: {str(e)}"
        
        return [
            types.TextContent(
                type="text",
                text=error_message
            )
        ]


async def handle_delete_index(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle delete_index tool."""
    try:
        es = get_es_client()
        
        index = arguments.get("index")
        
        result = es.indices.delete(index=index)
        
        return [
            types.TextContent(
                type="text",
                text=f"Index '{index}' deleted successfully:\n{json.dumps(result, indent=2)}"
            )
        ]
    except Exception as e:
        # Provide detailed error messages for different types of Elasticsearch errors
        error_message = "❌ Failed to delete index:\n\n"
        
        error_str = str(e).lower()
        if "connection" in error_str or "refused" in error_str:
            error_message += "🔌 **Connection Error**: Cannot connect to Elasticsearch server\n"
            error_message += f"📍 Check if Elasticsearch is running at the configured address\n"
            error_message += f"💡 Try: Use 'setup_elasticsearch' tool to start Elasticsearch\n\n"
        elif "not_found" in error_str or "not found" in error_str:
            error_message += f"📁 **Index Not Found**: Index '{index}' does not exist\n"
            error_message += f"📍 Cannot delete an index that doesn't exist\n"
            error_message += f"💡 Try: Use 'list_indices' to see available indices\n\n"
        elif "permission" in error_str or "forbidden" in error_str:
            error_message += "🔒 **Permission Error**: Not allowed to delete index\n"
            error_message += f"📍 Insufficient permissions for index deletion\n"
            error_message += f"💡 Try: Check Elasticsearch security settings\n\n"
        else:
            error_message += f"⚠️ **Unknown Error**: {str(e)}\n\n"
        
        error_message += f"🔍 **Technical Details**: {str(e)}"
        
        return [
            types.TextContent(
                type="text",
                text=error_message
            )
        ]


async def handle_validate_document_schema(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle validate_document_schema tool."""
    document = arguments.get("document")
    
    try:
        # Get base directory from config
        config = load_config()
        base_directory = config.get("security", {}).get("allowed_base_directory")
        
        validated_doc = validate_document_structure(document, base_directory)
        return [
            types.TextContent(
                type="text",
                text=f"✅ Document validation successful!\n\n"
                     f"Validated document:\n{json.dumps(validated_doc, indent=2, ensure_ascii=False)}\n\n"
                     f"Document is ready to be indexed.\n\n"
                     f"🎯 **Smart Content Strategy for Agents**:\n"
                     f"   • Check content length: If < 1000 chars, store in 'content' field directly\n"
                     f"   • For longer content: Consider if a separate file is truly needed\n"
                     f"   • Before indexing: Search for existing similar documents to update\n"
                     f"   • Avoid creating duplicate content - update existing instead"
            )
        ]
    except DocumentValidationError as e:
        return [
            types.TextContent(
                type="text",
                text=format_validation_error(e)
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"❌ Validation error: {str(e)}"
            )
        ]


async def handle_create_document_template(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle create_document_template tool."""
    try:
        # Get base directory from config
        config = load_config()
        base_directory = config.get("security", {}).get("allowed_base_directory")
        
        title = arguments.get("title")
        file_path = arguments.get("file_path") 
        priority = arguments.get("priority", "medium")
        source_type = arguments.get("source_type", "markdown")
        tags = arguments.get("tags", [])
        summary = arguments.get("summary", "")
        key_points = arguments.get("key_points", [])
        related = arguments.get("related", [])
        
        template = create_document_template(
            title=title,
            file_path=file_path,
            priority=priority,
            source_type=source_type,
            tags=tags,
            summary=summary,
            key_points=key_points,
            related=related,
            base_directory=base_directory
        )
        
        return [
            types.TextContent(
                type="text",
                text=f"✅ Document template created successfully!\n\n"
                     f"{json.dumps(template, indent=2, ensure_ascii=False)}\n\n"
                     f"This template can be used with the 'index_document' tool.\n\n"
                     f"💡 **Content Management Guidelines for Agents**:\n"
                     f"   • If content is SHORT (< 1000 chars): Add directly to 'content' field\n"
                     f"   • If content is LONG: Create file and reference it in document\n"
                     f"   • Always search existing documents first before creating new ones\n"
                     f"   • Update existing content instead of duplicating information\n"
                     f"   • Clean up outdated documents regularly to maintain quality"
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"❌ Failed to create document template: {str(e)}"
            )
        ]
