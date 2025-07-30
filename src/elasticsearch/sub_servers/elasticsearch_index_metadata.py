"""
Elasticsearch Index Metadata FastMCP Server
Index metadata management tools extracted from main elasticsearch server.
Handles documentation, governance, and lifecycle management of index metadata.
"""
import json
from typing import List, Dict, Any, Optional, Annotated
from datetime import datetime

from fastmcp import FastMCP, Context
from pydantic import Field

from src.elasticsearch.elasticsearch_client import get_es_client
from src.config.config import load_config

# Create FastMCP app
app = FastMCP(
    name="AgentKnowledgeMCP-Index-Metadata",
    version="1.0.0",
    instructions="Elasticsearch index metadata management tools"
)


# ================================
# TOOL 1: CREATE_INDEX_METADATA
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
            }
        }
        
        try:
            result = es.search(index=metadata_index, body=search_body)
            if result["hits"]["total"]["value"] > 0:
                existing_doc = result["hits"]["hits"][0]["_source"]
                return (f"⚠️ **Metadata Already Exists** for index '{index_name}'!\n\n" +
                       f"📋 **Existing Documentation**:\n" +
                       f"   📄 **Description**: {existing_doc.get('description', 'Not provided')}\n" +
                       f"   🎯 **Purpose**: {existing_doc.get('purpose', 'Not provided')}\n" +
                       f"   📅 **Created**: {existing_doc.get('created_date', 'Unknown')}\n" +
                       f"   👤 **Created By**: {existing_doc.get('created_by', 'Unknown')}\n" +
                       f"   🏷️ **Tags**: {', '.join(existing_doc.get('tags', []))}\n\n" +
                       f"🔄 **Update Options**:\n" +
                       f"   🔄 **Update**: Use 'update_index_metadata' to modify existing documentation\n" +
                       f"   🗑️ **Replace**: Use 'delete_index_metadata' then 'create_index_metadata'\n" +
                       f"   📊 **View All**: Use 'list_indices' to see all documented indices")
        except Exception:
            # Search failed, but we can still create metadata
            pass
        
        # Create the metadata document
        metadata_doc = {
            "index_name": index_name,
            "description": description,
            "purpose": purpose,
            "data_types": data_types,
            "created_by": created_by,
            "created_date": datetime.utcnow().isoformat(),
            "usage_pattern": usage_pattern,
            "retention_policy": retention_policy,
            "related_indices": related_indices,
            "tags": tags,
            "last_updated": datetime.utcnow().isoformat(),
            "updated_by": created_by
        }
        
        # Index the metadata document
        response = es.index(
            index=metadata_index,
            body=metadata_doc,
            id=f"metadata_{index_name}"
        )
        
        result_message = f"✅ **Index Metadata Created Successfully!**\n\n"
        result_message += f"📋 **Documentation Details**:\n"
        result_message += f"   🏷️ **Index Name**: {index_name}\n"
        result_message += f"   📄 **Description**: {description}\n"
        result_message += f"   🎯 **Purpose**: {purpose}\n"
        result_message += f"   📊 **Data Types**: {', '.join(data_types) if data_types else 'Not specified'}\n"
        result_message += f"   👤 **Created By**: {created_by}\n"
        result_message += f"   📅 **Created**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n"
        result_message += f"   🔄 **Usage Pattern**: {usage_pattern}\n"
        result_message += f"   📋 **Retention Policy**: {retention_policy}\n"
        result_message += f"   🔗 **Related Indices**: {', '.join(related_indices) if related_indices else 'None'}\n"
        result_message += f"   🏷️ **Tags**: {', '.join(tags) if tags else 'None'}\n\n"
        
        result_message += f"🔧 **Management Tools**:\n"
        result_message += f"   🔄 Use 'update_index_metadata' to modify this documentation\n"
        result_message += f"   📊 Use 'list_indices' to view all documented indices\n"
        result_message += f"   🗑️ Use 'delete_index_metadata' to remove this documentation\n\n"
        
        result_message += f"💡 **Best Practices**:\n"
        result_message += f"   ✅ Keep metadata updated when index structure changes\n"
        result_message += f"   ✅ Use descriptive tags for better organization\n"
        result_message += f"   ✅ Document retention policies for compliance\n"
        result_message += f"   ✅ Link related indices for dependency tracking"
        
        return result_message
        
    except Exception as e:
        error_message = "❌ Failed to create index metadata:\n\n"
        
        error_str = str(e).lower()
        if "connection" in error_str or "refused" in error_str:
            error_message += "🔌 **Connection Error**: Cannot connect to Elasticsearch server\n"
            error_message += f"📍 Check if Elasticsearch is running at the configured address\n"
            error_message += f"💡 Try: Use 'setup_elasticsearch' tool to start Elasticsearch\n\n"
        elif "not_found" in error_str and "index" in error_str:
            error_message += f"📁 **Index Error**: Target index '{index_name}' does not exist\n"
            error_message += f"📍 Cannot document an index that doesn't exist\n"
            error_message += f"💡 Try: Create the index first using 'create_index' tool\n\n"
        else:
            error_message += f"⚠️ **Unknown Error**: {str(e)}\n\n"
        
        error_message += f"🔍 **Technical Details**: {str(e)}"
        return error_message


