#!/usr/bin/env python3
"""
Elasticsearch Document Management Helper Functions

This module contains all the core document management functions for
indexing, retrieving, deleting, and validating documents in Elasticsearch.
These functions are used by the main FastMCP tools in elasticsearch_server.py.

Functions:
- index_document_operation: Index a document with smart duplicate prevention
- delete_document_operation: Delete a document from an index
- get_document_operation: Retrieve a document by ID
- validate_document_schema_operation: Validate document structure
- create_document_template_operation: Create a structured document template
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime

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
    generate_smart_doc_id,
    check_title_duplicates,
    get_existing_document_ids,
    check_content_similarity_with_ai
)


async def index_document_operation(
    index: str,
    document: Dict[str, Any],
    doc_id: Optional[str] = None,
    validate_schema: bool = True,
    check_duplicates: bool = True,
    force_index: bool = False,
    use_ai_similarity: bool = True,
    ctx = None
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
                if dup_check['found']:
                    duplicates_info = "\n".join([
                        f"   📄 {dup['title']} (ID: {dup['id']})\n      📝 {dup['summary']}\n      📅 {dup['last_modified']}"
                        for dup in dup_check['duplicates'][:3]
                    ])
                    
                    # Use AI similarity analysis if enabled and content is substantial
                    if use_ai_similarity and content and len(content) > 200 and ctx:
                        try:
                            ai_analysis = await check_content_similarity_with_ai(ctx, content, dup_check['duplicates'])
                            
                            if ai_analysis['is_duplicate']:
                                return (f"🚫 **Potential Duplicate Detected (AI Analysis)**:\n\n" +
                                       f"📄 **Title**: {title}\n" +
                                       f"🤖 **AI Confidence**: {ai_analysis['confidence']:.1%}\n" +
                                       f"📊 **Similarity Score**: {ai_analysis['similarity_score']:.2f}\n\n" +
                                       f"🎯 **AI Recommendation**: {ai_analysis['recommendation']}\n\n" +
                                       f"📋 **Similar Documents Found**:\n{duplicates_info}\n\n" +
                                       f"💡 **Options**:\n" +
                                       f"   • Set `force_index=true` to index anyway\n" +
                                       f"   • Modify content to make it more unique\n" +
                                       f"   • Update existing document instead\n" +
                                       f"   • Set `check_duplicates=false` to skip this check\n\n" +
                                       f"🔍 **AI Reasoning**: {ai_analysis['reasoning']}")
                            else:
                                # AI says it's not a duplicate, but warn about title similarity
                                pass  # Continue with indexing
                                
                        except Exception as ai_error:
                            # Fallback to simple duplicate detection
                            return (f"⚠️ **Potential Duplicate Detected (Title Match)**:\n\n" +
                                   f"📄 **Title**: {title}\n" +
                                   f"⚠️ **AI Analysis Failed**: {str(ai_error)}\n\n" +
                                   f"📋 **Similar Documents Found**:\n{duplicates_info}\n\n" +
                                   f"💡 **Options**:\n" +
                                   f"   • Set `force_index=true` to index anyway\n" +
                                   f"   • Modify title to make it more unique\n" +
                                   f"   • Update existing document instead\n" +
                                   f"   • Set `check_duplicates=false` to skip this check")
                    else:
                        # Simple title-based duplicate detection
                        return (f"⚠️ **Potential Duplicate Detected (Title Match)**:\n\n" +
                               f"📄 **Title**: {title}\n\n" +
                               f"📋 **Similar Documents Found**:\n{duplicates_info}\n\n" +
                               f"💡 **Options**:\n" +
                               f"   • Set `force_index=true` to index anyway\n" +
                               f"   • Modify title to make it more unique\n" +
                               f"   • Update existing document instead\n" +
                               f"   • Set `check_duplicates=false` to skip this check")

        # Validate document schema if required
        if validate_schema:
            try:
                # Validate the document structure
                validation_result = validate_document_structure(document)
                
                if not validation_result['valid']:
                    formatted_errors = format_validation_error(validation_result['errors'])
                    return (f"❌ **Document Validation Failed**:\n\n" +
                           f"📋 **Schema Errors Found**:\n{formatted_errors}\n\n" +
                           f"💡 **Fix Options**:\n" +
                           f"   • Fix the validation errors above\n" +
                           f"   • Use 'create_document_template' for proper format\n" +
                           f"   • Set `validate_schema=false` to skip validation\n" +
                           f"   • Use 'validate_document_schema' tool to check format first")
                    
            except Exception as validation_error:
                if validate_schema:  # Only return error if validation was explicitly requested
                    return (f"❌ **Document Validation Error**:\n\n" +
                           f"⚠️ **Validation Failed**: {str(validation_error)}\n\n" +
                           f"💡 **Solutions**:\n" +
                           f"   • Check document structure format\n" +
                           f"   • Use 'create_document_template' for proper format\n" +
                           f"   • Set `validate_schema=false` to skip validation")

        # Generate smart document ID if not provided
        if not doc_id:
            doc_id = generate_smart_doc_id(document, get_existing_document_ids(es, index))

        # Ensure timestamp is added
        if 'last_modified' not in document:
            document['last_modified'] = datetime.now().isoformat()

        # Index the document
        result = es.index(index=index, id=doc_id, body=document)

        return (f"✅ **Document Indexed Successfully**!\n\n" +
               f"📄 **Document Details**:\n" +
               f"   📋 **Index**: {index}\n" +
               f"   🆔 **ID**: {doc_id}\n" +
               f"   📝 **Title**: {document.get('title', 'No title')}\n" +
               f"   📊 **Result**: {result.get('result', 'unknown')}\n" +
               f"   📅 **Timestamp**: {document.get('last_modified', 'Not set')}\n\n" +
               f"🔍 **Verification**:\n" +
               f"   • Use 'get_document' with ID '{doc_id}' to retrieve\n" +
               f"   • Use 'search' to find by content\n" +
               f"   • Check 'list_indices' to see index statistics\n\n" +
               f"📈 **Index Stats**: Document count and search capabilities updated")

    except Exception as e:
        error_message = "❌ **Failed to index document**:\n\n"
        
        error_str = str(e).lower()
        if "connection" in error_str or "refused" in error_str:
            error_message += "🔌 **Connection Error**: Cannot connect to Elasticsearch server\n"
            error_message += f"📍 Check if Elasticsearch is running at the configured address\n"
            error_message += f"💡 Try: Use 'setup_elasticsearch' tool to start Elasticsearch\n\n"
        elif "index_not_found" in error_str:
            error_message += f"📂 **Index Error**: Index '{index}' does not exist\n"
            error_message += f"📍 Create the index first or check the index name\n"
            error_message += f"💡 Try: Use 'create_index' tool to create the index first\n\n"
        elif "parsing_exception" in error_str or "mapper_parsing_exception" in error_str:
            error_message += f"📝 **Document Format Error**: Invalid document structure\n"
            error_message += f"📍 Check document field types and values\n"
            error_message += f"💡 Try: Use 'validate_document_schema' to check format first\n\n"
        elif "version_conflict" in error_str:
            error_message += f"🔄 **Version Conflict**: Document was modified by another process\n"
            error_message += f"📍 Another update occurred simultaneously\n"
            error_message += f"💡 Try: Retry the operation or fetch latest version first\n\n"
        else:
            error_message += f"⚠️ **Unknown Error**: {str(e)}\n\n"
        
        error_message += f"🔍 **Technical Details**: {str(e)}"
        return error_message


async def delete_document_operation(
    index: str,
    doc_id: str
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
        elif "not_found" in error_str:
            error_message += f"📄 **Document Not Found**: Document with ID '{doc_id}' does not exist\n"
            error_message += f"📍 Check the document ID and index name\n"
            error_message += f"💡 Try: Use 'search' or 'get_document' to verify the document exists\n\n"
        elif "index_not_found" in error_str:
            error_message += f"📂 **Index Error**: Index '{index}' does not exist\n"
            error_message += f"📍 Check the index name spelling\n"
            error_message += f"💡 Try: Use 'list_indices' to see available indices\n\n"
        else:
            error_message += f"⚠️ **Unknown Error**: {str(e)}\n\n"
        
        error_message += f"🔍 **Technical Details**: {str(e)}"
        return error_message


async def get_document_operation(
    index: str,
    doc_id: str
) -> str:
    """Retrieve a document from Elasticsearch index."""
    try:
        es = get_es_client()

        result = es.get(index=index, id=doc_id)

        return f"✅ Document retrieved successfully:\n\n{json.dumps(result, indent=2, ensure_ascii=False)}"

    except Exception as e:
        # Provide detailed error messages for different types of Elasticsearch errors
        error_message = "❌ Failed to retrieve document:\n\n"

        error_str = str(e).lower()
        if "connection" in error_str or "refused" in error_str:
            error_message += "🔌 **Connection Error**: Cannot connect to Elasticsearch server\n"
            error_message += f"📍 Check if Elasticsearch is running at the configured address\n"
            error_message += f"💡 Try: Use 'setup_elasticsearch' tool to start Elasticsearch\n\n"
        elif "not_found" in error_str:
            error_message += f"📄 **Document Not Found**: Document with ID '{doc_id}' does not exist\n"
            error_message += f"📍 Check the document ID and index name\n"
            error_message += f"💡 Try: Use 'search' to find documents or verify the ID\n\n"
        elif "index_not_found" in error_str:
            error_message += f"📂 **Index Error**: Index '{index}' does not exist\n"
            error_message += f"📍 Check the index name spelling\n"
            error_message += f"💡 Try: Use 'list_indices' to see available indices\n\n"
        else:
            error_message += f"⚠️ **Unknown Error**: {str(e)}\n\n"
        
        error_message += f"🔍 **Technical Details**: {str(e)}"
        return error_message


async def validate_document_schema_operation(
    document: Dict[str, Any]
) -> str:
    """Validate document structure against knowledge base schema."""
    try:
        # Perform comprehensive validation
        validation_result = validate_document_structure(document)
        
        if validation_result['valid']:
            return (f"✅ **Document Structure Valid**!\n\n" +
                   f"📋 **Validation Results**:\n" +
                   f"   ✅ Schema structure: Valid\n" +
                   f"   ✅ Required fields: Present\n" +
                   f"   ✅ Field types: Correct\n" +
                   f"   ✅ Format compliance: Good\n\n" +
                   f"📊 **Document Overview**:\n" +
                   f"   📝 Title: {document.get('title', 'Not specified')}\n" +
                   f"   📄 Content length: {len(str(document.get('content', '')))} characters\n" +
                   f"   🏷️ Tags: {len(document.get('tags', []))} tags\n" +
                   f"   🔗 Related: {len(document.get('related', []))} references\n" +
                   f"   📅 Timestamp: {document.get('last_modified', 'Not set')}\n\n" +
                   f"🎯 **Ready for Indexing**: This document can be safely indexed\n" +
                   f"💡 **Next Step**: Use 'index_document' to add to knowledge base")
        else:
            # Format validation errors nicely
            formatted_errors = format_validation_error(validation_result['errors'])
            
            return (f"❌ **Document Validation Failed**:\n\n" +
                   f"📋 **Schema Errors Found**:\n{formatted_errors}\n\n" +
                   f"🔧 **Common Fixes**:\n" +
                   f"   • Ensure all required fields are present\n" +
                   f"   • Check data types (strings, arrays, objects)\n" +
                   f"   • Verify field names match expected schema\n" +
                   f"   • Add missing metadata fields\n\n" +
                   f"💡 **Helpful Tools**:\n" +
                   f"   • Use 'create_document_template' for proper format\n" +
                   f"   • Check existing documents for reference examples\n" +
                   f"   • Review schema documentation")
    
    except DocumentValidationError as e:
        return (f"❌ **Validation Error**:\n\n" +
               f"⚠️ **Schema Issue**: {str(e)}\n\n" +
               f"💡 **Solutions**:\n" +
               f"   • Check document structure format\n" +
               f"   • Use 'create_document_template' for proper format\n" +
               f"   • Review required fields and data types\n" +
               f"   • Ensure JSON structure is valid")
    
    except Exception as e:
        return (f"❌ **Validation Failed**:\n\n" +
               f"⚠️ **Unexpected Error**: {str(e)}\n\n" +
               f"💡 **Troubleshooting**:\n" +
               f"   • Check if document is valid JSON\n" +
               f"   • Ensure document is not empty\n" +
               f"   • Verify all field values are properly formatted\n" +
               f"   • Contact support if error persists\n\n" +
               f"🔍 **Technical Details**: {str(e)}")


async def create_document_template_operation(
    title: str,
    content: str = "",
    summary: str = "",
    tags: list = None,
    key_points: list = None,
    related: list = None,
    priority: str = "medium",
    source_type: str = "markdown",
    use_ai_enhancement: bool = True
) -> str:
    """Create a properly structured document template for knowledge base."""
    try:
        if tags is None:
            tags = []
        if key_points is None:
            key_points = []
        if related is None:
            related = []
        
        # Create base template
        template = create_doc_template_base(
            title=title,
            content=content,
            summary=summary,
            tags=tags,
            key_points=key_points,
            related=related,
            priority=priority,
            source_type=source_type
        )
        
        # Enhance with AI if enabled and content is provided
        if use_ai_enhancement and content and len(content.strip()) > 50:
            try:
                # Generate smart metadata
                ai_metadata = generate_smart_metadata(content, existing_tags=tags)
                
                # Merge AI-generated tags with manual tags
                combined_tags = list(set(tags + ai_metadata.get('tags', [])))
                template['tags'] = combined_tags
                
                # Merge AI-generated key points with manual ones  
                combined_points = list(set(key_points + ai_metadata.get('key_points', [])))
                template['key_points'] = combined_points
                
                ai_used = True
            except Exception as ai_error:
                # Fallback to basic metadata generation
                fallback_metadata = generate_fallback_metadata(content, title)
                template['tags'] = list(set(tags + fallback_metadata.get('tags', [])))
                template['key_points'] = list(set(key_points + fallback_metadata.get('key_points', [])))
                ai_used = False
        else:
            ai_used = False
        
        # Create formatted output
        result = (f"✅ **Document Template Created Successfully**!\n\n" +
                 f"📄 **Template Details**:\n" +
                 f"   📝 **Title**: {template['title']}\n" +
                 f"   📊 **Priority**: {template['priority']}\n" +
                 f"   📁 **Source Type**: {template['source_type']}\n" +
                 f"   🏷️ **Tags**: {len(template['tags'])} total\n" +
                 f"   🎯 **Key Points**: {len(template['key_points'])} total\n" +
                 f"   🔗 **Related**: {len(template['related'])} references\n" +
                 f"   📅 **Created**: {template['last_modified']}\n\n")
        
        if ai_used:
            result += (f"🤖 **AI Enhancement Used**: Generated {len(template['tags'])} total tags and {len(template['key_points'])} total key points\n\n")
        
        result += (f"📋 **Template Structure**:\n" +
                  f"```json\n{json.dumps(template, indent=2, ensure_ascii=False)}\n```\n\n" +
                  f"🎯 **Next Steps**:\n" +
                  f"   • Review and edit the generated template\n" +
                  f"   • Use 'validate_document_schema' to verify structure\n" +
                  f"   • Use 'index_document' to add to knowledge base\n" +
                  f"   • Customize tags and key points as needed\n\n" +
                  f"💡 **Tips**:\n" +
                  f"   • Add more specific tags for better searchability\n" +
                  f"   • Include relevant related document references\n" +
                  f"   • Use descriptive key points for quick understanding")
        
        return result
        
    except Exception as e:
        return (f"❌ **Failed to create document template**:\n\n" +
               f"⚠️ **Error**: {str(e)}\n\n" +
               f"💡 **Solutions**:\n" +
               f"   • Check that title is provided and not empty\n" +
               f"   • Ensure content is valid text if provided\n" +
               f"   • Verify priority is one of: low, medium, high\n" +
               f"   • Check source_type is valid\n\n" +
               f"🔍 **Technical Details**: {str(e)}")
