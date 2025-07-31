#!/usr/bin/env python3
"""
Instructions Sub-Server - FastMCP Implementation
Provides comprehensive MCP usage guides and copilot instructions.

This server handles all instruction-related prompts for AgentKnowledgeMCP,
including usage guides and AI assist    elif content_type == "rules":
        return f"""# 📏 Rules Management Assistant

You are a smart assistant for managing project rules and standards in the `.knowledges/rules/` directory.

## User Request
The user wants: {user_request}

## Your Role
Help users organize and manage coding standards, conventions, development requirements, and project rules.avioral guidelines.
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
    """FastMCP server for AI assistant instructions and smart prompting guidance."""

import os
from pathlib import Path
from typing import Literal
from fastmcp import FastMCP

app = FastMCP(name="Instructions Server")

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

def _load_mcp_usage_instructions() -> str:
    """Load the MCP usage instructions for comprehensive guidance."""
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
        return "Error reading MCP usage instructions (encoding issue). Please reinstall AgentKnowledgeMCP or check file integrity."
    except PermissionError:
        return "Permission denied reading MCP usage instructions. Please check file permissions for the AgentKnowledgeMCP installation."
    except Exception as e:
        return f"Error loading MCP usage instructions: {str(e)}. Please refer to GitHub documentation: https://github.com/itshare4u/AgentKnowledgeMCP"

def cli_main():
    """CLI entry point for Instructions FastMCP server."""
    print("🚀 Starting AgentKnowledgeMCP Instructions FastMCP server...")
    print("📝 Available prompts:")
    print("  • mcp_usage_guide - Comprehensive usage guide with scenarios and tutorials")
    print("  • copilot_instructions - AI assistant behavioral guidelines and protocols")
    print("  • smart_prompting_assistant - Smart assistant for managing workflows, rules, and memories")
    print("✨ Returns complete guidance content for optimal MCP server usage")

    app.run()

if __name__ == "__main__":
    cli_main()

def _find_existing_content(directory: Path, new_content: str) -> tuple[bool, str]:
    """Check if similar content already exists in the directory."""
    if not directory.exists():
        return False, ""
    
    # Get all markdown files in the directory
    md_files = list(directory.glob("*.md"))
    
    # Simple content matching - check if key phrases exist
    content_words = set(new_content.lower().split())
    
    for md_file in md_files:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                existing_content = f.read().lower()
                existing_words = set(existing_content.split())
                
                # Calculate simple word overlap
                overlap = len(content_words.intersection(existing_words))
                overlap_ratio = overlap / len(content_words) if content_words else 0
                
                # If more than 50% word overlap, consider it similar
                if overlap_ratio > 0.5:
                    return True, str(md_file)
                    
        except Exception:
            continue
    
    return False, ""

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

@app.prompt(
    name="mcp_usage_guide", 
    description="Comprehensive usage guide with scenarios and tutorials for AgentKnowledgeMCP",
    tags={"usage", "guide", "tutorial", "scenarios", "comprehensive", "help"}
)
async def mcp_usage_guide() -> str:
    """Return comprehensive usage guide with scenarios and tutorials for AgentKnowledgeMCP."""
    
    # Load the usage instructions content
    usage_content = _load_mcp_usage_instructions()
    
    # Return the content with helpful context
    return f"""# 📖 AgentKnowledgeMCP Comprehensive Usage Guide

This guide provides complete scenarios, tutorials, and best practices for using AgentKnowledgeMCP effectively:

{usage_content}

💡 **Pro Tip**: This guide contains real-world scenarios and step-by-step tutorials. Use it to understand how to leverage AgentKnowledgeMCP's full potential in your workflow."""

