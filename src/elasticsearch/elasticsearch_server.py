"""
Elasticsearch FastMCP Server - Step by step migration
Tool-by-tool conversion from handlers to FastMCP tools.
File 1/4: Elasticsearch Server
"""
import json
from typing import List, Dict, Any, Optional, Annotated
from datetime import datetime

from fastmcp import FastMCP, Context
from pydantic import Field

from src.elasticsearch.elasticsearch_client import get_es_client
from src.elasticsearch.document_schema import (
    validate_document_structure,
    DocumentValidationError,
    create_document_template as create_doc_template_base,
    format_validation_error
)
from src.elasticsearch.elasticsearch_helper import (
    generate_smart_metadata, 
    generate_fallback_metadata,
    parse_time_parameters,
    analyze_search_results_for_reorganization
)
from src.config.config import load_config

# Create FastMCP app
app = FastMCP(
    name="AgentKnowledgeMCP-Elasticsearch",
    version="1.0.0",
    instructions="Elasticsearch tools for knowledge management"
)


# ================================
# TOOL 1: SEARCH
# ================================

@app.tool(
    description="Search documents in Elasticsearch index with advanced filtering, pagination, and time-based sorting capabilities",
    tags={"elasticsearch", "search", "query"}
)
async def search(
    index: Annotated[str, Field(description="Name of the Elasticsearch index to search")],
    query: Annotated[str, Field(description="Search query text to find matching documents")],
    size: Annotated[int, Field(description="Maximum number of results to return", ge=1, le=1000)] = 10,
    fields: Annotated[Optional[List[str]], Field(description="Specific fields to include in search results")] = None,
    date_from: Annotated[Optional[str], Field(description="Start date filter in ISO format (YYYY-MM-DD)")] = None,
    date_to: Annotated[Optional[str], Field(description="End date filter in ISO format (YYYY-MM-DD)")] = None,
    time_period: Annotated[Optional[str], Field(description="Predefined time period filter (e.g., '7d', '1m', '1y')")] = None,
    sort_by_time: Annotated[str, Field(description="Sort order by timestamp", pattern="^(asc|desc)$")] = "desc"
) -> str:
    """Search documents in Elasticsearch index with optional time-based filtering."""
    try:
        es = get_es_client()

        # Parse time filters
        time_filter = parse_time_parameters(date_from, date_to, time_period)

        # Build search query with optional time filtering
        if time_filter:
            # Combine text search with time filtering
            search_body = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "multi_match": {
                                    "query": query,
                                    "fields": ["title^3", "summary^2", "content", "tags^2", "features^2", "tech_stack^2"]
                                }
                            }
                        ],
                        "filter": [time_filter]
                    }
                }
            }
        else:
            # Standard text search without time filtering
            search_body = {
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["title^3", "summary^2", "content", "tags^2", "features^2", "tech_stack^2"]
                    }
                }
            }

        # Add sorting - prioritize time if time filtering is used
        if time_filter:
            if sort_by_time == "desc":
                search_body["sort"] = [
                    {"last_modified": {"order": "desc"}},  # Primary: newest first
                    "_score"  # Secondary: relevance
                ]
            else:
                search_body["sort"] = [
                    {"last_modified": {"order": "asc"}},  # Primary: oldest first
                    "_score"  # Secondary: relevance
                ]
        else:
            # Default sorting: relevance first, then recency
            search_body["sort"] = [
                "_score",  # Primary sort by relevance
                {"last_modified": {"order": "desc"}}  # Secondary sort by recency
            ]

        search_body["size"] = size

        if fields:
            search_body["_source"] = fields

        result = es.search(index=index, body=search_body)

        # Build time filter description early for use in all branches
        time_filter_desc = ""
        if time_filter:
            if time_period:
                time_filter_desc = f" (filtered by: {time_period})"
            elif date_from or date_to:
                filter_parts = []
                if date_from:
                    filter_parts.append(f"from {date_from}")
                if date_to:
                    filter_parts.append(f"to {date_to}")
                time_filter_desc = f" (filtered by: {' '.join(filter_parts)})"

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
            time_suggestions = ""
            if time_filter:
                time_suggestions = (
                    f"\n\n⏰ **Time Filter Suggestions**:\n" +
                    f"   • Try broader time range (expand dates or use 'month'/'year')\n" +
                    f"   • Remove time filters to search all documents\n" +
                    f"   • Check if documents exist in the specified time period\n" +
                    f"   • Use relative dates like '30d' or '6m' for wider ranges\n"
                )

            return (f"🔍 No results found for '{query}' in index '{index}'{time_filter_desc}\n\n" +
                   f"💡 **Search Optimization Suggestions for Agents**:\n\n" +
                   f"📂 **Try Other Indices**:\n" +
                   f"   • Use 'list_indices' tool to see all available indices\n" +
                   f"   • Search the same query in different indices\n" +
                   f"   • Content might be stored in a different index\n" +
                   f"   • Check indices with similar names or purposes\n\n" +
                   f"🎯 **Try Different Keywords**:\n" +
                   f"   • Use synonyms and related terms\n" +
                   f"   • Try shorter, more general keywords\n" +
                   f"   • Break complex queries into simpler parts\n" +
                   f"   • Use different language variations if applicable\n\n" +
                   f"📅 **Consider Recency**:\n" +
                   f"   • Recent documents may use different terminology\n" +
                   f"   • Try searching with current date/time related terms\n" +
                   f"   • Look for latest trends or recent updates\n" +
                   f"   • Use time_period='month' or 'year' for broader time searches\n\n" +
                   f"🤝 **Ask User for Help**:\n" +
                   f"   • Request user to suggest related keywords\n" +
                   f"   • Ask about specific topics or domains they're interested in\n" +
                   f"   • Get context about what they're trying to find\n" +
                   f"   • Ask for alternative ways to describe their query\n\n" +
                   f"🔧 **Technical Tips**:\n" +
                   f"   • Use broader search terms first, then narrow down\n" +
                   f"   • Check for typos in search terms\n" +
                   f"   • Consider partial word matches\n" +
                   f"   • Try fuzzy matching or wildcard searches" +
                   time_suggestions)

        # Add detailed reorganization analysis for too many results
        reorganization_analysis = analyze_search_results_for_reorganization(formatted_results, query, total_results)

        # Build sorting description
        if time_filter:
            sort_desc = f"sorted by time ({sort_by_time}) then relevance"
        else:
            sort_desc = "sorted by relevance and recency"

        # Build guidance messages that will appear BEFORE results
        guidance_messages = ""
        
        # Limited results guidance (1-3 matches)
        if total_results > 0 and total_results <= 3:
            guidance_messages += (f"💡 **Limited Results Found** ({total_results} matches):\n" +
                                f"   📂 **Check Other Indices**: Use 'list_indices' tool to see all available indices\n" +
                                f"   🔍 **Search elsewhere**: Try the same query in different indices\n" +
                                f"   🎯 **Expand keywords**: Try broader or alternative keywords for more results\n" +
                                f"   🤝 **Ask user**: Request related terms or different perspectives\n" +
                                f"   📊 **Results info**: Sorted by relevance first, then by recency" +
                                (f"\n   ⏰ **Time range**: Consider broader time range if using time filters" if time_filter else "") +
                                f"\n\n")
        
        # Too many results guidance (15+ matches)
        if total_results > 15:
            guidance_messages += (f"🧹 **Too Many Results Found** ({total_results} matches):\n" +
                                f"   📊 **Consider Knowledge Base Reorganization**:\n" +
                                f"      • Ask user: 'Would you like to organize the knowledge base better?'\n" +
                                f"      • List key topics found in search results\n" +
                                f"      • Ask user to confirm which topics to consolidate/update/delete\n" +
                                f"      • Suggest merging similar documents into comprehensive ones\n" +
                                f"      • Propose archiving outdated/redundant information\n" +
                                f"   🎯 **User Collaboration Steps**:\n" +
                                f"      1. 'I found {total_results} documents about this topic'\n" +
                                f"      2. 'Would you like me to help organize them better?'\n" +
                                f"      3. List main themes/topics from results\n" +
                                f"      4. Get user confirmation for reorganization plan\n" +
                                f"      5. Execute: consolidate, update, or delete as agreed\n" +
                                f"   💡 **Quality Goals**: Fewer, better organized, comprehensive documents" +
                                (f"\n   • Consider narrower time range to reduce results" if time_filter else "") +
                                f"\n\n")

        # Add reorganization analysis if present
        if reorganization_analysis:
            guidance_messages += reorganization_analysis + "\n\n"

        return (guidance_messages +
               f"Search results for '{query}' in index '{index}'{time_filter_desc} ({sort_desc}):\n\n" +
               json.dumps({
                   "total": total_results,
                   "results": formatted_results
               }, indent=2, ensure_ascii=False))
    except Exception as e:
        # Provide detailed error messages for different types of Elasticsearch errors
        error_message = "❌ Search failed:\n\n"

        error_str = str(e).lower()
        if "connection" in error_str or "refused" in error_str:
            error_message += "🔌 **Connection Error**: Cannot connect to Elasticsearch server\n"
            error_message += f"📍 Check if Elasticsearch is running at the configured address\n"
            error_message += f"💡 Try: Use 'setup_elasticsearch' tool to start Elasticsearch\n\n"
        elif ("index" in error_str and "not found" in error_str) or "index_not_found_exception" in error_str or "no such index" in error_str:
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

        return error_message


