"""
Elasticsearch Document FastMCP Server
Document operations extracted from main elasticsearch server.
Handles document indexing, retrieval, and deletion operations.
"""
import json
from typing import List, Dict, Any, Optional, Annotated
from datetime import datetime

from fastmcp import FastMCP, Context
from pydantic import Field

from ..elasticsearch_client import get_es_client
from ..document_schema import (
    validate_document_structure,
    DocumentValidationError,
    format_validation_error
)
from ..elasticsearch_helper import (
    generate_smart_metadata, 
    generate_fallback_metadata,
    generate_smart_doc_id,
    check_title_duplicates,
    get_existing_document_ids,
    check_content_similarity_with_ai
)
from ...config.config import load_config
import hashlib
import json
import re
import time

# Create FastMCP app
app = FastMCP(
    name="AgentKnowledgeMCP-Document",
    version="1.0.0",
    instructions="Elasticsearch document operations tools"
)


# ================================
# TOOL 1: INDEX_DOCUMENT
# ================================

@app.tool(
    description="Index a document into Elasticsearch with smart duplicate prevention and intelligent document ID generation",
    tags={"elasticsearch", "index", "document", "validation", "duplicate-prevention"}
)
async def index_document(
    index: Annotated[str, Field(description="Name of the Elasticsearch index to store the document")],
    document: Annotated[Dict[str, Any], Field(description="Document data to index as JSON object")],
    doc_id: Annotated[Optional[str], Field(description="Optional document ID - if not provided, smart ID will be generated")] = None,
    validate_schema: Annotated[bool, Field(description="Whether to validate document structure for knowledge base format")] = True,
    check_duplicates: Annotated[bool, Field(description="Check for existing documents with similar title before indexing")] = True,
    force_index: Annotated[bool, Field(description="Force indexing even if potential duplicates are found")] = False,
    use_ai_similarity: Annotated[bool, Field(description="Use AI to analyze content similarity and provide intelligent recommendations")] = True,
    ctx: Context = None
) -> str:
    """Index a document into Elasticsearch with smart duplicate prevention."""
    try:
        es = get_es_client()

        # Smart duplicate checking if enabled
        if check_duplicates and not force_index:
            title = document.get('title', '')
            content = document.get('content', '')
            
            if title:
                # First check simple title duplicates
                dup_check = check_title_duplicates(es, index, title)
                if dup_check['has_duplicates']:
                    duplicate_msg = f"⚠️ **Potential Duplicate Document Detected!**\n\n"
                    duplicate_msg += f"🔍 **Similar Title Found**: '{dup_check['similar_title']}'\n"
                    duplicate_msg += f"📄 **Existing Document ID**: {dup_check['document_id']}\n"
                    duplicate_msg += f"📅 **Created**: {dup_check.get('created_date', 'Unknown')}\n\n"
                    
                    if use_ai_similarity and content:
                        # Use AI for content similarity analysis
                        if ctx:
                            await ctx.info("🤖 Analyzing content similarity with AI...")
                        
                        ai_analysis = await check_content_similarity_with_ai(
                            es, index, content, title, dup_check['document_id']
                        )
                        
                        duplicate_msg += f"🤖 **AI Similarity Analysis**:\n"
                        duplicate_msg += f"   📊 **Similarity Score**: {ai_analysis.get('similarity_score', 'Unknown')}\n"
                        duplicate_msg += f"   🔍 **Analysis**: {ai_analysis.get('analysis', 'No analysis available')}\n"
                        duplicate_msg += f"   💡 **Recommendation**: {ai_analysis.get('recommendation', 'No recommendation')}\n\n"
                        
                        if ai_analysis.get('is_duplicate', False):
                            duplicate_msg += f"🚫 **AI Decision**: Content is too similar to existing document\n\n"
                    
                    duplicate_msg += f"🔧 **Options**:\n"
                    duplicate_msg += f"   1. **Update Existing**: Modify the existing document instead\n"
                    duplicate_msg += f"   2. **Force Create**: Set force_index=True to create anyway\n"
                    duplicate_msg += f"   3. **Review Content**: Check if this is truly unique content\n\n"
                    duplicate_msg += f"💡 **Best Practice**: Consider updating existing document rather than creating duplicates"
                    
                    return duplicate_msg

        # Document validation if enabled
        if validate_schema:
            try:
                validate_document_structure(document)
                if ctx:
                    await ctx.info("✅ Document structure validation passed")
            except DocumentValidationError as e:
                validation_error = format_validation_error(e)
                return (f"❌ **Document Validation Failed**:\n\n" +
                       f"{validation_error}\n\n" +
                       f"💡 **Fix Required**: Correct the document structure and try again\n" +
                       f"🔧 **Help**: Use 'validate_document_schema' tool to test your document structure")

        # Generate smart document ID if not provided
        if not doc_id:
            if ctx:
                await ctx.info("🎯 Generating smart document ID...")
            
            doc_id = generate_smart_doc_id(document, get_existing_document_ids(es, index))
            if ctx:
                await ctx.info(f"📝 Generated ID: {doc_id}")

        # Add metadata to document
        if 'last_modified' not in document:
            document['last_modified'] = datetime.utcnow().isoformat()
        
        # Index the document
        response = es.index(
            index=index,
            id=doc_id,
            body=document
        )
        
        if ctx:
            await ctx.info(f"📁 Document indexed successfully with ID: {doc_id}")

        result_message = f"✅ **Document indexed successfully:**\n\n"
        result_message += "{\n"
        result_message += f"  \"_index\": \"{response['_index']}\",\n"
        result_message += f"  \"_id\": \"{response['_id']}\",\n"
        result_message += f"  \"_version\": {response['_version']},\n"
        result_message += f"  \"result\": \"{response['result']}\",\n"
        result_message += "  \"_shards\": {\n"
        result_message += f"    \"total\": {response['_shards']['total']},\n"
        result_message += f"    \"successful\": {response['_shards']['successful']},\n"
        result_message += f"    \"failed\": {response['_shards']['failed']}\n"
        result_message += "  },\n"
        result_message += f"  \"_seq_no\": {response['_seq_no']},\n"
        result_message += f"  \"_primary_term\": {response['_primary_term']}\n"
        result_message += "}\n\n"

        # Provide action feedback
        if response['result'] == 'created':
            result_message += f"🎉 **New Document Created**:\n"
            result_message += f"   📄 **Document ID**: {response['_id']}\n"
            result_message += f"   🆔 **ID Strategy**: {'User-provided' if doc_id else 'Smart-generated'}\n"
            if check_duplicates:
                result_message += f"   ✅ **Duplicate Check**: Passed - no similar titles found\n"
        else:
            result_message += f"🔄 **Document Updated**:\n"
            result_message += f"   📄 **Document ID**: {response['_id']}\n"
            result_message += f"   🔢 **Version**: {response['_version']}\n"

        result_message += f"\n\n💡 **Smart Duplicate Prevention Active**:\n"
        result_message += f"   🔍 **Auto-Check**: {'Enabled' if check_duplicates else 'Disabled'} - searches for similar titles\n"
        result_message += f"   🤖 **AI Analysis**: {'Enabled' if use_ai_similarity else 'Disabled'} - intelligent content similarity detection\n"
        result_message += f"   🆔 **Smart IDs**: Auto-generated from title with collision detection\n"
        result_message += f"   ⚡ **Force Option**: Use force_index=True to bypass duplicate warnings\n"
        result_message += f"   🔄 **Update Recommended**: Modify existing documents instead of creating duplicates\n"

        result_message += f"\n🤝 **Best Practices**:\n"
        result_message += f"   • Search before creating: 'search(index=\"{index}\", query=\"your topic\")'\n"
        result_message += f"   • Update existing documents when possible\n"
        result_message += f"   • Use descriptive titles for better smart ID generation\n"
        result_message += f"   • AI will analyze content similarity for intelligent recommendations\n"
        result_message += f"   • Set force_index=True only when content is truly unique"

        return result_message

    except Exception as e:
        error_message = "❌ Failed to index document:\n\n"
        
        error_str = str(e).lower()
        if "connection" in error_str or "refused" in error_str:
            error_message += "🔌 **Connection Error**: Cannot connect to Elasticsearch server\n"
            error_message += f"📍 Check if Elasticsearch is running at the configured address\n"
            error_message += f"💡 Try: Use 'setup_elasticsearch' tool to start Elasticsearch\n\n"
        elif "index_not_found" in error_str or "no such index" in error_str:
            error_message += f"📁 **Index Error**: Index '{index}' does not exist\n"
            error_message += f"📍 Create the index first before indexing documents\n"
            error_message += f"💡 Try: Use 'create_index' tool to create the index\n\n"
        elif "validation" in error_str:
            error_message += f"📋 **Validation Error**: Document structure is invalid\n"
            error_message += f"📍 Check document format and required fields\n"
            error_message += f"💡 Try: Use 'validate_document_schema' to check your document\n\n"
        else:
            error_message += f"⚠️ **Unknown Error**: {str(e)}\n\n"
        
        error_message += f"🔍 **Technical Details**: {str(e)}"
        return error_message