@app.prompt(
    name="smart_prompting_assistant",
    description="Smart prompting assistant for managing project workflows, rules, and memories in .knowledges directory",
    tags={"smart-prompting", "workflows", "rules", "memories", "knowledges", "project-management"}
)
async def smart_prompting_assistant(
    content_type: Literal["workflow", "rules", "memories"],
    user_request: str
) -> str:
    """Smart assistant for managing project knowledge in .knowledges directory.
    
    Args:
        content_type: Type of content to manage (workflow, rules, or memories)
        user_request: What the user wants to add or manage
    """
    
    if content_type == "workflow":
        return f"""# 🔄 Workflow Management Assistant

You are a smart assistant for managing project workflows in the `.knowledges/workflows/` directory.

## User Request
The user wants: {user_request}

## Your Role
Help users organize and manage step-by-step processes, procedures, and workflows for their projects.

## Instructions
1. **Check existing content**: Always search the `.knowledges/workflows/` directory first to see what workflows already exist
2. **Avoid duplicates**: If similar workflow exists, guide user to update existing file instead of creating new one
3. **Create organized content**: For new workflows, create well-structured markdown files with clear steps
4. **Use descriptive names**: Name files descriptively (e.g., `deployment-process.md`, `code-review-workflow.md`)

## Workflow Content Format
When creating new workflow files, use this structure:
```markdown
# Workflow: [Process Name]

## Overview
[Brief description of what this workflow accomplishes]

## Prerequisites
- [Requirement 1]
- [Requirement 2]

## Steps
1. [Step 1 with details]
2. [Step 2 with details]
3. [Step 3 with details]

## Expected Outcomes
- [Outcome 1]
- [Outcome 2]

## Notes
[Any additional notes or considerations]

---
*Created: [Date]*
```

## Best Practices
- Keep workflows actionable and specific
- Include all necessary prerequisites
- Use numbered steps for clarity
- Add expected outcomes for verification
- Include troubleshooting notes when relevant"""

    elif content_type == "rules":
        return """# � Rules Management Assistant

You are a smart assistant for managing project rules and standards in the `.knowledges/rules/` directory.

## Your Role
Help users organize and manage coding standards, conventions, development requirements, and project rules.

## Instructions
1. **Check existing content**: Always search the `.knowledges/rules/` directory first to see what rules already exist
2. **Avoid duplicates**: If similar rule exists, guide user to update existing file instead of creating new one
3. **Create consistent standards**: For new rules, create clear, enforceable guidelines
4. **Use descriptive names**: Name files descriptively (e.g., `coding-standards.md`, `git-conventions.md`)

## Rules Content Format
When creating new rules files, use this structure:
```markdown
# Rule: [Rule Name]

## Description
[Clear description of what this rule covers]

## Requirements
- [Requirement 1 - specific and measurable]
- [Requirement 2 - specific and measurable]

## Examples
### ✅ Good Example
```
[Show correct implementation]
```

### ❌ Bad Example
```
[Show what to avoid]
```

## Validation
- [How to check compliance]
- [Tools or methods for verification]

## Exceptions
[When this rule might not apply]

---
*Established: [Date]*
```

## Best Practices
- Make rules specific and measurable
- Include examples of correct and incorrect usage
- Provide validation methods
- Keep rules practical and enforceable
- Document any exceptions clearly"""

    else:  # memories
        return f"""# 🧠 Memories Management Assistant

You are a smart assistant for managing project memories and important information in the `.knowledges/memories/` directory.

## User Request
The user wants: {user_request}

## Your Role
Help users capture and organize important project information, decisions, lessons learned, and institutional knowledge.

## Instructions
1. **Check existing content**: Always search the `.knowledges/memories/` directory first to see what memories already exist
2. **Avoid duplicates**: If similar memory exists, guide user to update existing file or cross-reference
3. **Capture context**: For new memories, include full context and background
4. **Use date-based names**: Name files with dates for chronological organization (e.g., `2024-01-15-architecture-decision.md`)

## Memory Content Format
When creating new memory files, use this structure:
```markdown
# Memory: [Topic/Decision Name]

## Date
[Date of event/decision]

## Context
[Background information and circumstances]

## Details
[Detailed description of what happened, was decided, or learned]

## Impact
[How this affects the project going forward]

## Key Takeaways
- [Lesson learned 1]
- [Lesson learned 2]

## Related
- [Link to related files/decisions]
- [Related team members involved]

## Follow-up Actions
- [ ] [Action item 1]
- [ ] [Action item 2]

---
*Recorded: [Date and Time]*
```

## Best Practices
- Capture memories while they're fresh
- Include all relevant context and background
- Document both what worked and what didn't
- Cross-reference related memories and decisions
- Include specific dates and people involved
- Add follow-up actions when applicable"""

def _get_content_type_description(content_type: str) -> str:
    """Get description for each content type."""
    descriptions = {
        "workflow": "Step-by-step processes and procedures for project tasks (e.g., release process, deployment steps)",
        "rules": "Project standards, conventions, and development requirements (e.g., coding standards, review guidelines)", 
        "memories": "Important project information, decisions, and lessons learned (e.g., architectural decisions, common pitfalls)"
    }
    return descriptions.get(content_type, "Unknown content type")

def _generate_filename(content: str, content_type: str) -> str:
    """Generate a descriptive filename based on content."""
    # Extract first few words for filename
    words = content.strip().split()[:4]  # Take first 4 words
    filename_base = "-".join(word.lower().strip(".,!?;:") for word in words if word.isalnum() or word.strip(".,!?;:").isalnum())
    
    # Ensure filename is not too long
    if len(filename_base) > 30:
        filename_base = filename_base[:30]
    
    # Add content type prefix if helpful
    if content_type == "memories":
        from datetime import datetime
        date_str = datetime.now().strftime("%Y-%m-%d")
        return f"{date_str}-{filename_base}.md"
    else:
        return f"{filename_base}.md"

def _format_content_for_type(content: str, content_type: str) -> str:
    """Format content appropriately for each type."""
    if content_type == "memories":
        from datetime import datetime
        date_str = datetime.now().strftime("%Y-%m-%d")
        return f"""# Memory Entry - {date_str}

## Context
{content}

## Impact
[Describe the impact or importance of this information]

## Related
[List any related files, decisions, or documentation]

---
*Added: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*"""
    
    elif content_type == "workflow":
        return f"""# Workflow: [Process Name]

## Overview
{content}

## Steps
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Prerequisites
- [Requirement 1]
- [Requirement 2]

## Expected Outcomes
- [Outcome 1]
- [Outcome 2]

---
*Created: {datetime.now().strftime("%Y-%m-%d")}*"""
    
    else:  # rules
        return f"""# Rule: [Rule Name]

## Description
{content}

## Requirements
- [Requirement 1]
- [Requirement 2]

## Examples
```
[Example code or configuration]
```

## Validation
- [How to check compliance]

---
*Established: {datetime.now().strftime("%Y-%m-%d")}*"""

def cli_main():
    """CLI entry point for Instructions FastMCP server."""
    print("🚀 Starting AgentKnowledgeMCP Instructions FastMCP server...")
    print("📝 Available prompts:")
    print("  • mcp_usage_guide - Comprehensive usage guide with scenarios and tutorials")
    print("  • copilot_instructions - AI assistant behavioral guidelines and protocols")
    print("  • smart_prompting_assistant - Smart assistant for managing workflows, rules, and memories")
    print("✨ Returns complete guidance content for optimal MCP server usage")

    app.run()

if __name__ == "__main__":
    cli_main()
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
