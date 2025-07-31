#!/usr/bin/env python3
"""
Instructions Sub-Server - FastMCP Implementation
Provides comprehensive MCP usage guides and copilot instructions.

This server handles all instruction-related prompts for AgentKnowledgeMCP,
including usage guides and AI assistant behavioral guidelines.
"""

from pathlib import Path
from typing import Annotated

from fastmcp import FastMCP, Context
from pydantic import Field

# Create FastMCP application for instructions
app = FastMCP(
    name="AgentKnowledgeMCP-Instructions",
    version="1.0.0",
    instructions="Instructions server providing comprehensive MCP usage guides and AI assistant behavioral guidelines"
)

def _load_mcp_usage_instructions() -> str:
    """Load the detailed MCP usage instructions content."""
    try:
        instructions_path = Path(__file__).parent.parent.parent / "resources" / "mcp_usage_instructions.md"
        
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


def _load_copilot_instructions() -> str:
    """Load the copilot instructions content for AI assistants."""
    try:
        instructions_path = Path(__file__).parent.parent.parent / "resources" / "copilot-instructions.md"
        
        if not instructions_path.exists():
            return "Copilot instructions not found. Please refer to the GitHub repository: https://github.com/itshare4u/AgentKnowledgeMCP"
        
        with open(instructions_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            
        if not content:
            return "Copilot instructions file is empty. Please check the installation or refer to online documentation."
            
        return content
        
    except UnicodeDecodeError:
        return "Error reading copilot instructions (encoding issue). Please reinstall AgentKnowledgeMCP or check file integrity."
    except PermissionError:
        return "Permission denied reading copilot instructions. Please check file permissions for the AgentKnowledgeMCP installation."
    except Exception as e:
        return f"Error loading copilot instructions: {str(e)}. Please refer to GitHub documentation: https://github.com/itshare4u/AgentKnowledgeMCP"


# ================================
# INSTRUCTION PROMPTS
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


@app.prompt(
    name="copilot_instructions",
    description="AI Assistant instructions for optimal AgentKnowledgeMCP usage - Complete behavioral guidelines and mandatory protocols",
    tags={"copilot", "instructions", "ai", "assistant", "guidelines", "protocols", "behavioral"}
)
async def copilot_instructions() -> str:
    """Return the complete copilot instructions content for AI assistants working with AgentKnowledgeMCP."""
    
    # Load the copilot instructions content
    instructions_content = _load_copilot_instructions()
    
    # Return the content with additional context
    return f"""# 🤖 AI Assistant Instructions for AgentKnowledgeMCP

These are the complete behavioral guidelines and mandatory protocols for AI assistants working with AgentKnowledgeMCP:

{instructions_content}

💡 **Usage Note**: These instructions establish the behavioral framework that AI assistants should follow when working with the AgentKnowledgeMCP system to ensure optimal knowledge management and user interaction."""


# ================================
# CLI ENTRY POINT
# ================================
def cli_main():
    """CLI entry point for Instructions FastMCP server."""
    print("📚 Starting AgentKnowledgeMCP Instructions FastMCP server...")
    print("📝 Available prompts:")
    print("  • mcp_usage_guide - Comprehensive usage guide with scenarios and tutorials")
    print("  • copilot_instructions - AI assistant behavioral guidelines and protocols")
    print("✨ Provides complete guidance and behavioral instructions for optimal MCP usage")

    app.run()

if __name__ == "__main__":
    cli_main()