# ================================
# TOOL 2: UPDATE_INDEX_METADATA
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
        
        # Check if metadata exists
        try:
            doc_id = f"metadata_{index_name}"
            existing_doc = es.get(index=metadata_index, id=doc_id)
            current_metadata = existing_doc["_source"]
        except Exception:
            return (f"❌ **No Metadata Found** for index '{index_name}'!\n\n" +
                   f"📋 **Create First**: Use 'create_index_metadata' to document this index\n" +
                   f"📊 **View All**: Use 'list_indices' to see all documented indices\n" +
                   f"💡 **Note**: You must create metadata before you can update it")
        
        # Build update document with only provided fields
        update_doc = {}
        updated_fields = []
        
        if description is not None:
            update_doc["description"] = description
            updated_fields.append("description")
        
        if purpose is not None:
            update_doc["purpose"] = purpose
            updated_fields.append("purpose")
        
        if data_types is not None:
            update_doc["data_types"] = data_types
            updated_fields.append("data_types")
        
        if usage_pattern is not None:
            update_doc["usage_pattern"] = usage_pattern
            updated_fields.append("usage_pattern")
        
        if retention_policy is not None:
            update_doc["retention_policy"] = retention_policy
            updated_fields.append("retention_policy")
        
        if related_indices is not None:
            update_doc["related_indices"] = related_indices
            updated_fields.append("related_indices")
        
        if tags is not None:
            update_doc["tags"] = tags
            updated_fields.append("tags")
        
        # Always update timestamp and updater
        update_doc["last_updated"] = datetime.utcnow().isoformat()
        update_doc["updated_by"] = updated_by
        
        if not updated_fields:
            return (f"⚠️ **No Updates Provided** for index '{index_name}'!\n\n" +
                   f"📋 **Current Metadata**:\n" +
                   f"   📄 **Description**: {current_metadata.get('description', 'Not provided')}\n" +
                   f"   🎯 **Purpose**: {current_metadata.get('purpose', 'Not provided')}\n" +
                   f"   📊 **Data Types**: {', '.join(current_metadata.get('data_types', []))}\n" +
                   f"   🔄 **Usage Pattern**: {current_metadata.get('usage_pattern', 'Not specified')}\n" +
                   f"   📋 **Retention Policy**: {current_metadata.get('retention_policy', 'Not specified')}\n" +
                   f"   🔗 **Related Indices**: {', '.join(current_metadata.get('related_indices', []))}\n" +
                   f"   🏷️ **Tags**: {', '.join(current_metadata.get('tags', []))}\n" +
                   f"   📅 **Last Updated**: {current_metadata.get('last_updated', 'Unknown')}\n\n" +
                   f"💡 **To Update**: Provide at least one field to update")
        
        # Perform the update
        response = es.update(
            index=metadata_index,
            id=doc_id,
            body={"doc": update_doc}
        )
        
        result_message = f"✅ **Index Metadata Updated Successfully!**\n\n"
        result_message += f"🏷️ **Index**: {index_name}\n"
        result_message += f"🔄 **Updated Fields**: {', '.join(updated_fields)}\n"
        result_message += f"👤 **Updated By**: {updated_by}\n"
        result_message += f"📅 **Updated**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n\n"
        
        result_message += f"📋 **Updated Values**:\n"
        for field in updated_fields:
            if field == "data_types" and data_types is not None:
                result_message += f"   📊 **Data Types**: {', '.join(data_types)}\n"
            elif field == "related_indices" and related_indices is not None:
                result_message += f"   🔗 **Related Indices**: {', '.join(related_indices)}\n"
            elif field == "tags" and tags is not None:
                result_message += f"   🏷️ **Tags**: {', '.join(tags)}\n"
            else:
                result_message += f"   📝 **{field.replace('_', ' ').title()}**: {update_doc[field]}\n"
        
        result_message += f"\n🔧 **Management Tools**:\n"
        result_message += f"   📊 Use 'list_indices' to view all documented indices\n"
        result_message += f"   🔄 Use 'update_index_metadata' again to make more changes\n"
        result_message += f"   🗑️ Use 'delete_index_metadata' to remove this documentation"
        
        return result_message
        
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
            error_message += f"💡 Try: Create metadata first using 'create_index_metadata'\n\n"
        else:
            error_message += f"⚠️ **Unknown Error**: {str(e)}\n\n"
        
        error_message += f"🔍 **Technical Details**: {str(e)}"
        return error_message