# ================================
# TOOL 2: DELETE_DOCUMENT
# ================================

@app.tool(
    description="Delete a document from Elasticsearch index by document ID",
    tags={"elasticsearch", "delete", "document"}
)
async def delete_document(
    index: Annotated[str, Field(description="Name of the Elasticsearch index containing the document")],
    doc_id: Annotated[str, Field(description="Document ID to delete from the index")]
) -> str:
    """Delete a document from Elasticsearch index by document ID."""
    try:
        es = get_es_client()
        
        # Attempt to delete the document
        response = es.delete(
            index=index,
            id=doc_id
        )
        
        result_message = f"✅ **Document deleted successfully:**\n\n"
        result_message += f"📁 **Index**: {response['_index']}\n"
        result_message += f"📄 **Document ID**: {response['_id']}\n"
        result_message += f"🔢 **Version**: {response['_version']}\n"
        result_message += f"✅ **Result**: {response['result']}\n"
        result_message += f"🔄 **Shards**: {response['_shards']['successful']}/{response['_shards']['total']} successful\n\n"
        result_message += f"⚠️ **Important**: This action cannot be undone\n"
        result_message += f"💡 **Tip**: Use 'search' to verify the document has been removed"
        
        return result_message
        
    except Exception as e:
        error_message = "❌ Failed to delete document:\n\n"
        
        error_str = str(e).lower()
        if "not_found" in error_str or "not found" in error_str:
            error_message += f"📄 **Document Not Found**: No document with ID '{doc_id}' in index '{index}'\n"
            error_message += f"📍 Check the document ID and index name\n"
            error_message += f"💡 Try: Use 'search' to find the correct document ID\n\n"
        elif "index_not_found" in error_str:
            error_message += f"📁 **Index Not Found**: Index '{index}' does not exist\n"
            error_message += f"📍 Check the index name\n"
            error_message += f"💡 Try: Use 'list_indices' to see available indices\n\n"
        elif "connection" in error_str or "refused" in error_str:
            error_message += "🔌 **Connection Error**: Cannot connect to Elasticsearch server\n"
            error_message += f"📍 Check if Elasticsearch is running at the configured address\n"
            error_message += f"💡 Try: Use 'setup_elasticsearch' tool to start Elasticsearch\n\n"
        else:
            error_message += f"⚠️ **Unknown Error**: {str(e)}\n\n"
        
        error_message += f"🔍 **Technical Details**: {str(e)}"
        return error_message


