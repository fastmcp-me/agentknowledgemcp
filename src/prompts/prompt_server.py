"""
AgentKnowledgeMCP Prompt Server
FastMCP server for prompts providing comprehensive MCP usage guide content for LLM assistance.
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
    instructions="Simple prompt server that returns AgentKnowledgeMCP comprehensive usage guide content for LLM assistance"
)

def _load_mcp_usage_instructions() -> str:
    """Load the detailed MCP usage instructions content."""
    try:
        instructions_path = Path(__file__).parent.parent / "resources" / "mcp_usage_instructions.md"
        
        if not instructions_path.exists():
            return "MCP usage instructions not found. Please refer to the GitHub repository: https://github.com/itshare4u/AgentKnowledgeMCP"
        
        with open(instructions_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            
        if not content:
            return "MCP usage instructions file is empty. Please check the installation or refer to online documentation."
            
        return content
        
    except UnicodeDecodeError:
        return "Error reading MCP instructions (encoding issue). Please reinstall AgentKnowledgeMCP or check file integrity."
    except PermissionError:
        return "Permission denied reading MCP instructions. Please check file permissions for the AgentKnowledgeMCP installation."
    except Exception as e:
        return f"Error loading MCP instructions: {str(e)}. Please refer to GitHub documentation: https://github.com/itshare4u/AgentKnowledgeMCP"


# ================================
# MAIN PROMPT: MCP_USAGE_GUIDE
# ================================

@app.prompt(
    name="mcp_usage_guide",
    description="Complete comprehensive usage guide for this MCP server with scenarios and step-by-step tutorials",
    tags={"mcp", "usage", "guide", "scenarios", "tutorials", "comprehensive"}
)
async def mcp_usage_guide() -> str:
    """Return comprehensive MCP server usage instructions with detailed scenarios and step-by-step guidance."""
    
    # Load the detailed MCP usage instructions
    instructions_content = _load_mcp_usage_instructions()
    
    # Return the content as a complete guidance for users
    return f"""# 🚀 Complete MCP Server Usage Guide

This is the comprehensive guide for using AgentKnowledgeMCP server with specific scenarios and step-by-step instructions:

{instructions_content}

💡 **Important Note**: For the best experience, please attach the copilot instructions file to your prompt:
📚 **https://github.com/itshare4u/AgentKnowledgeMCP/blob/main/.github/copilot-instructions.md**

Please use this information to guide users step-by-step on how to work with the MCP server!"""


# ================================
# CLI ENTRY POINT
# ================================
def cli_main():
    """CLI entry point for Prompt FastMCP server."""
    print("🚀 Starting AgentKnowledgeMCP Prompt FastMCP server...")
    print("📝 Available prompt: mcp_usage_guide")
    print("✨ Returns comprehensive usage guide with scenarios and tutorials")

    app.run()

if __name__ == "__main__":
    cli_main()