# ================================
# TOOL 2: INDEX_DOCUMENT
# ================================

@app.tool(
    description="Index a document into Elasticsearch with optional schema validation and intelligent duplicate prevention",
    tags={"elasticsearch", "index", "document", "validation"}
)
async def index_document(
    index: Annotated[str, Field(description="Name of the Elasticsearch index to store the document")],
    document: Annotated[Dict[str, Any], Field(description="Document data to index as JSON object")],
    doc_id: Annotated[Optional[str], Field(description="Optional document ID - if not provided, Elasticsearch will auto-generate")] = None,
    validate_schema: Annotated[bool, Field(description="Whether to validate document structure for knowledge base format")] = True
) -> str:
    """Index a document into Elasticsearch with optional schema validation."""
    try:
        es = get_es_client()

        # Validate document structure if requested
        if validate_schema:
            try:
                # Check if this looks like a knowledge base document
                if isinstance(document, dict) and "id" in document and "title" in document:
                    validated_doc = validate_document_structure(document)
                    document = validated_doc

                    # Use the document ID from the validated document if not provided
                    if not doc_id:
                        doc_id = document.get("id")

                else:
                    # For non-knowledge base documents, still validate with strict mode if enabled
                    validated_doc = validate_document_structure(document, is_knowledge_doc=False)
                    document = validated_doc
            except DocumentValidationError as e:
                return f"❌ Validation failed:\n\n{format_validation_error(e)}"
            except Exception as e:
                return f"❌ Validation error: {str(e)}"

        # Index the document
        if doc_id:
            result = es.index(index=index, id=doc_id, body=document)
        else:
            result = es.index(index=index, body=document)

        return (f"✅ Document indexed successfully:\n\n" +
               json.dumps(result, indent=2, ensure_ascii=False) +
               f"\n\n💡 **IMPORTANT: Always Update Existing Documents Instead of Creating Duplicates**:\n" +
               f"   🔍 **BEFORE indexing new content**: Use 'search' tool to find similar documents\n" +
               f"   🔄 **UPDATE existing documents** instead of creating duplicates\n" +
               f"   📝 **For SHORT content**: Store directly in document 'content' field (recommended)\n" +
               f"   📁 **For LONG content**: Create separate files only when absolutely necessary\n" +
               f"   🧹 **Regular cleanup**: Delete outdated/superseded documents to maintain quality\n" +
               f"   🎯 **Search first, create last**: Avoid knowledge base bloat by reusing existing structure\n\n" +
               f"🤝 **Agent Best Practices**:\n" +
               f"   • Always search before creating to prevent duplicates\n" +
               f"   • Ask user: 'Should I update existing document X instead?'\n" +
               f"   • Use meaningful document IDs for better organization\n" +
               f"   • Include relevant tags for improved searchability\n" +
               f"   • Set appropriate priority levels for content importance")

    except Exception as e:
        # Provide detailed error messages for different types of Elasticsearch errors
        error_message = "❌ Document indexing failed:\n\n"

        error_str = str(e).lower()
        if "connection" in error_str or "refused" in error_str:
            error_message += "🔌 **Connection Error**: Cannot connect to Elasticsearch server\n"
            error_message += f"📍 Check if Elasticsearch is running at the configured address\n"
            error_message += f"💡 Try: Use 'setup_elasticsearch' tool to start Elasticsearch\n\n"
        elif ("index" in error_str and "not found" in error_str) or "index_not_found_exception" in error_str:
            error_message += f"📁 **Index Error**: Index '{index}' does not exist\n"
            error_message += f"📍 The target index has not been created yet\n"
            error_message += f"💡 **Suggestions for agents**:\n"
            error_message += f"   1. Use 'create_index' tool to create the index first\n"
            error_message += f"   2. Use 'list_indices' to see available indices\n"
            error_message += f"   3. Check the correct index name for your data type\n\n"
        elif "mapping" in error_str or "field" in error_str:
            error_message += f"🗂️ **Mapping Error**: Document structure conflicts with index mapping\n"
            error_message += f"📍 Document fields don't match the expected index schema\n"
            error_message += f"💡 Try: Adjust document structure or update index mapping\n\n"
        elif "version" in error_str or "conflict" in error_str:
            error_message += f"⚡ **Version Conflict**: Document already exists with different version\n"
            error_message += f"📍 Another process modified this document simultaneously\n"
            error_message += f"💡 Try: Use 'get_document' first, then update with latest version\n\n"
        elif "timeout" in error_str:
            error_message += "⏱️ **Timeout Error**: Indexing operation timed out\n"
            error_message += f"📍 Document may be too large or index overloaded\n"
            error_message += f"💡 Try: Reduce document size or retry later\n\n"
        else:
            error_message += f"⚠️ **Unknown Error**: {str(e)}\n\n"

        error_message += f"🔍 **Technical Details**: {str(e)}"

        return error_message


# ================================
# TOOL 3: DELETE_DOCUMENT
# ================================

@app.tool(
    description="Delete a document from Elasticsearch index by document ID",
    tags={"elasticsearch", "delete", "document"}
)
async def delete_document(
    index: Annotated[str, Field(description="Name of the Elasticsearch index containing the document")],
    doc_id: Annotated[str, Field(description="Document ID to delete from the index")]
) -> str:
    """Delete a document from Elasticsearch index."""
    try:
        es = get_es_client()

        result = es.delete(index=index, id=doc_id)

        return f"✅ Document deleted successfully:\n\n{json.dumps(result, indent=2, ensure_ascii=False)}"

    except Exception as e:
        # Provide detailed error messages for different types of Elasticsearch errors
        error_message = "❌ Failed to delete document:\n\n"

        error_str = str(e).lower()
        if "connection" in error_str or "refused" in error_str:
            error_message += "🔌 **Connection Error**: Cannot connect to Elasticsearch server\n"
            error_message += f"📍 Check if Elasticsearch is running at the configured address\n"
            error_message += f"💡 Try: Use 'setup_elasticsearch' tool to start Elasticsearch\n\n"
        elif ("not_found" in error_str or "not found" in error_str or "does not exist" in error_str) or "index_not_found_exception" in error_str or "no such index" in error_str:
            # Check if it's specifically an index not found error
            if ("index" in error_str and ("not found" in error_str or "not_found" in error_str or "does not exist" in error_str)) or "index_not_found_exception" in error_str or "no such index" in error_str:
                error_message += f"📁 **Index Not Found**: Index '{index}' does not exist\n"
                error_message += f"📍 The target index has not been created yet\n"
                error_message += f"💡 Try: Use 'list_indices' to see available indices\n\n"
            else:
                error_message += f"📄 **Document Not Found**: Document ID '{doc_id}' does not exist\n"
                error_message += f"📍 Cannot delete a document that doesn't exist\n"
                error_message += f"💡 Try: Check document ID or use 'search' to find documents\n\n"
        else:
            error_message += f"⚠️ **Unknown Error**: {str(e)}\n\n"

        error_message += f"🔍 **Technical Details**: {str(e)}"

        return error_message


# ================================
# TOOL 4: GET_DOCUMENT
# ================================

@app.tool(
    description="Retrieve a specific document from Elasticsearch index by document ID",
    tags={"elasticsearch", "get", "document", "retrieve"}
)
async def get_document(
    index: Annotated[str, Field(description="Name of the Elasticsearch index containing the document")],
    doc_id: Annotated[str, Field(description="Document ID to retrieve from the index")]
) -> str:
    """Retrieve a specific document from Elasticsearch index."""
    try:
        es = get_es_client()

        result = es.get(index=index, id=doc_id)

        return f"✅ Document retrieved successfully:\n\n{json.dumps(result, indent=2, ensure_ascii=False)}"

    except Exception as e:
        # Provide detailed error messages for different types of Elasticsearch errors
        error_message = "❌ Failed to get document:\n\n"

        error_str = str(e).lower()
        if "connection" in error_str or "refused" in error_str:
            error_message += "🔌 **Connection Error**: Cannot connect to Elasticsearch server\n"
            error_message += f"📍 Check if Elasticsearch is running at the configured address\n"
            error_message += f"💡 Try: Use 'setup_elasticsearch' tool to start Elasticsearch\n\n"
        elif ("not_found" in error_str or "not found" in error_str) or "index_not_found_exception" in error_str or "no such index" in error_str:
            if "index" in error_str or "index_not_found_exception" in error_str or "no such index" in error_str:
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

        return error_message


