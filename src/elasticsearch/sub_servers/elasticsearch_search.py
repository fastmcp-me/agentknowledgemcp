"""
Elasticsearch Search FastMCP Server
Search operations extracted from main elasticsearch server.
Handles advanced document search operations.
"""
import json
from typing import List, Dict, Any, Optional, Annotated
from datetime import datetime

from fastmcp import FastMCP, Context
from pydantic import Field

from ..elasticsearch_client import get_es_client
from ..elasticsearch_helper import (
    parse_time_parameters,
    analyze_search_results_for_reorganization
)
from ...config.config import load_config

# Create FastMCP app
app = FastMCP(
    name="AgentKnowledgeMCP-Search",
    version="1.0.0",
    instructions="Elasticsearch search tools for advanced document queries"
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
                                    "fields": ["title^3", "summary^2", "content", "tags^2", "features^2",
                                               "tech_stack^2"]
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
                    f"   • Try fuzzy matching or wildcard searches" + time_suggestions)

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
                                  f"\n")

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
                                  f"\n")

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
            error_message += f"💡 Try: Use 'setup_elasticsearch' tool to start Elasticsearch\n"
        elif (
                "index" in error_str and "not found" in error_str) or "index_not_found_exception" in error_str or "no such index" in error_str:
            error_message += f"📁 **Index Error**: Index '{index}' does not exist\n"
            error_message += f"📍 The search index has not been created yet\n"
            error_message += f"💡 **Suggestions for agents**:\n"
            error_message += f"   1. Use 'list_indices' tool to see all available indices\n"
            error_message += f"   2. Check which indices contain your target data\n"
            error_message += f"   3. Use the correct index name from the list\n"
            error_message += f"   4. If no suitable index exists, create one with 'create_index' tool\n"
        elif "timeout" in error_str:
            error_message += "⏱️ **Timeout Error**: Search query timed out\n"
            error_message += f"📍 Query may be too complex or index too large\n"
            error_message += f"💡 Try: Simplify query or reduce search size\n"
        elif "parse" in error_str or "query" in error_str:
            error_message += f"🔍 **Query Error**: Invalid search query format\n"
            error_message += f"📍 Search query syntax is not valid\n"
            error_message += f"💡 Try: Use simpler search terms\n"
        else:
            error_message += f"⚠️ **Unknown Error**: {str(e)}\n\n"

        error_message += f"🔍 **Technical Details**: {str(e)}"

        return error_message
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
        max_score = hits.get('max_score') or 0
        
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
        analysis = analyze_search_results_for_reorganization(hits['hits'], query, total_hits)
        if analysis:
            result_message += analysis
        
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
# CLI ENTRY POINT
# ================================

def cli_main():
    """CLI entry point for Elasticsearch Search FastMCP server."""
    print("🚀 Starting AgentKnowledgeMCP Elasticsearch Search FastMCP server...")
    print("🔍 Tools: search")
    print("🎯 Purpose: Advanced document search operations")
    print("✅ Status: 1 Search tool completed - Ready for production!")

    app.run()

    app.run()

if __name__ == "__main__":
    cli_main()
