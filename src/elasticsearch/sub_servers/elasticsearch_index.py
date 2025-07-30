"""
Elasticsearch Index FastMCP Server
Index management operations extracted from main elasticsearch server.
Handles index creation, deletion, and listing operations.
"""
import json
from typing import List, Dict, Any, Optional, Annotated
from datetime import datetime

from fastmcp import FastMCP, Context
from pydantic import Field

from ..elasticsearch_client import get_es_client
from ...config.config import load_config

# Create FastMCP app
app = FastMCP(
    name="AgentKnowledgeMCP-Index",
    version="1.0.0",
    instructions="Elasticsearch index management tools"
)


# ================================
# TOOL 1: LIST_INDICES
# ================================

@app.tool(
    description="List all available Elasticsearch indices with document count and size statistics",
    tags={"elasticsearch", "list", "indices", "stats"}
)
async def list_indices() -> str:
    """List all available Elasticsearch indices with comprehensive statistics."""
    try:
        es = get_es_client()
        
        # Get basic index info
        indices_info = es.indices.get_alias(index="*")
        
        # Get index stats
        try:
            stats = es.indices.stats(index="*")
        except Exception:
            stats = None
        
        if not indices_info:
            return ("📂 **No Indices Found**\n\n" +
                   "🔍 **Status**: No Elasticsearch indices exist yet\n" +
                   "💡 **Next Steps**: Create your first index using 'create_index' tool\n" +
                   "📚 **Example**: create_index(index='my_documents', mapping={...})")
        
        result = "📊 **Elasticsearch Indices Overview**\n\n"
        
        # Sort indices alphabetically
        sorted_indices = sorted(indices_info.keys())
        
        # Check for index metadata
        metadata_available = False
        if "index_metadata" in sorted_indices:
            metadata_available = True
            try:
                metadata_result = es.search(index="index_metadata", body={"query": {"match_all": {}}})
                metadata_docs = {doc["_source"]["index_name"]: doc["_source"] 
                               for doc in metadata_result["hits"]["hits"]}
            except Exception:
                metadata_docs = {}
        else:
            metadata_docs = {}
        
        result += f"📈 **Summary**: {len(sorted_indices)} indices found\n"
        if metadata_available:
            result += f"📋 **Metadata**: {len(metadata_docs)} indices documented\n"
        result += f"🔧 **Elasticsearch**: Connected and operational\n\n"
        
        # List each index with details
        for index_name in sorted_indices:
            result += f"📁 **{index_name}**\n"
            
            # Document count and size
            if stats and index_name in stats['indices']:
                index_stats = stats['indices'][index_name]
                doc_count = index_stats['total']['docs']['count']
                size_bytes = index_stats['total']['store']['size_in_bytes']
                size_mb = round(size_bytes / (1024 * 1024), 2)
                
                result += f"   📄 **Documents**: {doc_count:,}\n"
                result += f"   💾 **Size**: {size_mb} MB ({size_bytes:,} bytes)\n"
            else:
                result += f"   📄 **Documents**: Stats unavailable\n"
                result += f"   💾 **Size**: Stats unavailable\n"
            
            # Metadata information
            if index_name in metadata_docs:
                meta = metadata_docs[index_name]
                result += f"   📋 **Purpose**: {meta.get('purpose', 'Not documented')}\n"
                result += f"   🏷️ **Tags**: {', '.join(meta.get('tags', []))}\n"
                result += f"   👤 **Owner**: {meta.get('created_by', 'Unknown')}\n"
            else:
                if index_name != "index_metadata":  # Don't suggest documenting the metadata index itself
                    result += f"   📋 **Metadata**: Not documented\n"
                    result += f"   🔧 Action: Use 'create_index_metadata' to document this index\n"
            
            result += "\n"
        
        # Summary and recommendations
        undocumented_count = len([idx for idx in sorted_indices 
                                if idx not in metadata_docs and idx != "index_metadata"])
        
        if undocumented_count > 0:
            result += f"⚠️ **Governance Notice**:\n"
            result += f"   📊 **Undocumented Indices**: {undocumented_count}\n"
            result += f"   💡 Use 'create_index_metadata' tool to document missing indices\n"
            result += f"   🎯 **Best Practice**: Document all indices for better management\n\n"
        
        result += f"🔧 **Management Tools**:\n"
        result += f"   📝 **Create**: Use 'create_index' to add new indices\n"
        result += f"   🗑️ **Delete**: Use 'delete_index' to remove indices\n"
        result += f"   📋 **Document**: Use 'create_index_metadata' for governance\n"
        result += f"   🔍 **Search**: Use 'search' to query index contents"
        
        return result
        
    except Exception as e:
        error_message = "❌ Failed to list indices:\n\n"
        
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
# TOOL 2: CREATE_INDEX
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
            # This is the metadata index creation - allow it
            pass
        else:
            # For other indices, check if index_metadata exists for governance
            try:
                es.indices.get(index="index_metadata")
                # Metadata index exists, recommend documenting this new index
                governance_reminder = True
            except Exception:
                # No metadata index, suggest creating governance system
                governance_reminder = False
            
            if not governance_reminder:
                return (f"🏛️ **Governance Recommendation**:\n\n" +
                       f"💡 **Setup Index Governance First**: For better management, consider:\n" +
                       f"   🔧 **Use This Tool**: Call 'create_index_metadata' tool first\n" +
                       f"   📋 **Purpose**: Document your indices for better organization\n" +
                       f"   🎯 **Benefits**: Track purpose, ownership, and lifecycle\n\n" +
                       f"🚀 **Quick Start**: Create metadata system:\n" +
                       f"   1. Call 'create_index_metadata' with index name and description\n" +
                       f"   2. Then use this tool to create your actual index\n" +
                       f"   3. Document the new index right after creation\n\n" +
                       f"⚡ **Skip Governance**: If you want to proceed without governance, " +
                       f"create the index directly with your mapping.")
        
        # Check if index already exists
        try:
            existing_index = es.indices.get(index=index)
            return (f"⚠️ **Index Already Exists**: '{index}'\n\n" +
                   f"📋 **Current Mapping**: Index already configured\n" +
                   f"📊 **Status**: Ready for use\n" +
                   f"💡 **Next Steps**: Use 'index_document' to add documents\n" +
                   f"🔧 **Alternative**: Use 'delete_index' first if you want to recreate")
        except Exception:
            # Index doesn't exist, proceed with creation
            pass
        
        # Prepare index body
        index_body = {
            "mappings": mapping
        }
        
        if settings:
            index_body["settings"] = settings
        
        # Create the index
        response = es.indices.create(
            index=index,
            body=index_body
        )
        
        result_message = f"✅ **Index Created Successfully!**\n\n"
        result_message += f"📁 **Index Name**: {index}\n"
        result_message += f"✅ **Acknowledged**: {response.get('acknowledged', False)}\n"
        result_message += f"🔧 **Shards Acknowledged**: {response.get('shards_acknowledged', False)}\n\n"
        
        result_message += f"📋 **Configuration Summary**:\n"
        result_message += f"   🗺️ **Mapping**: {len(mapping.get('properties', {}))} fields defined\n"
        if settings:
            result_message += f"   ⚙️ **Settings**: Custom settings applied\n"
        else:
            result_message += f"   ⚙️ **Settings**: Using Elasticsearch defaults\n"
        
        result_message += f"\n🎯 **Next Steps**:\n"
        if index != "index_metadata":
            result_message += f"   📋 **Step 1**: Document this index using 'create_index_metadata'\n"
        result_message += f"   📝 **Step 2**: Start indexing documents with 'index_document'\n"
        result_message += f"   🔍 **Step 3**: Test with 'search' to query your data\n"
        result_message += f"   📊 **Monitor**: Use 'list_indices' to check status and stats\n\n"
        
        result_message += f"💡 **Best Practices**:\n"
        result_message += f"   ✅ Define field types explicitly in mapping\n"
        result_message += f"   ✅ Consider index lifecycle management\n"
        result_message += f"   ✅ Monitor index size and performance\n"
        result_message += f"   ✅ Document index purpose and ownership"
        
        return result_message
        
    except Exception as e:
        error_message = "❌ Failed to create index:\n\n"
        
        error_str = str(e).lower()
        if "connection" in error_str or "refused" in error_str:
            error_message += "🔌 **Connection Error**: Cannot connect to Elasticsearch server\n"
            error_message += f"📍 Check if Elasticsearch is running at the configured address\n"
            error_message += f"💡 Try: Use 'setup_elasticsearch' tool to start Elasticsearch\n\n"
        elif "invalid" in error_str and "mapping" in error_str:
            error_message += f"🗺️ **Mapping Error**: Invalid mapping configuration\n"
            error_message += f"📍 Check field types and mapping syntax\n"
            error_message += f"💡 **Common Issues**: Incorrect field types, missing properties\n\n"
        elif "already_exists" in error_str or "resource_already_exists" in error_str:
            error_message += f"📁 **Index Exists**: Index '{index}' already exists\n"
            error_message += f"📍 Choose a different name or delete existing index first\n"
            error_message += f"💡 **Options**: Use 'delete_index' then recreate, or use existing index\n\n"
        else:
            error_message += f"⚠️ **Unknown Error**: {str(e)}\n\n"
            
        # Additional help for index_metadata creation
        if index == "index_metadata":
            error_message += f"🏛️ **Metadata Index Help**:\n"
            error_message += f"   📋 **Step 1**: Create metadata index first using 'create_index' with name 'index_metadata'\n"
            error_message += f"   🗺️ **Step 2**: Use proper mapping for metadata fields\n"
            error_message += f"   🔧 **Step 3**: Then use 'create_index_metadata' to document your index\n\n"
        
        error_message += f"🔍 **Technical Details**: {str(e)}"
        return error_message