# ================================
# TOOL 5: LIST_INDICES
# ================================

@app.tool(
    description="List all available Elasticsearch indices with document count and size statistics",
    tags={"elasticsearch", "list", "indices", "stats"}
)
async def list_indices() -> str:
    """List all available Elasticsearch indices with basic statistics."""
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
                    
                    # Initialize basic index info
                    index_info = {
                        "name": index_name,
                        "docs": doc_count,
                        "size_bytes": size,
                        "description": "No description available",
                        "purpose": "Not documented",
                        "data_types": [],
                        "usage_pattern": "Unknown",
                        "created_date": "Unknown"
                    }
                    
                    # Try to get metadata for this index
                    try:
                        metadata_search = {
                            "query": {
                                "term": {
                                    "index_name": index_name
                                }
                            },
                            "size": 1
                        }
                        
                        metadata_result = es.search(index="index_metadata", body=metadata_search)
                        
                        if metadata_result['hits']['total']['value'] > 0:
                            metadata = metadata_result['hits']['hits'][0]['_source']
                            # Merge metadata into index info
                            index_info.update({
                                "description": metadata.get('description', 'No description available'),
                                "purpose": metadata.get('purpose', 'Not documented'),
                                "data_types": metadata.get('data_types', []),
                                "usage_pattern": metadata.get('usage_pattern', 'Unknown'),
                                "created_date": metadata.get('created_date', 'Unknown'),
                                "retention_policy": metadata.get('retention_policy', 'Not specified'),
                                "related_indices": metadata.get('related_indices', []),
                                "tags": metadata.get('tags', []),
                                "created_by": metadata.get('created_by', 'Unknown'),
                                "has_metadata": True
                            })
                        else:
                            index_info["has_metadata"] = False
                            
                    except Exception:
                        # If metadata index doesn't exist or search fails, keep basic info
                        index_info["has_metadata"] = False
                    
                    indices_info.append(index_info)
                    
                except:
                    indices_info.append({
                        "name": index_name,
                        "docs": "unknown",
                        "size_bytes": "unknown",
                        "description": "Statistics unavailable",
                        "has_metadata": False
                    })

        # Sort indices: metadata-documented first, then by name
        indices_info.sort(key=lambda x: (not x.get('has_metadata', False), x['name']))

        # Format the output with metadata information
        result = "✅ Available indices with metadata:\n\n"
        
        # Count documented vs undocumented
        documented = sum(1 for idx in indices_info if idx.get('has_metadata', False))
        undocumented = len(indices_info) - documented
        
        result += f"📊 **Index Overview**:\n"
        result += f"   📋 Total indices: {len(indices_info)}\n"
        result += f"   ✅ Documented: {documented}\n"
        result += f"   ❌ Undocumented: {undocumented}\n\n"
        
        if undocumented > 0:
            result += f"🚨 **Governance Alert**: {undocumented} indices lack metadata documentation\n"
            result += f"   💡 Use 'create_index_metadata' tool to document missing indices\n"
            result += f"   🎯 Proper documentation improves index management and team collaboration\n\n"
        
        # Group indices by documentation status
        documented_indices = [idx for idx in indices_info if idx.get('has_metadata', False)]
        undocumented_indices = [idx for idx in indices_info if not idx.get('has_metadata', False)]
        
        if documented_indices:
            result += f"📋 **Documented Indices** ({len(documented_indices)}):\n\n"
            for idx in documented_indices:
                size_mb = idx['size_bytes'] / 1048576 if isinstance(idx['size_bytes'], (int, float)) else 0
                result += f"🟢 **{idx['name']}**\n"
                result += f"   📝 Description: {idx['description']}\n"
                result += f"   🎯 Purpose: {idx['purpose']}\n"
                result += f"   📊 Documents: {idx['docs']}, Size: {size_mb:.1f} MB\n"
                result += f"   📂 Data Types: {', '.join(idx.get('data_types', [])) or 'Not specified'}\n"
                result += f"   🔄 Usage: {idx.get('usage_pattern', 'Unknown')}\n"
                result += f"   📅 Created: {idx.get('created_date', 'Unknown')}\n"
                if idx.get('tags'):
                    result += f"   🏷️ Tags: {', '.join(idx['tags'])}\n"
                if idx.get('related_indices'):
                    result += f"   🔗 Related: {', '.join(idx['related_indices'])}\n"
                result += "\n"
        
        if undocumented_indices:
            result += f"❌ **Undocumented Indices** ({len(undocumented_indices)}) - Need Metadata:\n\n"
            for idx in undocumented_indices:
                size_mb = idx['size_bytes'] / 1048576 if isinstance(idx['size_bytes'], (int, float)) else 0
                result += f"🔴 **{idx['name']}**\n"
                result += f"   📊 Documents: {idx['docs']}, Size: {size_mb:.1f} MB\n"
                result += f"   ⚠️ Status: No metadata documentation found\n"
                result += f"   🔧 Action: Use 'create_index_metadata' to document this index\n\n"
        
        # Add metadata improvement suggestions
        if undocumented > 0:
            result += f"💡 **Metadata Improvement Suggestions**:\n"
            result += f"   📋 Document each index's purpose and data types\n"
            result += f"   🎯 Define usage patterns and access frequencies\n"
            result += f"   📅 Record creation dates and retention policies\n"
            result += f"   🔗 Link related indices for better organization\n"
            result += f"   🏷️ Add relevant tags for categorization\n"
            result += f"   👤 Track ownership and responsibility\n\n"
        
        return result

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

        return error_message


# ================================
# TOOL 6: CREATE_INDEX
# ================================

