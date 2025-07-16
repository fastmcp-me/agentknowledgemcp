"""
Composed FastMCP server implementation for AgentKnowledgeMCP.
Uses modular service composition architecture for maintainable and scalable design.
"""
import asyncio
import logging
from pathlib import Path

from fastmcp import FastMCP

# Import our existing modules for initialization
from .config import load_config
from .security import init_security
from .elasticsearch_client import init_elasticsearch
from .elasticsearch_setup import auto_setup_elasticsearch
from .confirmation import initialize_confirmation_manager

# Import all services for composition
from .services import (
    elasticsearch_service,
    file_service,
    admin_service,
    confirmation_service,
    version_control_service
)

# Load configuration and initialize components
CONFIG = load_config()
init_security(CONFIG["security"]["allowed_base_directory"])

# Initialize confirmation manager
confirmation_manager = initialize_confirmation_manager(CONFIG)
print(f"✅ Confirmation system initialized (enabled: {CONFIG.get('confirmation', {}).get('enabled', True)})")

# Auto-setup Elasticsearch if needed
print("Checking Elasticsearch configuration")
config_path = Path(__file__).parent / "config.json"
setup_result = auto_setup_elasticsearch(config_path, CONFIG)

if setup_result["status"] == "setup_completed":
    # Reload config after setup
    CONFIG = load_config()
    print("✅ Elasticsearch auto-setup completed")
elif setup_result["status"] == "already_configured":
    print("Elasticsearch already configured")
elif setup_result["status"] == "setup_failed":
    print(f"⚠️  Elasticsearch auto-setup failed: {setup_result.get('error', 'Unknown error')}")
    print("📝 You can manually setup using the 'setup_elasticsearch' tool")

init_elasticsearch(CONFIG)

# Create main composed FastMCP server
app = FastMCP(
    name=CONFIG["server"]["name"],
    version=CONFIG["server"]["version"],
    instructions="🏗️ AgentKnowledgeMCP - Modular FastMCP server with service composition architecture for knowledge management, Elasticsearch operations, file management, and system administration"
)

# ================================
# SERVICE COMPOSITION
# ================================

print("🏗️ Composing services into main server...")

# Mount all services using dynamic composition for modularity
# This allows services to be updated independently and changes reflect immediately

# Elasticsearch operations - prefixed with 'es_'
app.mount(elasticsearch_service, prefix="es")
print("✅ Mounted ElasticsearchService with prefix 'es'")

# File operations - prefixed with 'file_'  
app.mount(file_service, prefix="file")
print("✅ Mounted FileOperationsService with prefix 'file'")

# Administrative operations - prefixed with 'admin_'
app.mount(admin_service, prefix="admin") 
print("✅ Mounted AdminService with prefix 'admin'")

# Confirmation system - prefixed with 'confirm_'
app.mount(confirmation_service, prefix="confirm")
print("✅ Mounted ConfirmationService with prefix 'confirm'")

# Version control - prefixed with 'vc_'
app.mount(version_control_service, prefix="vc")
print("✅ Mounted VersionControlService with prefix 'vc'")

print("🎉 Service composition completed successfully!")

# ================================
# COMPATIBILITY ALIASES (Optional)
# ================================

# Add some non-prefixed aliases for backward compatibility with existing clients
# These are imported statically for performance

async def setup_compatibility_aliases():
    """Setup backward compatibility aliases for existing tool names."""
    try:
        # Import core Elasticsearch tools without prefix for compatibility
        await app.import_server(elasticsearch_service, prefix=None)
        print("✅ Added compatibility aliases for Elasticsearch tools")
        
        # Import core admin tools without prefix
        core_admin_tools = FastMCP("CoreAdminTools")
        
        # Add only the most commonly used admin tools without prefix
        @core_admin_tools.tool()
        async def get_config():
            return await admin_service.get_tool("get_config")()
            
        @core_admin_tools.tool() 
        async def update_config(config_section=None, config_key=None, config_value=None, full_config=None):
            tool = await admin_service.get_tool("update_config")
            return await tool(config_section, config_key, config_value, full_config)
            
        await app.import_server(core_admin_tools, prefix=None)
        print("✅ Added compatibility aliases for core admin tools")
        
    except Exception as e:
        print(f"⚠️ Warning: Could not setup compatibility aliases: {e}")

def cli_main():
    """CLI entry point for composed FastMCP server."""
    print("🚀 Starting AgentKnowledgeMCP Composed FastMCP server...")
    print(f"📊 Server: {CONFIG['server']['name']}")
    print(f"🔧 Version: {CONFIG['server']['version']}")
    print("🌟 Architecture: Modular FastMCP with Service Composition")
    print()
    print("📋 Available Services:")
    print("  🔍 Elasticsearch Service (es_*) - Document search, indexing, and management")
    print("  📁 File Operations Service (file_*) - File and directory operations")
    print("  ⚙️ Admin Service (admin_*) - Configuration and system management") 
    print("  ✅ Confirmation Service (confirm_*) - User confirmation workflow")
    print("  📜 Version Control Service (vc_*) - File versioning and history")
    print()
    print("🔗 Compatibility: Core tools also available without prefixes")
    print()
    
    # Setup compatibility aliases
    async def setup_and_run():
        await setup_compatibility_aliases()
        # Start the FastMCP app
        app.run()
    
    # Run the server
    asyncio.run(setup_and_run())

if __name__ == "__main__":
    cli_main()
