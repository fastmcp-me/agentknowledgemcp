"""
Elasticsearch Search FastMCP Server
Search and validation operations extracted from main elasticsearch server.
Handles document search and schema validation operations.
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
    format_validation_error
)
from src.elasticsearch.elasticsearch_helper import (
    parse_time_parameters,
    analyze_search_results_for_reorganization
)
from src.config.config import load_config

# Create FastMCP app
app = FastMCP(
    name="AgentKnowledgeMCP-Search",
    version="1.0.0",
    instructions="Elasticsearch search and validation tools"
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
    """Search documents in Elasticsearch with advanced filtering and pagination."""
    try:
        es = get_es_client()
        
        # Build the search query
        search_body = {
            "query": {
                "bool": {
                    "must": [],
                    "filter": []
                }
            },
            "size": size,
            "sort": []
        }
        
        # Add text search
        if query.strip():
            if query == "*" or query == "":
                # Match all documents
                search_body["query"]["bool"]["must"].append({"match_all": {}})
            else:
                # Multi-field search with boosting
                search_body["query"]["bool"]["must"].append({
                    "multi_match": {
                        "query": query,
                        "fields": [
                            "title^3",      # Boost title matches
                            "summary^2",    # Boost summary matches  
                            "content",      # Normal content matches
                            "tags^2",       # Boost tag matches
                            "key_points"    # Include key points
                        ],
                        "type": "best_fields",
                        "fuzziness": "AUTO"
                    }
                })
        else:
            search_body["query"]["bool"]["must"].append({"match_all": {}})
        
        # Add time filtering
        time_filter = parse_time_parameters(date_from, date_to, time_period)
        if time_filter:
            search_body["query"]["bool"]["filter"].append(time_filter)
        
        # Add sorting
        if sort_by_time:
            time_sort = {"last_modified": {"order": sort_by_time, "missing": "_last"}}
            search_body["sort"].append(time_sort)
        
        # Add score sorting for relevance
        search_body["sort"].append("_score")
        
        # Specify fields to return
        if fields:
            search_body["_source"] = fields
        
        # Add highlighting for better results presentation
        search_body["highlight"] = {
            "fields": {
                "title": {},
                "content": {"fragment_size": 150, "number_of_fragments": 3},
                "summary": {},
                "key_points": {}
            }
        }
        
        # Execute search
        response = es.search(index=index, body=search_body)
        
        hits = response['hits']
        total_hits = hits['total']['value']
        max_score = hits.get('max_score', 0)
        
        if total_hits == 0:
            return (f"🔍 **No Results Found**\n\n" +
                   f"📝 **Query**: \"{query}\"\n" +
                   f"📁 **Index**: {index}\n" +
                   f"📊 **Total**: 0 documents found\n\n" +
                   f"💡 **Suggestions**:\n" +
                   f"   • Try broader search terms\n" +
                   f"   • Check spelling and try synonyms\n" +
                   f"   • Use wildcard (*) to search all documents\n" +
                   f"   • Verify the index contains documents\n" +
                   f"   • Try different time filters if used")
        
        # Format results
        result_message = f"🔍 **Search Results**\n\n"
        result_message += f"📝 **Query**: \"{query}\"\n"
        result_message += f"📁 **Index**: {index}\n" 
        result_message += f"📊 **Found**: {total_hits:,} documents (showing top {len(hits['hits'])})\n"
        result_message += f"⭐ **Max Score**: {max_score:.3f}\n"
        
        if time_filter:
            result_message += f"📅 **Time Filter**: Applied\n"
        
        result_message += f"\n📋 **Results**:\n\n"
        
        for i, hit in enumerate(hits['hits'], 1):
            doc = hit['_source']
            score = hit['_score']
            doc_id = hit['_id']
            
            result_message += f"**{i}. {doc.get('title', 'Untitled Document')}** (Score: {score:.3f})\n"
            result_message += f"   🆔 **ID**: {doc_id}\n"
            
            # Show summary or content preview
            if 'summary' in doc and doc['summary']:
                result_message += f"   📄 **Summary**: {doc['summary'][:200]}{'...' if len(doc['summary']) > 200 else ''}\n"
            elif 'content' in doc and doc['content']:
                content_preview = doc['content'][:150].replace('\n', ' ')
                result_message += f"   📝 **Preview**: {content_preview}{'...' if len(doc['content']) > 150 else ''}\n"
            
            # Show highlights if available
            if 'highlight' in hit:
                highlights = hit['highlight']
                for field, highlight_fragments in highlights.items():
                    if highlight_fragments:
                        result_message += f"   ✨ **{field.title()}**: {highlight_fragments[0]}\n"
            
            # Show key metadata
            if 'tags' in doc and doc['tags']:
                tags_display = doc['tags'][:5] if isinstance(doc['tags'], list) else [doc['tags']]
                result_message += f"   🏷️ **Tags**: {', '.join(tags_display)}\n"
            
            if 'last_modified' in doc:
                result_message += f"   📅 **Modified**: {doc['last_modified']}\n"
            
            result_message += "\n"
        
        # Add pagination info
        if total_hits > size:
            result_message += f"📄 **Pagination**: Showing {size} of {total_hits:,} results\n"
            result_message += f"💡 **More Results**: Increase 'size' parameter to see more\n\n"
        
        # Add search insights
        analysis = analyze_search_results_for_reorganization(hits['hits'])
        if analysis:
            result_message += f"🔍 **Search Insights**:\n"
            if analysis.get('common_tags'):
                result_message += f"   🏷️ **Common Tags**: {', '.join(analysis['common_tags'][:5])}\n"
            if analysis.get('date_range'):
                result_message += f"   📅 **Date Range**: {analysis['date_range']}\n"
            if analysis.get('content_types'):
                result_message += f"   📁 **Content Types**: {', '.join(analysis['content_types'])}\n"
        
        result_message += f"\n💡 **Search Tips**:\n"
        result_message += f"   • Use quotes for exact phrases: \"specific phrase\"\n"
        result_message += f"   • Use wildcards for partial matches: part*\n"
        result_message += f"   • Combine terms with AND/OR: term1 AND term2\n"
        result_message += f"   • Add time filters for recent documents\n"
        result_message += f"   • Increase size parameter for more results"
        
        return result_message
        
    except Exception as e:
        error_message = "❌ Failed to search documents:\n\n"
        
        error_str = str(e).lower()
        if "connection" in error_str or "refused" in error_str:
            error_message += "🔌 **Connection Error**: Cannot connect to Elasticsearch server\n"
            error_message += f"📍 Check if Elasticsearch is running at the configured address\n"
            error_message += f"💡 Try: Use 'setup_elasticsearch' tool to start Elasticsearch\n\n"
        elif "index_not_found" in error_str or "no such index" in error_str:
            error_message += f"📁 **Index Error**: Index '{index}' does not exist\n"
            error_message += f"📍 Check the index name or create the index first\n"
            error_message += f"💡 Try: Use 'list_indices' to see available indices\n\n"
        elif "parsing_exception" in error_str or "query_shard_exception" in error_str:
            error_message += f"🔍 **Query Error**: Invalid search query syntax\n"
            error_message += f"📍 Check your query format and special characters\n"
            error_message += f"💡 Try: Simplify the query or use basic text search\n\n"
        else:
            error_message += f"⚠️ **Unknown Error**: {str(e)}\n\n"

        error_message += f"🔍 **Technical Details**: {str(e)}"

        return error_message


# ================================
# TOOL 2: VALIDATE_DOCUMENT_SCHEMA
# ================================

@app.tool(
    description="Validate document structure against knowledge base schema and provide formatting guidance",
    tags={"elasticsearch", "validation", "document", "schema"}
)
async def validate_document_schema(
    document: Annotated[Dict[str, Any], Field(description="Document object to validate against knowledge base schema format")]
) -> str:
    """Validate document structure against knowledge base schema."""
    try:
        # Perform validation
        validate_document_structure(document)
        
        # If we get here, validation passed
        result_message = "✅ **Document Validation Passed!**\n\n"
        result_message += "📋 **Document Structure**: Valid knowledge base format\n"
        
        # Show document summary
        if 'title' in document:
            result_message += f"📝 **Title**: {document['title']}\n"
        if 'summary' in document:
            result_message += f"📄 **Summary**: {document['summary'][:100]}{'...' if len(document.get('summary', '')) > 100 else ''}\n"
        
        # Show structure details
        result_message += f"\n📊 **Structure Analysis**:\n"
        result_message += f"   📝 **Fields Found**: {len(document)} total fields\n"
        
        # Core fields check
        core_fields = ['title', 'content', 'summary', 'tags', 'priority']
        found_core = [field for field in core_fields if field in document]
        result_message += f"   ✅ **Core Fields**: {len(found_core)}/5 ({', '.join(found_core)})\n"
        
        # Optional fields check  
        optional_fields = ['related', 'key_points', 'last_modified', 'source_type']
        found_optional = [field for field in optional_fields if field in document]
        if found_optional:
            result_message += f"   📋 **Optional Fields**: {', '.join(found_optional)}\n"
        
        # Content analysis
        if 'content' in document:
            content_length = len(str(document['content']))
            result_message += f"   📄 **Content Size**: {content_length:,} characters\n"
            
        if 'tags' in document:
            tag_count = len(document['tags']) if isinstance(document['tags'], list) else 1
            result_message += f"   🏷️ **Tags**: {tag_count} tags\n"
        
        result_message += f"\n🎯 **Next Steps**:\n"
        result_message += f"   📝 **Ready to Index**: Use 'index_document' to store this document\n"
        result_message += f"   🔍 **Searchable**: Document will be fully searchable after indexing\n"
        result_message += f"   📊 **Governance**: Consider adding metadata for better organization\n"
        
        result_message += f"\n💡 **Quality Tips**:\n"
        result_message += f"   ✅ Use descriptive titles for better searchability\n"
        result_message += f"   ✅ Add relevant tags for categorization\n"
        result_message += f"   ✅ Include summary for quick understanding\n"
        result_message += f"   ✅ Set appropriate priority level"
        
        return result_message
        
    except DocumentValidationError as e:
        return format_validation_error(e)
    except Exception as e:
        return f"❌ Validation error: {str(e)}"


# ================================
# CLI ENTRY POINT
# ================================

def cli_main():
    """CLI entry point for Elasticsearch Search FastMCP server."""
    print("🚀 Starting AgentKnowledgeMCP Elasticsearch Search FastMCP server...")
    print("🔍 Tools: search, validate_document_schema")
    print("🎯 Purpose: Document search and schema validation operations")
    print("✅ Status: 2 Search & validation tools completed - Ready for production!")

    app.run()

if __name__ == "__main__":
    cli_main()