@app.tool(
    description="Create a new Elasticsearch index with optional mapping and settings configuration",
    tags={"elasticsearch", "create", "index", "mapping"}
)
async def create_index(
    index: Annotated[str, Field(description="Name of the new Elasticsearch index to create")],
    mapping: Annotated[Dict[str, Any], Field(description="Index mapping configuration defining field types and properties")],
    settings: Annotated[Optional[Dict[str, Any]], Field(description="Optional index settings for shards, replicas, analysis, etc.")] = None
) -> str:
    """Create a new Elasticsearch index with mapping and optional settings."""
    try:
        es = get_es_client()

        # Special case: Allow creating index_metadata without validation
        if index == "index_metadata":
            body = {"mappings": mapping}
            if settings:
                body["settings"] = settings

            result = es.indices.create(index=index, body=body)

            return (f"✅ Index metadata system initialized successfully!\n\n" +
                   f"📋 **Metadata Index Created**: {index}\n" +
                   f"🔧 **System Status**: Index metadata management now active\n" +
                   f"✅ **Next Steps**:\n" +
                   f"   1. Use 'create_index_metadata' to document your indices\n" +
                   f"   2. Then use 'create_index' to create actual indices\n" +
                   f"   3. Use 'list_indices' to see metadata integration\n\n" +
                   f"🎯 **Benefits Unlocked**:\n" +
                   f"   • Index governance and documentation enforcement\n" +
                   f"   • Enhanced index listing with descriptions\n" +
                   f"   • Proper cleanup workflows for index deletion\n" +
                   f"   • Team collaboration through shared index understanding\n\n" +
                   f"📋 **Technical Details**:\n{json.dumps(result, indent=2, ensure_ascii=False)}")

        # Check if metadata document exists for this index
        metadata_index = "index_metadata"
        try:
            # Search for existing metadata document
            search_body = {
                "query": {
                    "term": {
                        "index_name.keyword": index
                    }
                },
                "size": 1
            }
            
            metadata_result = es.search(index=metadata_index, body=search_body)
            
            if metadata_result['hits']['total']['value'] == 0:
                return (f"❌ Index creation blocked - Missing metadata documentation!\n\n" +
                       f"🚨 **MANDATORY: Create Index Metadata First**:\n" +
                       f"   📋 **Required Action**: Before creating index '{index}', you must document it\n" +
                       f"   🔧 **Use This Tool**: Call 'create_index_metadata' tool first\n" +
                       f"   📝 **Required Information**:\n" +
                       f"      • Index purpose and description\n" +
                       f"      • Data types and content it will store\n" +
                       f"      • Usage patterns and access frequency\n" +
                       f"      • Retention policies and lifecycle\n" +
                       f"      • Related indices and dependencies\n\n" +
                       f"💡 **Workflow**:\n" +
                       f"   1. Call 'create_index_metadata' with index name and description\n" +
                       f"   2. Then call 'create_index' again to create the actual index\n" +
                       f"   3. This ensures proper documentation and governance\n\n" +
                       f"🎯 **Why This Matters**:\n" +
                       f"   • Prevents orphaned indices without documentation\n" +
                       f"   • Ensures team understands index purpose\n" +
                       f"   • Facilitates better index management and cleanup\n" +
                       f"   • Provides context for future maintenance")
            
        except Exception as metadata_error:
            # If metadata index doesn't exist, that's also a problem
            if "index_not_found" in str(metadata_error).lower():
                return (f"❌ Index creation blocked - Metadata system not initialized!\n\n" +
                       f"🚨 **SETUP REQUIRED**: Index metadata system needs initialization\n" +
                       f"   📋 **Step 1**: Create metadata index first using 'create_index' with name 'index_metadata'\n" +
                       f"   📝 **Step 2**: Use this mapping for metadata index:\n" +
                       f"```json\n" +
                       f"{{\n" +
                       f"  \"properties\": {{\n" +
                       f"    \"index_name\": {{\"type\": \"keyword\"}},\n" +
                       f"    \"description\": {{\"type\": \"text\"}},\n" +
                       f"    \"purpose\": {{\"type\": \"text\"}},\n" +
                       f"    \"data_types\": {{\"type\": \"keyword\"}},\n" +
                       f"    \"created_by\": {{\"type\": \"keyword\"}},\n" +
                       f"    \"created_date\": {{\"type\": \"date\"}},\n" +
                       f"    \"usage_pattern\": {{\"type\": \"keyword\"}},\n" +
                       f"    \"retention_policy\": {{\"type\": \"text\"}},\n" +
                       f"    \"related_indices\": {{\"type\": \"keyword\"}},\n" +
                       f"    \"tags\": {{\"type\": \"keyword\"}}\n" +
                       f"  }}\n" +
                       f"}}\n" +
                       f"```\n" +
                       f"   🔧 **Step 3**: Then use 'create_index_metadata' to document your index\n" +
                       f"   ✅ **Step 4**: Finally create your actual index\n\n" +
                       f"💡 **This is a one-time setup** - once metadata index exists, normal workflow applies")

        # If we get here, metadata exists - proceed with index creation
        body = {"mappings": mapping}
        if settings:
            body["settings"] = settings

        result = es.indices.create(index=index, body=body)

        return f"✅ Index '{index}' created successfully:\n\n{json.dumps(result, indent=2, ensure_ascii=False)}"

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

        return error_message


# ================================
# TOOL 7: DELETE_INDEX
# ================================

@app.tool(
    description="Delete an Elasticsearch index and all its documents permanently",
    tags={"elasticsearch", "delete", "index", "destructive"}
)
async def delete_index(
    index: Annotated[str, Field(description="Name of the Elasticsearch index to delete")]
) -> str:
    """Delete an Elasticsearch index permanently."""
    try:
        es = get_es_client()

        # Check if metadata document exists for this index
        metadata_index = "index_metadata"
        try:
            # Search for existing metadata document
            search_body = {
                "query": {
                    "term": {
                        "index_name.keyword": index
                    }
                },
                "size": 1
            }
            
            metadata_result = es.search(index=metadata_index, body=search_body)
            
            if metadata_result['hits']['total']['value'] > 0:
                metadata_doc = metadata_result['hits']['hits'][0]
                metadata_id = metadata_doc['_id']
                metadata_source = metadata_doc['_source']
                
                return (f"❌ Index deletion blocked - Metadata cleanup required!\n\n" +
                       f"🚨 **MANDATORY: Remove Index Metadata First**:\n" +
                       f"   📋 **Found Metadata Document**: {metadata_id}\n" +
                       f"   📝 **Index Description**: {metadata_source.get('description', 'No description')}\n" +
                       f"   🔧 **Required Action**: Delete metadata document before removing index\n\n" +
                       f"💡 **Cleanup Workflow**:\n" +
                       f"   1. Call 'delete_index_metadata' with index name '{index}'\n" +
                       f"   2. Then call 'delete_index' again to remove the actual index\n" +
                       f"   3. This ensures proper cleanup and audit trail\n\n" +
                       f"📊 **Metadata Details**:\n" +
                       f"   • Purpose: {metadata_source.get('purpose', 'Not specified')}\n" +
                       f"   • Data Types: {', '.join(metadata_source.get('data_types', []))}\n" +
                       f"   • Created: {metadata_source.get('created_date', 'Unknown')}\n" +
                       f"   • Usage: {metadata_source.get('usage_pattern', 'Not specified')}\n\n" +
                       f"🎯 **Why This Matters**:\n" +
                       f"   • Maintains clean metadata registry\n" +
                       f"   • Prevents orphaned documentation\n" +
                       f"   • Ensures proper audit trail for deletions\n" +
                       f"   • Confirms intentional removal with full context")
            
        except Exception as metadata_error:
            # If metadata index doesn't exist, warn but allow deletion
            if "index_not_found" in str(metadata_error).lower():
                # Proceed with deletion but warn about missing metadata system
                result = es.indices.delete(index=index)
                
                return (f"⚠️ Index '{index}' deleted but metadata system is missing:\n\n" +
                       f"{json.dumps(result, indent=2, ensure_ascii=False)}\n\n" +
                       f"🚨 **Warning**: No metadata tracking system found\n" +
                       f"   📋 Consider setting up 'index_metadata' index for better governance\n" +
                       f"   💡 Use 'create_index_metadata' tool for future index documentation")

        # If we get here, no metadata found - proceed with deletion
        result = es.indices.delete(index=index)

        return f"✅ Index '{index}' deleted successfully:\n\n{json.dumps(result, indent=2, ensure_ascii=False)}"

    except Exception as e:
        # Provide detailed error messages for different types of Elasticsearch errors
        error_message = "❌ Failed to delete index:\n\n"

        error_str = str(e).lower()
        if "connection" in error_str or "refused" in error_str:
            error_message += "🔌 **Connection Error**: Cannot connect to Elasticsearch server\n"
            error_message += f"📍 Check if Elasticsearch is running at the configured address\n"
            error_message += f"💡 Try: Use 'setup_elasticsearch' tool to start Elasticsearch\n\n"
        elif ("not_found" in error_str or "not found" in error_str) or "index_not_found_exception" in error_str or "no such index" in error_str:
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

        return error_message


# ================================
# TOOL 8: VALIDATE_DOCUMENT_SCHEMA
# ================================

@app.tool(
    description="Validate document structure against knowledge base schema and provide formatting guidance",
    tags={"elasticsearch", "validation", "document", "schema"}
)
async def validate_document_schema(
    document: Annotated[Dict[str, Any], Field(description="Document object to validate against knowledge base schema format")]
) -> str:
    """Validate document structure against knowledge base schema standards."""
    try:
        validated_doc = validate_document_structure(document)

        return (f"✅ Document validation successful!\n\n" +
               f"Validated document:\n{json.dumps(validated_doc, indent=2, ensure_ascii=False)}\n\n" +
               f"Document is ready to be indexed.\n\n" +
               f"🚨 **MANDATORY: Check for Existing Documents First**:\n" +
               f"   🔍 **Search for similar content**: Use 'search' tool with relevant keywords\n" +
               f"   🔄 **Update instead of duplicate**: Modify existing documents when possible\n" +
               f"   📏 **Content length check**: If < 1000 chars, store in 'content' field directly\n" +
               f"   📁 **File creation**: Only for truly long content that needs separate storage\n" +
               f"   🎯 **Quality over quantity**: Prevent knowledge base bloat through smart reuse")

    except DocumentValidationError as e:
        return format_validation_error(e)
    except Exception as e:
        return f"❌ Validation error: {str(e)}"


# ================================
# TOOL 10: BATCH_INDEX_DIRECTORY
# ================================

