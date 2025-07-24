"""
Elasticsearch FastMCP Server - Step by step migration
Tool-by-tool conversion from handlers to FastMCP tools.
File 1/4: Elasticsearch Server
"""
import json
from typing import List, Dict, Any, Optional, Annotated
from datetime import datetime, timedelta
import re

from fastmcp import FastMCP, Context
from pydantic import Field

from src.elasticsearch.elasticsearch_client import get_es_client
from src.elasticsearch.document_schema import (
    validate_document_structure,
    DocumentValidationError,
    create_document_template as create_doc_template_base,
    format_validation_error
)
from src.config.config import load_config

# Create FastMCP app
app = FastMCP(
    name="AgentKnowledgeMCP-Elasticsearch",
    version="1.0.0",
    instructions="Elasticsearch tools for knowledge management"
)

async def _generate_smart_metadata(title: str, content: str, ctx: Context) -> Dict[str, Any]:
    """Generate intelligent tags and key_points using LLM sampling."""
    try:
        # Create prompt for generating metadata and smart content
        prompt = f"""Analyze the following document and provide comprehensive smart metadata and content:

Title: {title}

Content: {content[:2000]}{"..." if len(content) > 2000 else ""}

Please provide:
1. Relevant tags (3-8 tags, lowercase, hyphen-separated)
2. Key points (3-6 important points from the content)
3. Smart summary (2-3 sentences capturing the essence)
4. Enhanced content (improved/structured version if content is brief or unclear)

Respond in JSON format:
{{
  "tags": ["tag1", "tag2", "tag3"],
  "key_points": ["Point 1", "Point 2", "Point 3"],
  "smart_summary": "Brief 2-3 sentence summary of the document",
  "enhanced_content": "Improved/structured content if original is brief, otherwise keep original"
}}

Focus on:
- Technical concepts and technologies mentioned
- Main topics and themes
- Document type and purpose
- Key features or functionalities discussed
- Clear, professional language for summary and content
- Maintain accuracy while improving clarity"""

        # Request LLM analysis with controlled parameters and model preferences
        response = await ctx.sample(
            messages=prompt,
            system_prompt="You are an expert document analyzer and content enhancer. Generate accurate, relevant metadata and improve content quality while maintaining original meaning. Always respond with valid JSON.",
            model_preferences=["claude-3-opus", "claude-3-sonnet", "gpt-4"],  # Prefer reasoning models for analysis
            temperature=0.3,  # Low randomness for consistency
            max_tokens=600   # Increased for smart content generation
        )
        
        # Parse the JSON response
        try:
            metadata = json.loads(response.text.strip())
            
            # Validate and clean the response
            tags = metadata.get("tags", [])
            key_points = metadata.get("key_points", [])
            smart_summary = metadata.get("smart_summary", "")
            enhanced_content = metadata.get("enhanced_content", "")
            
            # Ensure we have reasonable limits and clean data
            tags = [tag.lower().strip() for tag in tags[:8] if tag and isinstance(tag, str)]
            key_points = [point.strip() for point in key_points[:6] if point and isinstance(point, str)]
            
            # Clean and validate smart content
            smart_summary = smart_summary.strip() if isinstance(smart_summary, str) else ""
            enhanced_content = enhanced_content.strip() if isinstance(enhanced_content, str) else ""
            
            return {
                "tags": tags,
                "key_points": key_points,
                "smart_summary": smart_summary,
                "enhanced_content": enhanced_content
            }
            
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            await ctx.warning("LLM response was not valid JSON, using fallback metadata generation")
            return _generate_fallback_metadata(title, content)
            
    except Exception as e:
        # Fallback for any sampling errors
        await ctx.warning(f"LLM sampling failed ({str(e)}), using fallback metadata generation")
        return _generate_fallback_metadata(title, content)