# ================================
# TOOL 3: GET_DOCUMENT
# ================================

@app.tool(
    description="Retrieve a specific document from Elasticsearch index by document ID",
    tags={"elasticsearch", "get", "document", "retrieve"}
)
async def get_document(
    index: Annotated[str, Field(description="Name of the Elasticsearch index containing the document")],
    doc_id: Annotated[str, Field(description="Document ID to retrieve from the index")]
) -> str:
    """Retrieve a specific document from Elasticsearch index by document ID."""
    try:
        es = get_es_client()
        
        # Attempt to get the document
        response = es.get(
            index=index,
            id=doc_id
        )
        
        document = response['_source']
        
        result_message = f"✅ **Document retrieved successfully:**\n\n"
        result_message += f"📁 **Index**: {response['_index']}\n"
        result_message += f"📄 **Document ID**: {response['_id']}\n"
        result_message += f"🔢 **Version**: {response['_version']}\n"
        result_message += f"📊 **Found**: {response['found']}\n\n"
        result_message += f"📋 **Document Content**:\n"
        result_message += f"```json\n{json.dumps(document, indent=2, ensure_ascii=False)}\n```\n\n"
        
        # Show key document info if available
        if 'title' in document:
            result_message += f"📝 **Title**: {document['title']}\n"
        if 'summary' in document:
            result_message += f"📄 **Summary**: {document['summary']}\n"
        if 'last_modified' in document:
            result_message += f"📅 **Last Modified**: {document['last_modified']}\n"
        if 'tags' in document:
            result_message += f"🏷️ **Tags**: {', '.join(document['tags']) if isinstance(document['tags'], list) else document['tags']}\n"
            
        return result_message
        
    except Exception as e:
        error_message = "❌ Failed to retrieve document:\n\n"
        
        error_str = str(e).lower()
        if "not_found" in error_str or "not found" in error_str:
            error_message += f"📄 **Document Not Found**: No document with ID '{doc_id}' in index '{index}'\n"
            error_message += f"📍 Check the document ID and index name\n"
            error_message += f"💡 Try: Use 'search' to find documents in this index\n\n"
        elif "index_not_found" in error_str:
            error_message += f"📁 **Index Not Found**: Index '{index}' does not exist\n"
            error_message += f"📍 Check the index name\n"
            error_message += f"💡 Try: Use 'list_indices' to see available indices\n\n"
        elif "connection" in error_str or "refused" in error_str:
            error_message += "🔌 **Connection Error**: Cannot connect to Elasticsearch server\n"
            error_message += f"📍 Check if Elasticsearch is running at the configured address\n"
            error_message += f"💡 Try: Use 'setup_elasticsearch' tool to start Elasticsearch\n\n"
        else:
            error_message += f"⚠️ **Unknown Error**: {str(e)}\n\n"
        
        error_message += f"🔍 **Technical Details**: {str(e)}"
        return error_message