@app.tool(
    description="Batch index all documents from a directory into Elasticsearch with AI-enhanced metadata generation and comprehensive file processing",
    tags={"elasticsearch", "batch", "directory", "index", "bulk", "ai-enhanced"}
)
async def batch_index_directory(
    index: Annotated[str, Field(description="Name of the Elasticsearch index to store the documents")],
    directory_path: Annotated[str, Field(description="Path to directory containing documents to index")],
    file_pattern: Annotated[str, Field(description="File pattern to match (e.g., '*.md', '*.txt', '*')")] = "*.md",
    validate_schema: Annotated[bool, Field(description="Whether to validate document structure for knowledge base format")] = True,
    recursive: Annotated[bool, Field(description="Whether to search subdirectories recursively")] = True,
    skip_existing: Annotated[bool, Field(description="Skip files that already exist in index (check by filename)")] = False,
    max_file_size: Annotated[int, Field(description="Maximum file size in bytes to process", ge=1, le=10485760)] = 1048576,  # 1MB default
    use_ai_enhancement: Annotated[bool, Field(description="Use AI to generate intelligent tags and key points for each document")] = True,
    ctx: Context = None
) -> str:
    """Batch index all documents from a directory into Elasticsearch."""
    try:
        from pathlib import Path
        import os
        
        # Check directory exists and is valid
        directory = Path(directory_path)
        if not directory.exists():
            return f"❌ Directory not found: {directory_path}\n💡 Check the directory path spelling and location"
        
        if not directory.is_dir():
            return f"❌ Path is not a directory: {directory_path}\n💡 Provide a directory path, not a file path"
        
        # Get Elasticsearch client
        es = get_es_client()
        
        # Find all matching files
        if recursive:
            files = list(directory.rglob(file_pattern))
        else:
            files = list(directory.glob(file_pattern))
        
        if not files:
            return f"❌ No files found matching pattern '{file_pattern}' in directory: {directory_path}\n💡 Try a different file pattern like '*.txt', '*.json', or '*'"
        
        # Filter out files that are too large
        valid_files = []
        skipped_size = []
        for file_path in files:
            if file_path.is_file():
                try:
                    file_size = file_path.stat().st_size
                    if file_size <= max_file_size:
                        valid_files.append(file_path)
                    else:
                        skipped_size.append((file_path, file_size))
                except Exception as e:
                    # Skip files we can't stat
                    continue
        
        if not valid_files:
            return f"❌ No valid files found (all files too large or inaccessible)\n💡 Increase max_file_size or check file permissions"
        
        # Check for existing documents if skip_existing is True
        existing_docs = set()
        if skip_existing:
            try:
                # Search for existing documents by titles
                search_body = {
                    "query": {"match_all": {}},
                    "size": 10000,  # Get many docs to check
                    "_source": ["title", "id"]
                }
                existing_result = es.search(index=index, body=search_body)
                for hit in existing_result['hits']['hits']:
                    source = hit.get('_source', {})
                    if 'title' in source:
                        existing_docs.add(source['title'])
                    if 'id' in source:
                        existing_docs.add(source['id'])
            except Exception:
                # If we can't check existing docs, proceed anyway
                pass
        
        # Process files
        successful = []
        failed = []
        skipped_existing = []
        
        for file_path in valid_files:
            try:
                file_name = file_path.name
                title = file_path.stem.replace('_', ' ').replace('-', ' ').title()
                
                # Skip if document with same title already exists in index
                if skip_existing and title in existing_docs:
                    skipped_existing.append(file_name)
                    continue
                
                # Read file content
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    # Try with different encodings
                    try:
                        with open(file_path, 'r', encoding='latin-1') as f:
                            content = f.read()
                    except Exception as e:
                        failed.append((file_name, f"Encoding error: {str(e)}"))
                        continue
                except Exception as e:
                    failed.append((file_name, f"Read error: {str(e)}"))
                    continue
                
                # Create document from file
                relative_path = file_path.relative_to(directory)
                doc_id = f"{file_path.stem}_{hash(str(relative_path)) % 100000}"  # Create unique ID
                
                # Initialize basic tags and key points
                base_tags = [
                    "batch-indexed",
                    file_path.suffix[1:] if file_path.suffix else "no-extension",
                    directory.name
                ]
                
                base_key_points = [
                    f"Content length: {len(content)} characters",
                    f"Source directory: {directory.name}"
                ]
                
                final_tags = base_tags.copy()
                final_key_points = base_key_points.copy()
                final_summary = f"Document from {file_name}"
                
                # Use AI enhancement if requested and context is available
                if use_ai_enhancement and ctx and content.strip():
                    try:
                        await ctx.info(f"🤖 Generating AI metadata and smart content for: {file_name}")
                        ai_metadata = await generate_smart_metadata(title, content, ctx)
                        
                        # Merge AI-generated tags with base tags
                        ai_tags = ai_metadata.get("tags", [])
                        for tag in ai_tags:
                            if tag not in final_tags:
                                final_tags.append(tag)
                        
                        # Merge AI-generated key points with base points
                        ai_key_points = ai_metadata.get("key_points", [])
                        for point in ai_key_points:
                            if point not in final_key_points:
                                final_key_points.append(point)
                        
                        # Use AI-generated smart summary and enhanced content
                        ai_summary = ai_metadata.get("smart_summary", "")
                        ai_enhanced_content = ai_metadata.get("enhanced_content", "")
                        
                        if ai_summary:
                            final_summary = ai_summary
                        elif len(content) > 100:
                            # Fallback to content preview if no AI summary
                            content_preview = content[:300].strip()
                            if content_preview:
                                final_summary = content_preview + ("..." if len(content) > 300 else "")
                        
                        # Use enhanced content if available and substantially different
                        if ai_enhanced_content and len(ai_enhanced_content) > len(content) * 0.8:
                            content = ai_enhanced_content
                                
                    except Exception as e:
                        await ctx.warning(f"AI enhancement failed for {file_name}: {str(e)}")
                
                document = {
                    "id": doc_id,
                    "title": title,
                    "summary": final_summary,
                    "content": content,
                    "last_modified": datetime.now().isoformat(),
                    "priority": "medium",
                    "tags": final_tags,
                    "related": [],
                    "source_type": "documentation",
                    "key_points": final_key_points
                }
                
                # Validate document if requested
                if validate_schema:
                    try:
                        validated_doc = validate_document_structure(document)
                        document = validated_doc
                    except DocumentValidationError as e:
                        failed.append((file_name, f"Validation error: {str(e)}"))
                        continue
                    except Exception as e:
                        failed.append((file_name, f"Validation error: {str(e)}"))
                        continue
                
                # Index the document
                try:
                    result = es.index(index=index, id=doc_id, body=document)
                    successful.append((file_name, doc_id, result.get('result', 'unknown')))
                except Exception as e:
                    failed.append((file_name, f"Indexing error: {str(e)}"))
                    continue
                    
            except Exception as e:
                failed.append((file_path.name, f"Processing error: {str(e)}"))
                continue
        
        # Build result summary
        total_processed = len(successful) + len(failed) + len(skipped_existing)
        result_summary = f"✅ Batch indexing completed for directory: {directory_path}\n\n"
        
        # Summary statistics
        result_summary += f"📊 **Processing Summary**:\n"
        result_summary += f"   📁 Directory: {directory_path}\n"
        result_summary += f"   🔍 Pattern: {file_pattern} (recursive: {recursive})\n"
        result_summary += f"   📄 Files found: {len(files)}\n"
        result_summary += f"   ✅ Successfully indexed: {len(successful)}\n"
        result_summary += f"   ❌ Failed: {len(failed)}\n"
        
        if skipped_existing:
            result_summary += f"   ⏭️ Skipped (already exist): {len(skipped_existing)}\n"
        
        if skipped_size:
            result_summary += f"   📏 Skipped (too large): {len(skipped_size)}\n"
        
        result_summary += f"   🎯 Index: {index}\n"
        
        # AI Enhancement info
        if use_ai_enhancement and ctx:
            result_summary += f"   🤖 AI Enhancement: Enabled (generated intelligent tags and key points)\n"
        else:
            result_summary += f"   🤖 AI Enhancement: Disabled (using basic metadata)\n"
        
        result_summary += "\n"
        
        # Successful indexing details
        if successful:
            result_summary += f"✅ **Successfully Indexed** ({len(successful)} files):\n"
            for file_name, doc_id, index_result in successful[:10]:  # Show first 10
                result_summary += f"   📄 {file_name} → {doc_id} ({index_result})\n"
            if len(successful) > 10:
                result_summary += f"   ... and {len(successful) - 10} more files\n"
            result_summary += "\n"
        
        # Failed indexing details
        if failed:
            result_summary += f"❌ **Failed to Index** ({len(failed)} files):\n"
            for file_name, error_msg in failed[:5]:  # Show first 5 errors
                result_summary += f"   📄 {file_name}: {error_msg}\n"
            if len(failed) > 5:
                result_summary += f"   ... and {len(failed) - 5} more errors\n"
            result_summary += "\n"
        
        # Skipped files details
        if skipped_existing:
            result_summary += f"⏭️ **Skipped (Already Exist)** ({len(skipped_existing)} files):\n"
            for file_name in skipped_existing[:5]:
                result_summary += f"   📄 {file_name}\n"
            if len(skipped_existing) > 5:
                result_summary += f"   ... and {len(skipped_existing) - 5} more files\n"
            result_summary += "\n"
        
        if skipped_size:
            result_summary += f"📏 **Skipped (Too Large)** ({len(skipped_size)} files):\n"
            for file_path, file_size in skipped_size[:3]:
                size_mb = file_size / 1048576
                result_summary += f"   📄 {file_path.name}: {size_mb:.1f} MB\n"
            if len(skipped_size) > 3:
                result_summary += f"   ... and {len(skipped_size) - 3} more large files\n"
            result_summary += f"   💡 Increase max_file_size to include these files\n\n"
        
        # Performance tips
        if len(successful) > 0:
            result_summary += f"🚀 **Performance Tips for Future Batches**:\n"
            result_summary += f"   🔄 Use skip_existing=True to avoid reindexing\n"
            result_summary += f"   📂 Process subdirectories separately for better control\n"
            result_summary += f"   🔍 Use specific file patterns (*.md, *.txt) for faster processing\n"
            result_summary += f"   📏 Adjust max_file_size based on your content needs\n"
            if use_ai_enhancement:
                result_summary += f"   🤖 AI enhancement adds ~2-3 seconds per file but greatly improves metadata quality\n"
                result_summary += f"   ⚡ Set use_ai_enhancement=False for faster processing with basic metadata\n"
            else:
                result_summary += f"   🤖 Enable use_ai_enhancement=True for intelligent tags and key points\n"
            result_summary += "\n"
        
        # Knowledge base recommendations
        if len(successful) > 20:
            result_summary += f"🧹 **Knowledge Base Organization Recommendation**:\n"
            result_summary += f"   📊 You've indexed {len(successful)} documents from this batch\n"
            result_summary += f"   💡 Consider organizing them by topics or themes\n"
            result_summary += f"   🔍 Use the 'search' tool to find related documents for consolidation\n"
            result_summary += f"   🎯 Group similar content to improve knowledge base quality\n"
        
        return result_summary
        
    except Exception as e:
        error_message = "❌ Batch indexing failed:\n\n"
        
        error_str = str(e).lower()
        if "connection" in error_str or "refused" in error_str:
            error_message += "🔌 **Connection Error**: Cannot connect to Elasticsearch server\n"
            error_message += f"📍 Check if Elasticsearch is running at the configured address\n"
            error_message += f"💡 Try: Use 'setup_elasticsearch' tool to start Elasticsearch\n\n"
        elif ("index" in error_str and "not found" in error_str) or "index_not_found_exception" in error_str:
            error_message += f"📁 **Index Error**: Index '{index}' does not exist\n"
            error_message += f"📍 The target index has not been created yet\n"
            error_message += f"💡 Try: Use 'create_index' tool to create the index first\n\n"
        elif "permission" in error_str or "access denied" in error_str:
            error_message += f"🔒 **Permission Error**: Access denied to directory or files\n"
            error_message += f"📍 Insufficient permissions to read directory or files\n"
            error_message += f"💡 Try: Check directory permissions or verify file access rights\n\n"
        else:
            error_message += f"⚠️ **Unknown Error**: {str(e)}\n\n"
        
        error_message += f"🔍 **Technical Details**: {str(e)}"
        return error_message