def _generate_fallback_metadata(title: str, content: str) -> Dict[str, Any]:
    """Generate basic metadata when LLM sampling is not available."""
    # Basic tags based on title and content analysis
    title_lower = title.lower()
    content_lower = content.lower()[:1000]  # First 1000 chars for analysis
    
    tags = ["document"]
    
    # Add file type tags
    if any(word in title_lower for word in ["readme", "documentation", "docs"]):
        tags.append("documentation")
    if any(word in title_lower for word in ["config", "configuration", "settings"]):
        tags.append("configuration")
    if any(word in title_lower for word in ["test", "testing", "spec"]):
        tags.append("testing")
    if any(word in content_lower for word in ["python", "def ", "class ", "import "]):
        tags.append("python")
    if any(word in content_lower for word in ["javascript", "function", "const ", "let "]):
        tags.append("javascript")
    if any(word in content_lower for word in ["api", "endpoint", "request", "response"]):
        tags.append("api")
    
    # Basic key points
    key_points = [
        f"Document title: {title}",
        f"Content length: {len(content)} characters"
    ]
    
    # Add content-based points
    if "implementation" in content_lower:
        key_points.append("Contains implementation details")
    if "example" in content_lower or "demo" in content_lower:
        key_points.append("Includes examples or demonstrations")
    if "error" in content_lower or "exception" in content_lower:
        key_points.append("Discusses error handling")
    
    return {
        "tags": tags[:6],  # Limit to 6 tags
        "key_points": key_points[:4],  # Limit to 4 points
        "smart_summary": f"Fallback document: {title}",
        "enhanced_content": content[:500] + "..." if len(content) > 500 else content
    }

def _parse_time_parameters(date_from: Optional[str] = None, date_to: Optional[str] = None,
                          time_period: Optional[str] = None) -> Dict[str, Any]:
    """Parse time-based search parameters and return Elasticsearch date range filter."""

    def parse_relative_date(date_str: str) -> datetime:
        """Parse relative date strings like '7d', '1w', '1m' to datetime."""
        if not date_str:
            return None

        match = re.match(r'(\d+)([dwmy])', date_str.lower())
        if match:
            amount, unit = match.groups()
            amount = int(amount)

            if unit == 'd':
                return datetime.now() - timedelta(days=amount)
            elif unit == 'w':
                return datetime.now() - timedelta(weeks=amount)
            elif unit == 'm':
                return datetime.now() - timedelta(days=amount * 30)
            elif unit == 'y':
                return datetime.now() - timedelta(days=amount * 365)

        return None

    def parse_date_string(date_str: str) -> str:
        """Parse various date formats to Elasticsearch compatible format."""
        if not date_str:
            return None

        if date_str.lower() == 'now':
            return 'now'

        # Try relative dates first
        relative_date = parse_relative_date(date_str)
        if relative_date:
            return relative_date.isoformat()

        # Try parsing standard formats
        formats = [
            '%Y-%m-%d',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ'
        ]

        for fmt in formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.isoformat()
            except ValueError:
                continue

        return None

    # Handle time_period shortcuts
    if time_period:
        now = datetime.now()
        if time_period == 'today':
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
            return {
                "range": {
                    "last_modified": {
                        "gte": start_of_day.isoformat(),
                        "lte": "now"
                    }
                }
            }
        elif time_period == 'yesterday':
            yesterday = now - timedelta(days=1)
            start_of_yesterday = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_yesterday = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
            return {
                "range": {
                    "last_modified": {
                        "gte": start_of_yesterday.isoformat(),
                        "lte": end_of_yesterday.isoformat()
                    }
                }
            }
        elif time_period == 'week':
            week_ago = now - timedelta(weeks=1)
            return {
                "range": {
                    "last_modified": {
                        "gte": week_ago.isoformat(),
                        "lte": "now"
                    }
                }
            }
        elif time_period == 'month':
            month_ago = now - timedelta(days=30)
            return {
                "range": {
                    "last_modified": {
                        "gte": month_ago.isoformat(),
                        "lte": "now"
                    }
                }
            }
        elif time_period == 'year':
            year_ago = now - timedelta(days=365)
            return {
                "range": {
                    "last_modified": {
                        "gte": year_ago.isoformat(),
                        "lte": "now"
                    }
                }
            }

    # Handle explicit date range
    if date_from or date_to:
        range_filter = {"range": {"last_modified": {}}}

        if date_from:
            parsed_from = parse_date_string(date_from)
            if parsed_from:
                range_filter["range"]["last_modified"]["gte"] = parsed_from

        if date_to:
            parsed_to = parse_date_string(date_to)
            if parsed_to:
                range_filter["range"]["last_modified"]["lte"] = parsed_to

        if range_filter["range"]["last_modified"]:
            return range_filter

    return None


