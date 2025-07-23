"""
AgentKnowledgeMCP Prompt Server
FastMCP server dedicated to providing simple prompts that return comprehensive usage guide content.
"""
from pathlib import Path
from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

# Create FastMCP app for prompt guidance
app = FastMCP(
    name="AgentKnowledgeMCP-Prompts",
    version="1.0.0",
    instructions="Simple prompts that return AgentKnowledgeMCP comprehensive usage guide content for LLM assistance"
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


# CLI entry point
def cli_main():
    """CLI entry point for Prompt FastMCP server."""
    print("🚀 Starting AgentKnowledgeMCP Prompt FastMCP server...")
    print("📝 Prompts: usage_guide, help_request")
    print("✨ Simple prompts that return markdown content for LLM assistance")

    app.run()

if __name__ == "__main__":
    cli_main()