# ================================
# TOOL 9: CREATE_DOCUMENT_TEMPLATE
# ================================

@app.tool(
    description="Create a properly structured document template for knowledge base with AI-generated metadata and formatting",
    tags={"elasticsearch", "document", "template", "knowledge-base", "ai-enhanced"}
)
async def create_document_template(
    title: Annotated[str, Field(description="Document title for the knowledge base entry")],
    content: Annotated[str, Field(description="Document content for AI analysis and metadata generation")] = "",
    priority: Annotated[str, Field(description="Priority level for the document", pattern="^(high|medium|low)$")] = "medium",
    source_type: Annotated[str, Field(description="Type of source content", pattern="^(markdown|code|config|documentation|tutorial)$")] = "markdown",
    tags: Annotated[List[str], Field(description="Additional manual tags (will be merged with AI-generated tags)")] = [],
    summary: Annotated[str, Field(description="Brief summary description of the document content")] = "",
    key_points: Annotated[List[str], Field(description="Additional manual key points (will be merged with AI-generated points)")] = [],
    related: Annotated[List[str], Field(description="List of related document IDs or references")] = [],
    use_ai_enhancement: Annotated[bool, Field(description="Use AI to generate intelligent tags and key points")] = True,
    ctx: Context = None
) -> str:
    """Create a properly structured document template for knowledge base indexing with AI-generated metadata."""
    try:
        # Initialize metadata
        final_tags = list(tags)  # Copy manual tags
        final_key_points = list(key_points)  # Copy manual key points
        
        # Use AI enhancement if requested and content is provided
        if use_ai_enhancement and content.strip() and ctx:
            try:
                await ctx.info("🤖 Generating intelligent metadata and smart content using AI...")
                ai_metadata = await generate_smart_metadata(title, content, ctx)
                
                # Merge AI-generated tags with manual tags
                ai_tags = ai_metadata.get("tags", [])
                for tag in ai_tags:
                    if tag not in final_tags:
                        final_tags.append(tag)
                
                # Merge AI-generated key points with manual points
                ai_key_points = ai_metadata.get("key_points", [])
                for point in ai_key_points:
                    if point not in final_key_points:
                        final_key_points.append(point)
                
                # Use AI-generated smart summary if available
                ai_summary = ai_metadata.get("smart_summary", "")
                if ai_summary and not summary:
                    summary = ai_summary
                
                # Use AI-enhanced content if available and better
                ai_enhanced_content = ai_metadata.get("enhanced_content", "")
                if ai_enhanced_content and len(ai_enhanced_content) > len(content) * 0.8:
                    content = ai_enhanced_content
                        
                await ctx.info(f"✅ AI generated {len(ai_tags)} tags, {len(ai_key_points)} key points, smart summary, and enhanced content")
                
            except Exception as e:
                await ctx.warning(f"AI enhancement failed: {str(e)}, using manual metadata only")
        
        # Generate auto-summary if not provided and content is available
        if not summary and content.strip():
            if len(content) > 200:
                summary = content[:200].strip() + "..."
            else:
                summary = content.strip()

        template = create_doc_template_base(
            title=title,
            priority=priority,
            source_type=source_type,
            tags=final_tags,
            summary=summary,
            key_points=final_key_points,
            related=related
        )

        ai_info = ""
        if use_ai_enhancement and ctx:
            ai_info = f"\n🤖 **AI Enhancement Used**: Generated {len(final_tags)} total tags and {len(final_key_points)} total key points\n"

        return (f"✅ Document template created successfully with AI-enhanced metadata!\n\n" +
               f"{json.dumps(template, indent=2, ensure_ascii=False)}\n" +
               ai_info +
               f"\nThis template can be used with the 'index_document' tool.\n\n" +
               f"⚠️ **CRITICAL: Search Before Creating - Avoid Duplicates**:\n" +
               f"   🔍 **STEP 1**: Use 'search' tool to check if similar content already exists\n" +
               f"   🔄 **STEP 2**: If found, UPDATE existing document instead of creating new one\n" +
               f"   📝 **STEP 3**: For SHORT content (< 1000 chars): Add directly to 'content' field\n" +
               f"   📁 **STEP 4**: For LONG content: Create file only when truly necessary\n" +
               f"   🧹 **STEP 5**: Clean up outdated documents regularly to maintain quality\n" +
               f"   🎯 **Remember**: Knowledge base quality > quantity - avoid bloat!")

    except Exception as e:
        return f"❌ Failed to create document template: {str(e)}"


# ================================
# TOOL 11: CREATE_INDEX_METADATA
# ================================