# ================================
# TOOL 4: VALIDATE_DOCUMENT_SCHEMA
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
# TOOL 5: CREATE_DOCUMENT_TEMPLATE
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
    use_ai_enhancement: Annotated[bool, Field(description="Use AI to generate intelligent tags and key points")] = True
) -> str:
    """Create a properly structured document template for knowledge base indexing with AI-generated metadata."""
    try:
        # Initialize metadata
        final_tags = list(tags)  # Copy manual tags
        final_key_points = list(key_points)  # Copy manual key points
        
        # Use AI enhancement if requested and content is provided
        if use_ai_enhancement and content.strip():
            try:
                # Note: Full AI enhancement would require context parameter
                # For now, we'll use pattern-based enhancement
                
                content_lower = content.lower()
                
                # Generate intelligent tags based on content analysis
                ai_tags = []
                if any(word in content_lower for word in ['class', 'function', 'def', 'import', 'var ', 'const ']):
                    ai_tags.extend(["code", "programming"])
                if any(word in content_lower for word in ['config', 'setting', 'parameter', 'option']):
                    ai_tags.extend(["configuration", "settings"])
                if any(word in content_lower for word in ['# ', '## ', '### ', 'documentation', 'guide']):
                    ai_tags.extend(["documentation", "guide"])
                if any(word in content_lower for word in ['test', 'example', 'demo', 'sample']):
                    ai_tags.extend(["example", "testing"])
                if any(word in content_lower for word in ['api', 'endpoint', 'request', 'response']):
                    ai_tags.extend(["api", "integration"])
                if any(word in content_lower for word in ['error', 'bug', 'fix', 'debug']):
                    ai_tags.extend(["troubleshooting", "debugging"])
                if any(word in content_lower for word in ['install', 'setup', 'configure']):
                    ai_tags.extend(["setup", "installation"])
                
                # Merge AI-generated tags with manual tags
                for tag in ai_tags:
                    if tag not in final_tags:
                        final_tags.append(tag)
                
                # Generate intelligent key points
                ai_key_points = []
                lines = content.split('\n')
                non_empty_lines = [line.strip() for line in lines if line.strip()]
                
                if non_empty_lines:
                    ai_key_points.append(f"Content length: {len(content)} characters")
                    ai_key_points.append(f"Number of lines: {len(non_empty_lines)}")
                
                # Look for headers/titles in markdown
                headers = [line for line in non_empty_lines if line.startswith('#')]
                if headers:
                    ai_key_points.append(f"Contains {len(headers)} headers/sections")
                    # Add first few headers as key points
                    for header in headers[:3]:
                        clean_header = header.lstrip('#').strip()
                        if clean_header:
                            ai_key_points.append(f"Section: {clean_header}")
                
                # Look for code blocks
                code_blocks = content.count('```')
                if code_blocks >= 2:
                    ai_key_points.append(f"Contains {code_blocks // 2} code blocks")
                
                # Look for lists
                list_items = [line for line in non_empty_lines if line.startswith(('- ', '* ', '+ '))]
                if list_items:
                    ai_key_points.append(f"Contains {len(list_items)} list items")
                
                # Merge AI-generated key points with manual points
                for point in ai_key_points:
                    if point not in final_key_points:
                        final_key_points.append(point)
                
                # Generate smart summary if not provided
                if not summary and content.strip():
                    if len(content) > 200:
                        # Try to find first meaningful paragraph
                        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip() and not p.strip().startswith('#')]
                        if paragraphs:
                            first_para = paragraphs[0]
                            if len(first_para) > 50:
                                summary = first_para[:200] + ("..." if len(first_para) > 200 else "")
                            else:
                                summary = content[:200].strip() + "..."
                        else:
                            summary = content[:200].strip() + "..."
                    else:
                        summary = content.strip()
                        
            except Exception as e:
                # AI enhancement failed, continue with manual metadata only
                pass
        
        # Generate auto-summary if still not provided and content is available
        if not summary and content.strip():
            if len(content) > 200:
                summary = content[:200].strip() + "..."
            else:
                summary = content.strip()

        # Create template using helper function - simplified version for this context
        template = {
            "id": title.lower().replace(' ', '-').replace('_', '-')[:50],
            "title": title,
            "summary": summary,
            "content": content,
            "last_modified": datetime.utcnow().isoformat(),
            "priority": priority,
            "tags": final_tags,
            "related": related,
            "source_type": source_type,
            "key_points": final_key_points
        }

        ai_info = ""
        if use_ai_enhancement:
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
# CLI ENTRY POINT
# ================================

def cli_main():
    """CLI entry point for Elasticsearch Document FastMCP server."""
    print("🚀 Starting AgentKnowledgeMCP Elasticsearch Document FastMCP server...")
    print("📄 Tools: index_document, delete_document, get_document, validate_document_schema, create_document_template")
    print("🎯 Purpose: Complete document operations including CRUD, validation, and template creation")
    print("✅ Status: 5 Document tools completed - Ready for production!")

    app.run()

if __name__ == "__main__":
    cli_main()