# ================================
# TOOL 3: DELETE_INDEX_METADATA
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
            }
        }
        
        try:
            result = es.search(index=metadata_index, body=search_body)
            if result["hits"]["total"]["value"] == 0:
                return (f"⚠️ **No Metadata Found** for index '{index_name}'!\n\n" +
                       f"📋 **Nothing to Delete**: This index has no metadata documentation\n" +
                       f"📊 **View All**: Use 'list_indices' to see all documented indices\n" +
                       f"💡 **Create New**: Use 'create_index_metadata' to document this index")
            
            # Get the document to show what's being deleted
            existing_doc = result["hits"]["hits"][0]["_source"]
            doc_id = result["hits"]["hits"][0]["_id"]
            
        except Exception:
            return (f"❌ **Metadata System Error**: Cannot access index metadata\n\n" +
                   f"📍 The metadata index may not exist or be accessible\n" +
                   f"💡 Try: Use 'setup_elasticsearch' tool to verify Elasticsearch status\n" +
                   f"🔧 Alternative: Use 'create_index_metadata' to initialize the system")
        
        # Delete the metadata document
        delete_response = es.delete(
            index=metadata_index,
            id=doc_id
        )
        
        result_message = f"✅ **Index Metadata Deleted Successfully!**\n\n"
        result_message += f"🗑️ **Removed Documentation for**: {index_name}\n\n"
        result_message += f"📋 **Deleted Metadata Details**:\n"
        result_message += f"   📄 **Description**: {existing_doc.get('description', 'Not provided')}\n"
        result_message += f"   🎯 **Purpose**: {existing_doc.get('purpose', 'Not provided')}\n"
        result_message += f"   👤 **Created By**: {existing_doc.get('created_by', 'Unknown')}\n"
        result_message += f"   📅 **Created**: {existing_doc.get('created_date', 'Unknown')}\n"
        result_message += f"   🏷️ **Tags**: {', '.join(existing_doc.get('tags', []))}\n\n"
        
        result_message += f"⚠️ **Important Notes**:\n"
        result_message += f"   📁 **Index Still Exists**: Only metadata documentation was removed\n"
        result_message += f"   📊 **Data Intact**: All data in '{index_name}' remains unchanged\n"
        result_message += f"   🔧 You can now safely use 'delete_index' to remove the actual index\n"
        result_message += f"   📊 Use 'list_indices' to verify metadata removal\n\n"
        
        result_message += f"🎯 **Next Steps**:\n"
        result_message += f"   1. Proceed with 'delete_index {index_name}' to remove the actual index\n"
        result_message += f"   2. Or use 'create_index_metadata' if you want to re-document this index\n"
        result_message += f"   3. Clean up any related indices mentioned in metadata\n\n"
        result_message += f"⚠️ **Important**: This only deleted the documentation, not the actual index"
        
        return result_message
        
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


# ================================
# CLI ENTRY POINT
# ================================

def cli_main():
    """CLI entry point for Elasticsearch Index Metadata FastMCP server."""
    print("🚀 Starting AgentKnowledgeMCP Elasticsearch Index Metadata FastMCP server...")
    print("🔧 Tools: create_index_metadata, update_index_metadata, delete_index_metadata")
    print("📋 Purpose: Index documentation, governance, and lifecycle management")
    print("✅ Status: 3 Index Metadata tools completed - Ready for production!")

    app.run()

if __name__ == "__main__":
    cli_main()