# ================================
# TOOL 3: DELETE_INDEX
# ================================

@app.tool(
    description="Delete an Elasticsearch index and all its documents permanently",
    tags={"elasticsearch", "delete", "index", "destructive"}
)
async def delete_index(
    index: Annotated[str, Field(description="Name of the Elasticsearch index to delete")]
) -> str:
    """Delete an Elasticsearch index and all its documents permanently."""
    try:
        es = get_es_client()
        
        # Check if index exists first
        try:
            index_info = es.indices.get(index=index)
        except Exception:
            return (f"⚠️ **Index Not Found**: '{index}'\n\n" +
                   f"📁 **Status**: Index does not exist or is not accessible\n" +
                   f"💡 **Check Name**: Verify the index name is correct\n" +
                   f"📊 **List All**: Use 'list_indices' to see available indices\n" +
                   f"🔍 **Search**: Use 'search' if you're looking for documents")
        
        # Get index statistics before deletion for reporting
        try:
            stats = es.indices.stats(index=index)
            doc_count = stats['indices'][index]['total']['docs']['count']
            size_bytes = stats['indices'][index]['total']['store']['size_in_bytes']
            size_mb = round(size_bytes / (1024 * 1024), 2)
            has_stats = True
        except Exception:
            doc_count = "Unknown"
            size_mb = "Unknown"
            has_stats = False
        
        # Check for metadata before deletion
        metadata_info = ""
        try:
            metadata_result = es.search(
                index="index_metadata",
                body={"query": {"term": {"index_name.keyword": index}}}
            )
            if metadata_result["hits"]["total"]["value"] > 0:
                metadata_info = f"\n⚠️ **Metadata Found**: This index has documentation in index_metadata\n"
                metadata_info += f"   📋 **Recommendation**: Use 'delete_index_metadata' to clean up documentation\n"
        except Exception:
            # No metadata index or no metadata found
            pass
        
        # Perform the deletion
        response = es.indices.delete(index=index)
        
        result_message = f"✅ **Index Deleted Successfully!**\n\n"
        result_message += f"🗑️ **Deleted Index**: {index}\n"
        result_message += f"✅ **Acknowledged**: {response.get('acknowledged', False)}\n"
        
        if has_stats:
            result_message += f"\n📊 **Deleted Content**:\n"
            result_message += f"   📄 **Documents**: {doc_count:,} documents removed\n"
            result_message += f"   💾 **Size**: {size_mb} MB freed\n"
        
        result_message += metadata_info
        
        result_message += f"\n⚠️ **Important Warnings**:\n"
        result_message += f"   🚫 **Irreversible**: This action cannot be undone\n"
        result_message += f"   📄 **Data Loss**: All documents in the index are permanently deleted\n"
        result_message += f"   🔧 **Mapping Lost**: Index structure and settings are removed\n\n"
        
        result_message += f"🎯 **Next Steps**:\n"
        if metadata_info:
            result_message += f"   1. Call 'delete_index_metadata' with index name '{index}'\n"
            result_message += f"   2. Clean up any dependent configurations\n"
        else:
            result_message += f"   📊 **Verify**: Use 'list_indices' to confirm deletion\n"
        
        if index != "index_metadata":
            result_message += f"   📋 Consider setting up 'index_metadata' index for better governance\n"
            result_message += f"   💡 Use 'create_index_metadata' tool for future index documentation"
        
        return result_message
        
    except Exception as e:
        error_message = "❌ Failed to delete index:\n\n"
        
        error_str = str(e).lower()
        if "connection" in error_str or "refused" in error_str:
            error_message += "🔌 **Connection Error**: Cannot connect to Elasticsearch server\n"
            error_message += f"📍 Check if Elasticsearch is running at the configured address\n"
            error_message += f"💡 Try: Use 'setup_elasticsearch' tool to start Elasticsearch\n\n"
        elif "index_not_found" in error_str or "not found" in error_str:
            error_message += f"📁 **Index Not Found**: Index '{index}' does not exist\n"
            error_message += f"📍 Check the index name for typos\n"
            error_message += f"💡 Try: Use 'list_indices' to see available indices\n\n"
        elif "illegal_argument" in error_str:
            error_message += f"📝 **Invalid Index Name**: '{index}' is not a valid index name\n"
            error_message += f"📍 Index names must follow Elasticsearch naming conventions\n"
            error_message += f"💡 **Rules**: Lowercase, no special chars except - and _\n\n"
        else:
            error_message += f"⚠️ **Unknown Error**: {str(e)}\n\n"

        error_message += f"🔍 **Technical Details**: {str(e)}"

        return error_message


# ================================
# CLI ENTRY POINT
# ================================

def cli_main():
    """CLI entry point for Elasticsearch Index FastMCP server."""
    print("🚀 Starting AgentKnowledgeMCP Elasticsearch Index FastMCP server...")
    print("📁 Tools: list_indices, create_index, delete_index")
    print("🎯 Purpose: Index creation, deletion, and listing operations")
    print("✅ Status: 3 Index management tools completed - Ready for production!")

    app.run()

if __name__ == "__main__":
    cli_main()
