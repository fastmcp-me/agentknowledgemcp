"""
AgentKnowledgeMCP Prompt Server
FastMCP server for prompts and resources providing comprehensive usage guide content and documentation.
"""
from pathlib import Path
from typing import Annotated
import json

from fastmcp import FastMCP
from pydantic import Field

# Create FastMCP app for prompt guidance and resource access
app = FastMCP(
    name="AgentKnowledgeMCP-Prompts",
    version="1.0.0",
    instructions="Simple prompts and resources that return AgentKnowledgeMCP comprehensive usage guide content for LLM assistance"
)

def _load_comprehensive_guide() -> str:
    """Load the comprehensive usage guide content."""
    try:
        guide_path = Path(__file__).parent.parent / "resources" / "comprehensive_usage_guide.md"
        
        if not guide_path.exists():
            return "Comprehensive usage guide not found. Please refer to the GitHub repository: https://github.com/itshare4u/AgentKnowledgeMCP"
        
        with open(guide_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            
        if not content:
            return "Comprehensive usage guide is empty. Please check the installation or refer to online documentation."
            
        return content
        
    except UnicodeDecodeError:
        return "Error reading usage guide (encoding issue). Please reinstall AgentKnowledgeMCP or check file integrity."
    except PermissionError:
        return "Permission denied reading usage guide. Please check file permissions for the AgentKnowledgeMCP installation."
    except Exception as e:
        return f"Error loading usage guide: {str(e)}. Please refer to GitHub documentation: https://github.com/itshare4u/AgentKnowledgeMCP"


# ================================
# PROMPT 1: USAGE_GUIDE
# ================================

@app.prompt(
    name="usage_guide",
    description="Return the complete comprehensive usage guide for AgentKnowledgeMCP",
    tags={"usage", "guide", "documentation", "help", "comprehensive"}
)
async def usage_guide() -> str:
    """Return the complete comprehensive usage guide content."""
    
    # Load the comprehensive guide content
    guide_content = _load_comprehensive_guide()
    
    # Return the content as a guidance prompt for the LLM
    return f"""Here is the complete AgentKnowledgeMCP usage guide. Please use this information to help the user with their questions about AgentKnowledgeMCP:

{guide_content}

Please provide clear, helpful guidance based on this documentation."""


# ================================
# PROMPT 2: HELP_REQUEST
# ================================

@app.prompt(
    name="help_request",
    description="Generate help request prompts for specific AgentKnowledgeMCP topics",
    tags={"help", "assistance", "support", "questions"}
)
async def help_request(
    topic: Annotated[str, Field(
        description="What you need help with regarding AgentKnowledgeMCP"
    )] = "general usage"
) -> str:
    """Generate help request prompts for specific topics."""
    
    return f"""I need help with AgentKnowledgeMCP regarding: {topic}

Please provide:
- Clear step-by-step guidance
- Practical examples where applicable  
- Best practices and tips
- Common issues and solutions

Additional context:
- GitHub Repository: https://github.com/itshare4u/AgentKnowledgeMCP
- Documentation: https://github.com/itshare4u/AgentKnowledgeMCP/blob/main/.github/copilot-instructions.md
- Support: https://github.com/itshare4u/AgentKnowledgeMCP/issues"""


# ================================
# RESOURCE 1: COMPREHENSIVE_GUIDE
# ================================

@app.resource(
    uri="resource://comprehensive-usage-guide",
    name="Comprehensive Usage Guide",
    description="Complete AgentKnowledgeMCP usage guide with examples and best practices",
    mime_type="text/markdown",
    tags={"documentation", "guide", "comprehensive"}
)
async def comprehensive_guide() -> str:
    """Return the complete comprehensive usage guide content as a resource."""
    return _load_comprehensive_guide()


# ================================
# RESOURCE 2: CONFIG_TEMPLATE
# ================================

@app.resource(
    uri="resource://config-template",
    name="Configuration Template",
    description="Example configuration file for AgentKnowledgeMCP with all available options",
    mime_type="application/json",
    tags={"configuration", "template", "setup"}
)
async def config_template() -> dict:
    """Return a configuration template with default values and documentation."""
    return {
        "server": {
            "name": "AgentKnowledgeMCP",
            "version": "1.0.0",
            "description": "Elasticsearch MCP Server for knowledge management"
        },
        "elasticsearch": {
            "host": "localhost", 
            "port": 9200,
            "username": "",
            "password": "",
            "index_prefix": "knowledge_",
            "timeout": 30,
            "max_retries": 3
        },
        "security": {
            "allowed_base_directory": "/path/to/your/safe/directory",
            "restrict_file_operations": True,
            "validate_paths": True
        },
        "document_validation": {
            "strict_schema_validation": False,
            "auto_correct_paths": True,
            "require_summary": True
        },
        "confirmation": {
            "enabled": True,
            "require_confirmation_for": ["delete", "overwrite", "destructive_operations"]
        }
    }


# ================================
# RESOURCE 3: QUICK_START
# ================================

@app.resource(
    uri="resource://quick-start-guide",
    name="Quick Start Guide",
    description="Step-by-step quick start guide for new users",
    mime_type="text/markdown",
    tags={"quickstart", "tutorial", "beginner"}
)
async def quick_start_guide() -> str:
    """Return a quick start guide for new users."""
    return """# 🚀 AgentKnowledgeMCP Quick Start Guide

## Step 1: Installation
```bash
# Install with uvx (recommended)
uvx agent-knowledge-mcp

# Or with pip
pip install agent-knowledge-mcp
```

## Step 2: Basic Configuration
```bash
# Create config from template
cp src/config.default.json src/config.json

# Edit your configuration
nano src/config.json
```

## Step 3: Connect to Your AI Assistant

### For Claude Desktop:
Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "agent-knowledge": {
      "command": "uvx",
      "args": ["agent-knowledge-mcp"]
    }
  }
}
```

### For Other MCP Clients:
```json
{
  "mcp.servers": {
    "agent-knowledge": {
      "command": "uvx", 
      "args": ["agent-knowledge-mcp"]
    }
  }
}
```

## Step 4: First Commands
Try these commands with your AI assistant:

1. **Search documents**: "Search for configuration examples"
2. **Index a document**: "Index this markdown file into the knowledge base"
3. **Get help**: "Show me how to use AgentKnowledgeMCP effectively"

## Step 5: Explore Tools
- 🔍 **9 Elasticsearch tools** for search and indexing
- 📁 **11 File system tools** for file management
- ⚙️ **11 Admin tools** for configuration and maintenance
- 📜 **3 Version control tools** for change tracking

## Need Help?
- Use the `usage_guide` prompt for comprehensive documentation
- Check GitHub: https://github.com/itshare4u/AgentKnowledgeMCP
- Ask questions: https://github.com/itshare4u/AgentKnowledgeMCP/issues

Happy knowledge management! 🎉"""


# ================================
# RESOURCE 4: TOOL_REFERENCE
# ================================

@app.resource(
    uri="resource://tools-reference",
    name="Tools Reference",
    description="Complete reference of all available tools organized by category",
    mime_type="application/json",
    tags={"reference", "tools", "api"}
)
async def tools_reference() -> dict:
    """Return a structured reference of all available tools."""
    return {
        "categories": {
            "elasticsearch": {
                "description": "Document search, indexing, and management",
                "prefix": "es_",
                "tools": [
                    {"name": "search", "description": "Search documents with advanced queries"},
                    {"name": "index_document", "description": "Add or update documents in the index"},
                    {"name": "create_index", "description": "Create new Elasticsearch index"},
                    {"name": "get_document", "description": "Retrieve specific document by ID"},
                    {"name": "delete_document", "description": "Remove document from index"},
                    {"name": "list_indices", "description": "List all available indices"},
                    {"name": "delete_index", "description": "Remove entire index"},
                    {"name": "validate_document_schema", "description": "Validate document structure"},
                    {"name": "create_document_template", "description": "Generate document templates"}
                ]
            },
            "file_operations": {
                "description": "Comprehensive file and directory management",
                "prefix": "file_",
                "tools": [
                    {"name": "edit_file", "description": "Unified tool for all file operations (read, write, append, delete, move, copy, info, list, mkdir, rmdir)"}
                ]
            },
            "administration": {
                "description": "System configuration and management",
                "prefix": "admin_",
                "tools": [
                    {"name": "get_config", "description": "View current configuration"},
                    {"name": "update_config", "description": "Modify configuration settings"},
                    {"name": "validate_config", "description": "Check configuration validity"},
                    {"name": "reload_config", "description": "Reload configuration from file"},
                    {"name": "reset_config", "description": "Reset to default configuration"},
                    {"name": "server_status", "description": "Check server health and status"},
                    {"name": "server_upgrade", "description": "Upgrade MCP server"},
                    {"name": "setup_elasticsearch", "description": "Auto-configure Elasticsearch"},
                    {"name": "elasticsearch_status", "description": "Check Elasticsearch connectivity"}
                ]
            }
        },
        "total_tools": 25,
        "backward_compatibility": "All tools available without prefixes for compatibility"
    }


# ================================
# RESOURCE 5: TROUBLESHOOTING
# ================================

@app.resource(
    uri="resource://troubleshooting-guide",
    name="Troubleshooting Guide",
    description="Common issues and solutions for AgentKnowledgeMCP",
    mime_type="text/markdown",
    tags={"troubleshooting", "help", "support"}
)
async def troubleshooting_guide() -> str:
    """Return a troubleshooting guide with common issues and solutions."""
    return """# 🔧 AgentKnowledgeMCP Troubleshooting Guide

## Common Issues & Solutions

### 🚫 Connection Problems
**Issue**: "Server not responding" or "Connection refused"

**Solutions**:
1. Check MCP server status: `admin_server_status`
2. Verify configuration: `admin_get_config`
3. Restart Claude Desktop or your MCP client
4. Check logs for error messages

### 🔍 Search Issues
**Issue**: "Search returns no results" or "Index not found"

**Solutions**:
1. List available indices: `es_list_indices`
2. Check Elasticsearch status: `admin_elasticsearch_status`
3. Try broader search terms
4. Verify documents are indexed: `es_search` with `*` query

### 📄 Document Indexing Problems
**Issue**: "Document validation failed" or "Indexing errors"

**Solutions**:
1. Validate document structure: `es_validate_document_schema`
2. Use document template: `es_create_document_template`
3. Check required fields (title, content, file_path)
4. Verify file permissions and paths

### ⚙️ Configuration Issues
**Issue**: "Invalid configuration" or "Permission denied"

**Solutions**:
1. Validate config: `admin_validate_config`
2. Reset to defaults: `admin_reset_config`
3. Check file permissions in allowed directories
4. Verify Elasticsearch connection settings

### 🐳 Elasticsearch Setup Problems
**Issue**: "Elasticsearch not found" or "Connection timeout"

**Solutions**:
1. Auto-setup Elasticsearch: `admin_setup_elasticsearch`
2. Check Docker installation and status
3. Verify ports (9200, 5601) are available
4. Check firewall and network settings

### 📁 File Operation Errors
**Issue**: "Permission denied" or "File not found"

**Solutions**:
1. Check allowed_base_directory in config
2. Use absolute paths when possible
3. Verify file permissions and ownership
4. Check if file exists: `file_edit_file` with operation=info

## Performance Tips

### 🚀 Optimize Search
- Use specific keywords instead of broad terms
- Utilize field-specific searches
- Implement proper document tagging
- Regular index maintenance

### 💾 Memory Management
- Monitor Elasticsearch heap size
- Regular cleanup of old documents
- Optimize document size and structure
- Use appropriate batch sizes

### 🔒 Security Best Practices
- Restrict allowed_base_directory appropriately
- Regular security audits of configurations
- Monitor file access patterns
- Keep server and dependencies updated

## Getting More Help

### 📞 Support Channels
- GitHub Issues: https://github.com/itshare4u/AgentKnowledgeMCP/issues
- Documentation: https://github.com/itshare4u/AgentKnowledgeMCP
- Community Discussions: GitHub Discussions

### 🔍 Diagnostic Commands
```bash
# Check overall system status
admin_server_status

# Validate current configuration
admin_validate_config

# Test Elasticsearch connectivity
admin_elasticsearch_status

# List available tools and capabilities
# (Use your MCP client's list tools functionality)
```

### 📋 When Reporting Issues
Include:
1. AgentKnowledgeMCP version
2. Error messages (full text)
3. Configuration (sanitized)
4. Steps to reproduce
5. Expected vs actual behavior

Most issues can be resolved by checking configuration, verifying permissions, and ensuring all dependencies are properly installed and running."""


# ================================
# RESOURCE 6: EXAMPLE_WORKFLOWS
# ================================

@app.resource(
    uri="resource://example-workflows",
    name="Example Workflows",
    description="Real-world workflow examples for different use cases",
    mime_type="application/json",
    tags={"examples", "workflows", "use-cases"}
)
async def example_workflows() -> dict:
    """Return structured examples of common workflows."""
    return {
        "workflows": {
            "knowledge_discovery": {
                "name": "Knowledge Discovery",
                "description": "Find and explore existing information",
                "steps": [
                    {"action": "search", "command": "es_search", "example": "Search for 'authentication patterns'"},
                    {"action": "analyze", "command": "es_get_document", "example": "Get detailed document by ID"},
                    {"action": "explore", "command": "es_search", "example": "Find related documents with similar tags"}
                ]
            },
            "document_management": {
                "name": "Document Management",
                "description": "Add, update, and organize documents",
                "steps": [
                    {"action": "create", "command": "es_create_document_template", "example": "Generate template for API documentation"},
                    {"action": "validate", "command": "es_validate_document_schema", "example": "Check document structure"},
                    {"action": "index", "command": "es_index_document", "example": "Add document to knowledge base"},
                    {"action": "track", "command": "vc_commit_file", "example": "Version control the changes"}
                ]
            },
            "code_analysis": {
                "name": "Code Analysis & Documentation",
                "description": "Analyze code and create documentation",
                "steps": [
                    {"action": "read", "command": "file_edit_file", "example": "Read source code files"},
                    {"action": "analyze", "command": "es_search", "example": "Find similar code patterns"},
                    {"action": "document", "command": "es_index_document", "example": "Create code documentation"},
                    {"action": "backup", "command": "file_edit_file", "example": "Copy files to backup location"}
                ]
            },
            "project_setup": {
                "name": "Project Setup",
                "description": "Initialize new project with knowledge management",
                "steps": [
                    {"action": "configure", "command": "admin_update_config", "example": "Set project-specific settings"},
                    {"action": "create_index", "command": "es_create_index", "example": "Create project-specific index"},
                    {"action": "template", "command": "es_create_document_template", "example": "Setup document templates"}
                ]
            },
            "maintenance": {
                "name": "System Maintenance",
                "description": "Regular maintenance and cleanup tasks",
                "steps": [
                    {"action": "status_check", "command": "admin_server_status", "example": "Check system health"},
                    {"action": "elasticsearch_check", "command": "admin_elasticsearch_status", "example": "Verify search functionality"},
                    {"action": "cleanup", "command": "es_delete_document", "example": "Remove outdated documents"},
                    {"action": "optimize", "command": "es_list_indices", "example": "Review index usage and performance"}
                ]
            }
        },
        "use_cases": {
            "personal_knowledge": "Individual knowledge management and note-taking",
            "team_documentation": "Collaborative documentation and knowledge sharing",
            "enterprise_knowledge": "Large-scale organizational knowledge management",
            "research_projects": "Academic and research documentation workflows",
            "software_development": "Code documentation and technical knowledge management"
        }
    }


# ================================
# RESOURCE 7: API_EXAMPLES
# ================================

@app.resource(
    uri="resource://api-examples/{category}",
    name="API Examples by Category",
    description="Specific API usage examples for different tool categories",
    mime_type="text/markdown",
    tags={"api", "examples", "tutorial"}
)
async def api_examples(category: str) -> str:
    """Return API examples for a specific category."""
    
    examples = {
        "elasticsearch": """# 🔍 Elasticsearch API Examples

## Search Documents
```json
// Basic search
{
  "tool": "es_search",
  "arguments": {
    "index": "knowledge_base",
    "query": "authentication patterns",
    "size": 10
  }
}

// Advanced search with filters
{
  "tool": "es_search", 
  "arguments": {
    "index": "knowledge_base",
    "query": "API security",
    "size": 5,
    "fields": ["title", "summary", "tags"]
  }
}
```

## Index Documents
```json
// Index a new document
{
  "tool": "es_index_document",
  "arguments": {
    "index": "knowledge_base",
    "document": {
      "title": "API Authentication Guide",
      "summary": "Complete guide to API authentication patterns",
      "content": "Detailed content here...",
      "file_path": "/docs/api-auth.md",
      "tags": ["api", "authentication", "security"],
      "priority": "high"
    }
  }
}
```

## Create Index
```json
{
  "tool": "es_create_index",
  "arguments": {
    "index": "project_docs",
    "mapping": {
      "properties": {
        "title": {"type": "text"},
        "content": {"type": "text"},
        "created_at": {"type": "date"}
      }
    }
  }
}
```""",

        "file": """# 📁 File Operations API Examples

## Read Files
```json
{
  "tool": "file_edit_file",
  "arguments": {
    "operation": "read",
    "path": "/project/README.md"
  }
}
```

## Write Files
```json
{
  "tool": "file_edit_file",
  "arguments": {
    "operation": "write",
    "path": "/project/new-doc.md",
    "content": "# New Document\\n\\nContent goes here...",
    "create_dirs": true
  }
}
```

## Directory Operations
```json
// List directory contents
{
  "tool": "file_edit_file",
  "arguments": {
    "operation": "list",
    "path": "/project/docs",
    "recursive": true,
    "include_hidden": false
  }
}

// Create directory
{
  "tool": "file_edit_file",
  "arguments": {
    "operation": "mkdir",
    "path": "/project/new-folder"
  }
}
```

## File Information
```json
{
  "tool": "file_edit_file",
  "arguments": {
    "operation": "info",
    "path": "/project/important-file.txt"
  }
}
```""",

        "admin": """# ⚙️ Administration API Examples

## Configuration Management
```json
// Get current configuration
{
  "tool": "admin_get_config",
  "arguments": {}
}

// Update configuration
{
  "tool": "admin_update_config",
  "arguments": {
    "config_section": "security",
    "config_key": "allowed_base_directory",
    "config_value": "/new/safe/directory"
  }
}

// Validate configuration
{
  "tool": "admin_validate_config",
  "arguments": {}
}
```

## System Management
```json
// Check server status
{
  "tool": "admin_server_status",
  "arguments": {}
}

// Setup Elasticsearch
{
  "tool": "admin_setup_elasticsearch",
  "arguments": {
    "include_kibana": true,
    "force_recreate": false
  }
}

// Check Elasticsearch status
{
  "tool": "admin_elasticsearch_status",
  "arguments": {}
}
```"""
    }
    
    return examples.get(category, f"# API Examples for '{category}'\n\nCategory not found. Available categories: elasticsearch, admin")


# ================================
# CLI ENTRY POINT
# ================================
def cli_main():
    """CLI entry point for Prompt FastMCP server."""
    print("🚀 Starting AgentKnowledgeMCP Prompt FastMCP server...")
    print("📝 Prompts: usage_guide, help_request")
    print("📚 Resources: comprehensive-usage-guide, config-template, quick-start-guide, tools-reference, troubleshooting-guide, example-workflows, api-examples/{category}")
    print("✨ Prompts return guidance content and resources provide structured documentation")

    app.run()

if __name__ == "__main__":
    cli_main()