@app.tool(
    description="Create metadata documentation for an Elasticsearch index to ensure proper governance and documentation",
    tags={"elasticsearch", "metadata", "documentation", "governance"}
)
async def create_index_metadata(
    index_name: Annotated[str, Field(description="Name of the index to document")],
    description: Annotated[str, Field(description="Detailed description of the index purpose and content")],
    purpose: Annotated[str, Field(description="Primary purpose and use case for this index")],
    data_types: Annotated[List[str], Field(description="Types of data stored in this index (e.g., 'documents', 'logs', 'metrics')")] = [],
    usage_pattern: Annotated[str, Field(description="How the index is accessed (e.g., 'read-heavy', 'write-heavy', 'mixed')")] = "mixed",
    retention_policy: Annotated[str, Field(description="Data retention policy and lifecycle management")] = "No specific policy",
    related_indices: Annotated[List[str], Field(description="Names of related or dependent indices")] = [],
    tags: Annotated[List[str], Field(description="Tags for categorizing and organizing indices")] = [],
    created_by: Annotated[str, Field(description="Team or person responsible for this index")] = "Unknown"
) -> str:
    """Create comprehensive metadata documentation for an Elasticsearch index."""
    try:
        es = get_es_client()
        
        # Check if metadata index exists
        metadata_index = "index_metadata"
        try:
            es.indices.get(index=metadata_index)
        except Exception:
            # Create metadata index if it doesn't exist
            metadata_mapping = {
                "properties": {
                    "index_name": {"type": "keyword"},
                    "description": {"type": "text"},
                    "purpose": {"type": "text"},
                    "data_types": {"type": "keyword"},
                    "created_by": {"type": "keyword"},
                    "created_date": {"type": "date"},
                    "usage_pattern": {"type": "keyword"},
                    "retention_policy": {"type": "text"},
                    "related_indices": {"type": "keyword"},
                    "tags": {"type": "keyword"},
                    "last_updated": {"type": "date"},
                    "updated_by": {"type": "keyword"}
                }
            }
            
            try:
                es.indices.create(index=metadata_index, body={"mappings": metadata_mapping})
            except Exception as create_error:
                if "already exists" not in str(create_error).lower():
                    return f"❌ Failed to create metadata index: {str(create_error)}"
        
        # Check if metadata already exists for this index
        search_body = {
            "query": {
                "term": {
                    "index_name.keyword": index_name
                }
            },
            "size": 1
        }
        
        existing_result = es.search(index=metadata_index, body=search_body)
        
        if existing_result['hits']['total']['value'] > 0:
            existing_doc = existing_result['hits']['hits'][0]
            existing_id = existing_doc['_id']
            existing_data = existing_doc['_source']
            
            return (f"⚠️ Index metadata already exists for '{index_name}'!\n\n" +
                   f"📋 **Existing Metadata** (ID: {existing_id}):\n" +
                   f"   📝 Description: {existing_data.get('description', 'No description')}\n" +
                   f"   🎯 Purpose: {existing_data.get('purpose', 'No purpose')}\n" +
                   f"   📂 Data Types: {', '.join(existing_data.get('data_types', []))}\n" +
                   f"   👤 Created By: {existing_data.get('created_by', 'Unknown')}\n" +
                   f"   📅 Created: {existing_data.get('created_date', 'Unknown')}\n\n" +
                   f"💡 **Options**:\n" +
                   f"   🔄 **Update**: Use 'update_index_metadata' to modify existing documentation\n" +
                   f"   🗑️ **Replace**: Use 'delete_index_metadata' then 'create_index_metadata'\n" +
                   f"   ✅ **Keep**: Current metadata is sufficient, proceed with 'create_index'\n\n" +
                   f"🚨 **Note**: You can now create the index '{index_name}' since metadata exists")
        
        # Create new metadata document
        current_time = datetime.now().isoformat()
        
        metadata_doc = {
            "index_name": index_name,
            "description": description,
            "purpose": purpose,
            "data_types": data_types,
            "created_by": created_by,
            "created_date": current_time,
            "usage_pattern": usage_pattern,
            "retention_policy": retention_policy,
            "related_indices": related_indices,
            "tags": tags,
            "last_updated": current_time,
            "updated_by": created_by
        }
        
        # Generate a consistent document ID
        metadata_id = f"metadata_{index_name}"
        
        result = es.index(index=metadata_index, id=metadata_id, body=metadata_doc)
        
        return (f"✅ Index metadata created successfully!\n\n" +
               f"📋 **Metadata Details**:\n" +
               f"   🎯 Index: {index_name}\n" +
               f"   📝 Description: {description}\n" +
               f"   🎯 Purpose: {purpose}\n" +
               f"   📂 Data Types: {', '.join(data_types) if data_types else 'None specified'}\n" +
               f"   🔄 Usage Pattern: {usage_pattern}\n" +
               f"   📅 Retention: {retention_policy}\n" +
               f"   🔗 Related Indices: {', '.join(related_indices) if related_indices else 'None'}\n" +
               f"   🏷️ Tags: {', '.join(tags) if tags else 'None'}\n" +
               f"   👤 Created By: {created_by}\n" +
               f"   📅 Created: {current_time}\n\n" +
               f"✅ **Next Steps**:\n" +
               f"   🔧 You can now use 'create_index' to create the actual index '{index_name}'\n" +
               f"   📊 Use 'list_indices' to see this metadata in the index listing\n" +
               f"   🔄 Use 'update_index_metadata' if you need to modify this documentation\n\n" +
               f"🎯 **Benefits Achieved**:\n" +
               f"   • Index purpose is clearly documented\n" +
               f"   • Team collaboration is improved through shared understanding\n" +
               f"   • Future maintenance is simplified with proper context\n" +
               f"   • Index governance and compliance are maintained")
        
    except Exception as e:
        error_message = "❌ Failed to create index metadata:\n\n"
        
        error_str = str(e).lower()
        if "connection" in error_str or "refused" in error_str:
            error_message += "🔌 **Connection Error**: Cannot connect to Elasticsearch server\n"
            error_message += f"📍 Check if Elasticsearch is running at the configured address\n"
            error_message += f"💡 Try: Use 'setup_elasticsearch' tool to start Elasticsearch\n\n"
        else:
            error_message += f"⚠️ **Unknown Error**: {str(e)}\n\n"
        
        error_message += f"🔍 **Technical Details**: {str(e)}"
        return error_message


# ================================
# TOOL 12: UPDATE_INDEX_METADATA
# ================================

