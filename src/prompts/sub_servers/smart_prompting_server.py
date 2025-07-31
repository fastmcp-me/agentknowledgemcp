#!/usr/bin/env python3
"""
Smart Prompting Sub-Server - FastMCP Implementation
Provides AI-filtered project guidance using .knowledges directory.

This server implements the smart prompting architecture for project-specific guidance,
loading workflows, rules, and memories from the .knowledges directory and providing
AI-synthesized recommendations.
"""

import asyncio
from pathlib import Path
from typing import List, Optional, Annotated
import os

from fastmcp import FastMCP, Context
from pydantic import Field

# Create FastMCP application for smart prompting
app = FastMCP(
    name="AgentKnowledgeMCP-SmartPrompting",
    version="1.0.0",
    instructions="Smart prompting server providing AI-filtered project guidance from .knowledges directory"
)

async def load_knowledges_content(knowledges_dir: Path, scope: str = "project") -> str:
    """
    Load and organize content from .knowledges directory
    
    Args:
        knowledges_dir: Path to .knowledges directory  
        scope: Scope of guidance needed (project, feature, file, etc.)
        
    Returns:
        Formatted string with all relevant knowledge content
    """
    content_sections = []
    
    # Define subdirectories to scan
    subdirs = ["workflows", "rules", "memories"]
    
    for subdir in subdirs:
        subdir_path = knowledges_dir / subdir
        if not subdir_path.exists():
            continue
            
        # Find all markdown files in subdirectory
        md_files = list(subdir_path.glob("*.md"))
        if not md_files:
            continue
            
        section_content = [f"\n## {subdir.upper()}"]
        
        for md_file in md_files:
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    file_content = f.read().strip()
                    if file_content:
                        section_content.append(f"\n### {md_file.stem}")
                        section_content.append(file_content)
            except Exception as e:
                section_content.append(f"\n### {md_file.stem} (ERROR)")
                section_content.append(f"Error reading file: {str(e)}")
        
        if len(section_content) > 1:  # More than just the header
            content_sections.extend(section_content)
    
    if not content_sections:
        return "No knowledge content found in .knowledges directory."
        
    return "\n".join(content_sections)


# ================================
# SMART PROMPTING TOOL
# ================================

@app.tool(
    name="ask_mcp_advance", 
    description="Advanced project guidance using AI-filtered knowledge from .knowledges directory",
    tags={"smart-prompting", "guidance", "ai-filtered", "project-knowledge"}
)
async def ask_mcp_advance(
    intended_action: Annotated[str, Field(description="What you intend to do (e.g., 'implement feature', 'fix bug', 'deploy')")],
    task_description: Annotated[str, Field(description="Detailed description of the specific task")],
    ctx: Context,
    scope: Annotated[str, Field(description="Scope of guidance needed", default="project")] = "project"
) -> str:
    """
    Advanced MCP guidance tool that loads project-specific workflows, rules, and memories
    
    Args:
        intended_action: What the user intends to do (e.g., "implement feature", "fix bug", "deploy")
        task_description: Detailed description of the specific task
        scope: Scope of guidance needed ("project", "feature", "file", "function")
        ctx: FastMCP Context object for workspace access and AI capabilities
        
    Returns:
        AI-filtered guidance based on project knowledge
    """
    try:
        # Get workspace root from VS Code via MCP
        roots = await ctx.list_roots()
        if not roots:
            return """❌ No workspace root available. 

Please ensure:
1. You have a project open in VS Code
2. VS Code MCP extension is properly configured
3. The workspace has root access permissions"""

        workspace_root = Path(str(roots[0]))  # Convert Root object to string then to Path
        knowledges_dir = workspace_root / ".knowledges"
        
        await ctx.info(f"Checking for knowledge in: {knowledges_dir}")
        
        if not knowledges_dir.exists():
            return f"""📁 No .knowledges directory found in {workspace_root}

To use smart prompting, create the following structure:
```
{workspace_root}/
├── .knowledges/
│   ├── workflows/     # Process and procedure documentation  
│   ├── rules/         # Coding standards and guidelines
│   └── memories/      # Lessons learned and project decisions
```

Add relevant .md files to each subdirectory for project-specific guidance."""

        # Load content from .knowledges subdirectories
        await ctx.info("Loading project knowledge...")
        content = await load_knowledges_content(knowledges_dir, scope)
        
        if content == "No knowledge content found in .knowledges directory.":
            return f"""📂 .knowledges directory exists but is empty: {knowledges_dir}

Add .md files to these subdirectories:
- workflows/ - for process documentation
- rules/ - for coding standards and guidelines  
- memories/ - for lessons learned and project decisions

Example files:
- workflows/release-process.md
- rules/coding-standards.md
- memories/architecture-decisions.md"""

        # Use AI filtering for synthesis
        await ctx.info("Synthesizing guidance with AI...")
        
        guidance_prompt = f"""Based on the project knowledge below, provide specific, actionable guidance for this task:

**INTENDED ACTION**: {intended_action}
**TASK DESCRIPTION**: {task_description}  
**SCOPE**: {scope}

**PROJECT KNOWLEDGE**:
{content}

Please provide:
1. Specific steps or recommendations based on the project's workflows
2. Relevant rules or standards to follow
3. Important lessons or decisions to consider
4. Any potential issues or gotchas from project memory

Focus on actionable guidance that incorporates the project's established patterns and practices."""

        guidance = await ctx.sample(guidance_prompt, temperature=0.3)
        
        await ctx.info("✅ Smart prompting guidance generated")
        
        return f"""🧠 **Smart Prompting Guidance**

**Task**: {intended_action} - {task_description}
**Scope**: {scope}
**Knowledge Source**: {workspace_root}/.knowledges/

---

{guidance}

---
*Generated from project-specific workflows, rules, and memories*"""

    except Exception as e:
        await ctx.error(f"Error in ask_mcp_advance: {str(e)}")
        return f"""❌ **Error generating guidance**: {str(e)}

Please check:
1. VS Code workspace permissions
2. .knowledges directory structure  
3. File permissions and encoding
4. MCP Context availability"""


# ================================
# CLI ENTRY POINT
# ================================
def cli_main():
    """CLI entry point for Smart Prompting FastMCP server."""
    print("🧠 Starting AgentKnowledgeMCP Smart Prompting FastMCP server...")
    print("🛠️ Available tools:")
    print("  • ask_mcp_advance - AI-filtered project guidance from .knowledges directory")
    print("✨ Provides intelligent project-specific recommendations and best practices")

    app.run()

if __name__ == "__main__":
    cli_main()
