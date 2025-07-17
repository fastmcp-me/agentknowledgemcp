"""
AgentKnowledgeMCP Main Server - FastMCP Server Composition
Modern server composition using FastMCP mounting architecture for modular design.
"""
import asyncio
from pathlib import Path

from fastmcp import FastMCP

# Import our existing modules for initialization
from src.config.config import load_config
from src.utils.security import init_security
from src.elasticsearch.elasticsearch_client import init_elasticsearch
from src.elasticsearch.elasticsearch_setup import auto_setup_elasticsearch
from src.confirmation.confirmation import initialize_confirmation_manager

# Import individual server modules for mounting
from src.admin.admin_server import app as admin_server_app
from src.elasticsearch.elasticsearch_server import app as elasticsearch_server_app  
from src.file.file_server import app as file_server_app
from src.version_control.version_control_server import app as version_control_server_app

# Load configuration and initialize components
CONFIG = load_config()
init_security(CONFIG["security"]["allowed_base_directory"])

# Initialize confirmation manager
confirmation_manager = initialize_confirmation_manager(CONFIG)
print(f"✅ Confirmation system initialized (enabled: {CONFIG.get('confirmation', {}).get('enabled', True)})")

# Auto-setup Elasticsearch if needed
print("🔍 Checking Elasticsearch configuration...")
config_path = Path(__file__).parent / "config.json"
setup_result = auto_setup_elasticsearch(config_path, CONFIG)

if setup_result["status"] == "setup_completed":
    # Reload config after setup
    CONFIG = load_config()
    print("✅ Elasticsearch auto-setup completed")
elif setup_result["status"] == "already_configured":
    print("✅ Elasticsearch already configured")
elif setup_result["status"] == "setup_failed":
    print(f"⚠️  Elasticsearch auto-setup failed: {setup_result.get('error', 'Unknown error')}")
    print("📝 You can manually setup using the 'setup_elasticsearch' tool")

init_elasticsearch(CONFIG)

# Create main FastMCP server
app = FastMCP(
    name=CONFIG["server"]["name"],
    version=CONFIG["server"]["version"],
    instructions="🏗️ AgentKnowledgeMCP - Modern FastMCP server with modular composition architecture for knowledge management, Elasticsearch operations, file management, and system administration"
)

# ================================
# SERVER COMPOSITION - MOUNTING
# ================================

print("🏗️ Mounting individual servers into main server...")

# Mount Elasticsearch server with 'es' prefix
# This provides: es_search, es_index_document, es_create_index, etc.
app.mount(elasticsearch_server_app, prefix="es")
print("✅ Mounted elasticsearch_server.app with prefix 'es'")

# Mount File operations server with 'file' prefix  
# This provides: file_read_file, file_write_file, file_list_directory, etc.
app.mount(file_server_app, prefix="file")
print("✅ Mounted file_server.app with prefix 'file'")

# Mount Administrative operations server with 'admin' prefix
# This provides: admin_get_config, admin_update_config, admin_server_status, etc.
app.mount(admin_server_app, prefix="admin")
print("✅ Mounted admin_server.app with prefix 'admin'")

# Mount Version control server with 'vc' prefix
# This provides: vc_setup_version_control, vc_commit_file, vc_get_previous_file_version
app.mount(version_control_server_app, prefix="vc")
print("✅ Mounted version_control_server.app with prefix 'vc'")

print("🎉 Server composition completed successfully!")

# ================================
# BACKWARD COMPATIBILITY ALIASES
# ================================

# Add core tools without prefix for backward compatibility using static import
async def setup_compatibility_aliases():
    """Setup backward compatibility aliases for existing tool names."""
    try:
        print("🔗 Setting up backward compatibility aliases...")

        # Import core Elasticsearch tools without prefix for compatibility
        await app.import_server(elasticsearch_server_app, prefix=None)
        print("✅ Added compatibility aliases for Elasticsearch tools")
        
        # Import core file operations without prefix
        await app.import_server(file_server_app, prefix=None)
        print("✅ Added compatibility aliases for File operations")
        
        # Import core admin tools without prefix
        await app.import_server(admin_server_app, prefix=None) 
        print("✅ Added compatibility aliases for Admin tools")
        
        # Import version control tools without prefix
        await app.import_server(version_control_server_app, prefix=None)
        print("✅ Added compatibility aliases for Version Control tools")
        
        print("🔗 Backward compatibility setup complete!")

    except Exception as e:
        print(f"⚠️ Warning: Could not setup compatibility aliases: {e}")

def cli_main():
    """CLI entry point for main FastMCP server."""
    print("🚀 Starting AgentKnowledgeMCP Main FastMCP Server...")
    print(f"📊 Server: {CONFIG['server']['name']}")
    print(f"🔧 Version: {CONFIG['server']['version']}")
    print("🌟 Architecture: Modern FastMCP with Server Mounting")
    print()
    print("📋 Available Servers (Mounted):")
    print("  🔍 Elasticsearch Server (es_*) - Document search, indexing, and management")
    print("    └─ Tools: search, index_document, create_index, get_document, delete_document, list_indices, delete_index")
    print("  📁 File Operations Server (file_*) - File and directory operations")
    print("    └─ Tools: read_file, write_file, append_file, delete_file, move_file, copy_file, list_directory, create_directory, delete_directory, file_info")
    print("  ⚙️ Admin Server (admin_*) - Configuration and system management")
    print("    └─ Tools: get_config, update_config, server_status, server_upgrade, setup_elasticsearch, elasticsearch_status, get_comprehensive_usage_guide, validate_config, reset_config, reload_config")
    print("  📜 Version Control Server (vc_*) - File versioning and history")
    print("    └─ Tools: setup_version_control, commit_file, get_previous_file_version")
    print()
    print("🔗 Compatibility: All tools also available without prefixes")
    print()

    # Setup compatibility aliases first (async part)
    async def setup_compatibility():
        await setup_compatibility_aliases()
    
    # Run async setup
    asyncio.run(setup_compatibility())
    
    # Start the FastMCP app (sync)
    app.run()

if __name__ == "__main__":
    cli_main()