@app.tool(
    description="Update existing metadata documentation for an Elasticsearch index",
    tags={"elasticsearch", "metadata", "update", "documentation"}
)
async def update_index_metadata(
    index_name: Annotated[str, Field(description="Name of the index to update metadata for")],
    description: Annotated[Optional[str], Field(description="Updated description of the index purpose and content")] = None,
    purpose: Annotated[Optional[str], Field(description="Updated primary purpose and use case")] = None,
    data_types: Annotated[Optional[List[str]], Field(description="Updated types of data stored in this index")] = None,
    usage_pattern: Annotated[Optional[str], Field(description="Updated access pattern")] = None,
    retention_policy: Annotated[Optional[str], Field(description="Updated data retention policy")] = None,
    related_indices: Annotated[Optional[List[str]], Field(description="Updated related or dependent indices")] = None,
    tags: Annotated[Optional[List[str]], Field(description="Updated tags for categorization")] = None,
    updated_by: Annotated[str, Field(description="Person or team making this update")] = "Unknown"
) -> str:
    """Update existing metadata documentation for an Elasticsearch index."""
    try:
        es = get_es_client()
        metadata_index = "index_metadata"
        
        # Search for existing metadata
        search_body = {
            "query": {
                "term": {
                    "index_name.keyword": index_name
                }
            },
            "size": 1
        }
        
        existing_result = es.search(index=metadata_index, body=search_body)
        
        if existing_result['hits']['total']['value'] == 0:
            return (f"❌ No metadata found for index '{index_name}'!\n\n" +
                   f"🚨 **Missing Metadata**: Cannot update non-existent documentation\n" +
                   f"   💡 **Solution**: Use 'create_index_metadata' to create documentation first\n" +
                   f"   📋 **Required**: Provide description, purpose, and data types\n" +
                   f"   ✅ **Then**: Use this update tool for future modifications\n\n" +
                   f"🔍 **Alternative**: Use 'list_indices' to see all documented indices")
        
        # Get existing document
        existing_doc = existing_result['hits']['hits'][0]
        existing_id = existing_doc['_id']
        existing_data = existing_doc['_source']
        
        # Prepare update data - only update provided fields
        update_data = {
            "last_updated": datetime.now().isoformat(),
            "updated_by": updated_by
        }
        
        if description is not None:
            update_data["description"] = description
        if purpose is not None:
            update_data["purpose"] = purpose
        if data_types is not None:
            update_data["data_types"] = data_types
        if usage_pattern is not None:
            update_data["usage_pattern"] = usage_pattern
        if retention_policy is not None:
            update_data["retention_policy"] = retention_policy
        if related_indices is not None:
            update_data["related_indices"] = related_indices
        if tags is not None:
            update_data["tags"] = tags
        
        # Update the document
        result = es.update(index=metadata_index, id=existing_id, body={"doc": update_data})
        
        # Get updated document to show changes
        updated_result = es.get(index=metadata_index, id=existing_id)
        updated_data = updated_result['_source']
        
        # Build change summary
        changes_made = []
        if description is not None:
            changes_made.append(f"   📝 Description: {existing_data.get('description', 'None')} → {description}")
        if purpose is not None:
            changes_made.append(f"   🎯 Purpose: {existing_data.get('purpose', 'None')} → {purpose}")
        if data_types is not None:
            old_types = ', '.join(existing_data.get('data_types', []))
            new_types = ', '.join(data_types)
            changes_made.append(f"   📂 Data Types: {old_types or 'None'} → {new_types}")
        if usage_pattern is not None:
            changes_made.append(f"   🔄 Usage Pattern: {existing_data.get('usage_pattern', 'None')} → {usage_pattern}")
        if retention_policy is not None:
            changes_made.append(f"   📅 Retention: {existing_data.get('retention_policy', 'None')} → {retention_policy}")
        if related_indices is not None:
            old_related = ', '.join(existing_data.get('related_indices', []))
            new_related = ', '.join(related_indices)
            changes_made.append(f"   🔗 Related: {old_related or 'None'} → {new_related}")
        if tags is not None:
            old_tags = ', '.join(existing_data.get('tags', []))
            new_tags = ', '.join(tags)
            changes_made.append(f"   🏷️ Tags: {old_tags or 'None'} → {new_tags}")
        
        return (f"✅ Index metadata updated successfully!\n\n" +
               f"📋 **Updated Metadata for '{index_name}'**:\n" +
               (f"🔄 **Changes Made**:\n" + '\n'.join(changes_made) + "\n\n" if changes_made else "") +
               f"📊 **Current Metadata**:\n" +
               f"   📝 Description: {updated_data.get('description', 'No description')}\n" +
               f"   🎯 Purpose: {updated_data.get('purpose', 'No purpose')}\n" +
               f"   📂 Data Types: {', '.join(updated_data.get('data_types', [])) if updated_data.get('data_types') else 'None'}\n" +
               f"   🔄 Usage Pattern: {updated_data.get('usage_pattern', 'Unknown')}\n" +
               f"   📅 Retention: {updated_data.get('retention_policy', 'Not specified')}\n" +
               f"   🔗 Related Indices: {', '.join(updated_data.get('related_indices', [])) if updated_data.get('related_indices') else 'None'}\n" +
               f"   🏷️ Tags: {', '.join(updated_data.get('tags', [])) if updated_data.get('tags') else 'None'}\n" +
               f"   👤 Last Updated By: {updated_by}\n" +
               f"   📅 Last Updated: {update_data['last_updated']}\n\n" +
               f"✅ **Benefits**:\n" +
               f"   • Index documentation stays current and accurate\n" +
               f"   • Team has updated context for index usage\n" +
               f"   • Change history is tracked with timestamps\n" +
               f"   • Governance and compliance are maintained")
        
    except Exception as e:
        error_message = "❌ Failed to update index metadata:\n\n"
        
        error_str = str(e).lower()
        if "connection" in error_str or "refused" in error_str:
            error_message += "🔌 **Connection Error**: Cannot connect to Elasticsearch server\n"
            error_message += f"📍 Check if Elasticsearch is running at the configured address\n"
            error_message += f"💡 Try: Use 'setup_elasticsearch' tool to start Elasticsearch\n\n"
        elif ("not_found" in error_str or "not found" in error_str) and "index" in error_str:
            error_message += f"📁 **Index Error**: Metadata index 'index_metadata' does not exist\n"
            error_message += f"📍 The metadata system has not been initialized\n"
            error_message += f"💡 Try: Use 'create_index_metadata' to set up metadata system\n\n"
        else:
            error_message += f"⚠️ **Unknown Error**: {str(e)}\n\n"
        
        error_message += f"🔍 **Technical Details**: {str(e)}"
        return error_message


# ================================
# TOOL 13: DELETE_INDEX_METADATA
# ================================

@app.tool(
    description="Delete metadata documentation for an Elasticsearch index",
    tags={"elasticsearch", "metadata", "delete", "cleanup"}
)
async def delete_index_metadata(
    index_name: Annotated[str, Field(description="Name of the index to remove metadata for")]
) -> str:
    """Delete metadata documentation for an Elasticsearch index."""
    try:
        es = get_es_client()
        metadata_index = "index_metadata"
        
        # Search for existing metadata
        search_body = {
            "query": {
                "term": {
                    "index_name.keyword": index_name
                }
            },
            "size": 1
        }
        
        existing_result = es.search(index=metadata_index, body=search_body)
        
        if existing_result['hits']['total']['value'] == 0:
            return (f"⚠️ No metadata found for index '{index_name}'!\n\n" +
                   f"📋 **Status**: Index metadata does not exist\n" +
                   f"   ✅ **Good**: No cleanup required for metadata\n" +
                   f"   🔧 **Safe**: You can proceed with 'delete_index' if needed\n" +
                   f"   🔍 **Check**: Use 'list_indices' to see all documented indices\n\n" +
                   f"💡 **This is Normal If**:\n" +
                   f"   • Index was created before metadata system was implemented\n" +
                   f"   • Index was created without using 'create_index_metadata' first\n" +
                   f"   • Metadata was already deleted in a previous cleanup")
        
        # Get existing document details before deletion
        existing_doc = existing_result['hits']['hits'][0]
        existing_id = existing_doc['_id']
        existing_data = existing_doc['_source']
        
        # Delete the metadata document
        result = es.delete(index=metadata_index, id=existing_id)
        
        return (f"✅ Index metadata deleted successfully!\n\n" +
               f"🗑️ **Deleted Metadata for '{index_name}'**:\n" +
               f"   📋 Document ID: {existing_id}\n" +
               f"   📝 Description: {existing_data.get('description', 'No description')}\n" +
               f"   🎯 Purpose: {existing_data.get('purpose', 'No purpose')}\n" +
               f"   📂 Data Types: {', '.join(existing_data.get('data_types', [])) if existing_data.get('data_types') else 'None'}\n" +
               f"   👤 Created By: {existing_data.get('created_by', 'Unknown')}\n" +
               f"   📅 Created: {existing_data.get('created_date', 'Unknown')}\n\n" +
               f"✅ **Cleanup Complete**:\n" +
               f"   🗑️ Metadata documentation removed from registry\n" +
               f"   🔧 You can now safely use 'delete_index' to remove the actual index\n" +
               f"   📊 Use 'list_indices' to verify metadata removal\n\n" +
               f"🎯 **Next Steps**:\n" +
               f"   1. Proceed with 'delete_index {index_name}' to remove the actual index\n" +
               f"   2. Or use 'create_index_metadata' if you want to re-document this index\n" +
               f"   3. Clean up any related indices mentioned in metadata\n\n" +
               f"⚠️ **Important**: This only deleted the documentation, not the actual index")
        
    except Exception as e:
        error_message = "❌ Failed to delete index metadata:\n\n"
        
        error_str = str(e).lower()
        if "connection" in error_str or "refused" in error_str:
            error_message += "🔌 **Connection Error**: Cannot connect to Elasticsearch server\n"
            error_message += f"📍 Check if Elasticsearch is running at the configured address\n"
            error_message += f"💡 Try: Use 'setup_elasticsearch' tool to start Elasticsearch\n\n"
        elif ("not_found" in error_str or "not found" in error_str) and "index" in error_str:
            error_message += f"📁 **Index Error**: Metadata index 'index_metadata' does not exist\n"
            error_message += f"📍 The metadata system has not been initialized\n"
            error_message += f"💡 This means no metadata exists to delete - you can proceed safely\n\n"
        else:
            error_message += f"⚠️ **Unknown Error**: {str(e)}\n\n"
        
        error_message += f"🔍 **Technical Details**: {str(e)}"
        return error_message


# CLI entry point
def cli_main():
    """CLI entry point for Elasticsearch FastMCP server."""
    print("🚀 Starting AgentKnowledgeMCP Elasticsearch FastMCP server...")
    print("🔍 Tools: search, index_document, delete_document, get_document, list_indices, create_index, delete_index, batch_index_directory, validate_document_schema, create_document_template, create_index_metadata, update_index_metadata, delete_index_metadata")
    print("✅ Status: All 13 Elasticsearch tools completed with Index Metadata Management - Ready for production!")

    app.run()

if __name__ == "__main__":
    cli_main()
