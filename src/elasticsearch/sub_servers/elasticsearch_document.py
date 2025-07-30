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

from src.elasticsearch.elasticsearch_client import get_es_client
from src.elasticsearch.document_schema import (
    validate_document_structure,
    DocumentValidationError,
    format_validation_error
)
from src.elasticsearch.elasticsearch_helper import (
    generate_smart_metadata, 
    generate_fallback_metadata,
    generate_smart_doc_id,
    check_title_duplicates,
    get_existing_document_ids,
    check_content_similarity_with_ai
)
from src.config.config import load_config
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
# CLI ENTRY POINT
# ================================

def cli_main():
    """CLI entry point for Elasticsearch Document FastMCP server."""
    print("🚀 Starting AgentKnowledgeMCP Elasticsearch Document FastMCP server...")
    print("📄 Tools: index_document, delete_document, get_document")
    print("🎯 Purpose: Document indexing, retrieval, and deletion operations")
    print("✅ Status: 3 Document tools completed - Ready for production!")

    app.run()

if __name__ == "__main__":
    cli_main()