def _analyze_search_results_for_reorganization(results: List[Dict], query_text: str, total_results: int) -> str:
    """Analyze search results and provide specific reorganization suggestions."""
    if total_results <= 15:
        return ""

    # Extract topics and themes from search results
    topics = set()
    sources = set()
    priorities = {"high": 0, "medium": 0, "low": 0}
    dates = []

    for result in results[:10]:  # Analyze first 10 results
        source_data = result.get("source", {})

        # Extract tags as topics
        tags = source_data.get("tags", [])
        topics.update(tags)

        # Extract source types
        source_type = source_data.get("source_type", "unknown")
        sources.add(source_type)

        # Count priorities
        priority = source_data.get("priority", "medium")
        priorities[priority] = priorities.get(priority, 0) + 1

        # Extract dates for timeline analysis
        last_modified = source_data.get("last_modified", "")
        if last_modified:
            dates.append(last_modified)

    # Generate reorganization suggestions
    suggestion = f"\n\n🔍 **Knowledge Base Analysis for '{query_text}'** ({total_results} documents):\n\n"

    # Topic analysis
    if topics:
        suggestion += f"📋 **Topics Found**: {', '.join(sorted(list(topics))[:8])}\n"
        suggestion += f"💡 **Reorganization Suggestion**: Group documents by these topics\n\n"

    # Source type analysis
    if sources:
        suggestion += f"📁 **Content Types**: {', '.join(sorted(sources))}\n"
        suggestion += f"💡 **Organization Tip**: Separate by content type for better structure\n\n"

    # Priority distribution
    total_priority_docs = sum(priorities.values())
    if total_priority_docs > 0:
        high_pct = (priorities["high"] / total_priority_docs) * 100
        suggestion += f"⭐ **Priority Distribution**: {priorities['high']} high, {priorities['medium']} medium, {priorities['low']} low\n"
        if priorities["low"] > 5:
            suggestion += f"💡 **Cleanup Suggestion**: Consider archiving {priorities['low']} low-priority documents\n\n"

    # User collaboration template
    suggestion += f"🤝 **Ask User These Questions**:\n"
    suggestion += f"   1. 'I found {total_results} documents about {query_text}. Would you like to organize them better?'\n"
    suggestion += f"   2. 'Should we group them by: {', '.join(sorted(list(topics))[:3]) if topics else 'topic areas'}?'\n"
    suggestion += f"   3. 'Which documents can we merge or archive to reduce redundancy?'\n"
    suggestion += f"   4. 'Do you want to keep all {priorities.get('low', 0)} low-priority items?'\n\n"

    suggestion += f"✅ **Reorganization Goals**:\n"
    suggestion += f"   • Reduce from {total_results} to ~{max(5, total_results // 3)} well-organized documents\n"
    suggestion += f"   • Create comprehensive topic-based documents\n"
    suggestion += f"   • Archive or delete outdated/redundant content\n"
    suggestion += f"   • Improve searchability and knowledge quality"

    return suggestion


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
        time_filter = _parse_time_parameters(date_from, date_to, time_period)

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
        reorganization_analysis = _analyze_search_results_for_reorganization(formatted_results, query, total_results)

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

                else:
                    # For non-knowledge base documents, still validate with strict mode if enabled
                    validated_doc = validate_document_structure(document, base_directory, is_knowledge_doc=False)
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

        return f"✅ Available indices:\n\n{json.dumps(indices_info, indent=2, ensure_ascii=False)}"

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
        # Get base directory from config
        config = load_config()
        base_directory = config.get("security", {}).get("allowed_base_directory")

        validated_doc = validate_document_structure(document, base_directory)

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
        from src.utils.security import validate_path, SecurityError
        
        # Validate directory path
        try:
            validated_dir = validate_path(directory_path)
        except SecurityError as e:
            return f"❌ Security error: {str(e)}"
        
        if not validated_dir.exists():
            return f"❌ Directory not found: {directory_path}\n💡 Check the directory path spelling and location"
        
        if not validated_dir.is_dir():
            return f"❌ Path is not a directory: {directory_path}\n💡 Provide a directory path, not a file path"
        
        # Get Elasticsearch client
        es = get_es_client()
        
        # Find all matching files
        if recursive:
            files = list(validated_dir.rglob(file_pattern))
        else:
            files = list(validated_dir.glob(file_pattern))
        
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
                # Search for existing documents by file names
                search_body = {
                    "query": {"match_all": {}},
                    "size": 10000,  # Get many docs to check
                    "_source": ["file_name", "file_path"]
                }
                existing_result = es.search(index=index, body=search_body)
                for hit in existing_result['hits']['hits']:
                    source = hit.get('_source', {})
                    if 'file_name' in source:
                        existing_docs.add(source['file_name'])
                    if 'file_path' in source:
                        existing_docs.add(os.path.basename(source['file_path']))
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
                
                # Skip if file already exists in index
                if skip_existing and file_name in existing_docs:
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
                relative_path = file_path.relative_to(validated_dir)
                doc_id = f"{file_path.stem}_{hash(str(relative_path)) % 100000}"  # Create unique ID
                
                title = file_path.stem.replace('_', ' ').replace('-', ' ').title()
                
                # Initialize basic tags and key points
                base_tags = [
                    "batch-indexed",
                    file_path.suffix[1:] if file_path.suffix else "no-extension",
                    validated_dir.name
                ]
                
                base_key_points = [
                    f"File size: {file_path.stat().st_size} bytes",
                    f"File type: {file_path.suffix or 'no extension'}",
                    f"Directory: {file_path.parent.name}"
                ]
                
                final_tags = base_tags.copy()
                final_key_points = base_key_points.copy()
                final_summary = f"Document from {file_name}"
                
                # Use AI enhancement if requested and context is available
                if use_ai_enhancement and ctx and content.strip():
                    try:
                        await ctx.info(f"🤖 Generating AI metadata and smart content for: {file_name}")
                        ai_metadata = await _generate_smart_metadata(title, content, ctx)
                        
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
                    "file_path": str(file_path),
                    "file_name": file_name,
                    "directory": str(file_path.parent),
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
                        config = load_config()
                        base_directory = config.get("security", {}).get("allowed_base_directory")
                        validated_doc = validate_document_structure(document, base_directory)
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
            error_message += f"💡 Try: Check directory permissions or change allowed_base_directory\n\n"
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
    file_path: Annotated[str, Field(description="File path where the document content will be stored")],
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
        # Get base directory from config
        config = load_config()
        base_directory = config.get("security", {}).get("allowed_base_directory")

        # Initialize metadata
        final_tags = list(tags)  # Copy manual tags
        final_key_points = list(key_points)  # Copy manual key points
        
        # Use AI enhancement if requested and content is provided
        if use_ai_enhancement and content.strip() and ctx:
            try:
                await ctx.info("🤖 Generating intelligent metadata and smart content using AI...")
                ai_metadata = await _generate_smart_metadata(title, content, ctx)
                
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
            file_path=file_path,
            priority=priority,
            source_type=source_type,
            tags=final_tags,
            summary=summary,
            key_points=final_key_points,
            related=related,
            base_directory=base_directory
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


# CLI entry point
def cli_main():
    """CLI entry point for Elasticsearch FastMCP server."""
    print("🚀 Starting AgentKnowledgeMCP Elasticsearch FastMCP server...")
    print("🔍 Tools: search, index_document, delete_document, get_document, list_indices, create_index, delete_index, batch_index_directory, validate_document_schema, create_document_template")
    print("✅ Status: All 10 Elasticsearch tools completed - Ready for production!")

    app.run()

if __name__ == "__main__":
    cli_main()
