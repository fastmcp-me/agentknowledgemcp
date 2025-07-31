#!/usr/bin/env python3
"""
Test the complete enhanced smart prompting system including AI guidance with citations.
"""

import asyncio
import tempfile
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from fastmcp import Client
from src.prompts.sub_servers.smart_prompting_server import app as smart_prompting_app

async def test_complete_enhanced_system():
    """Test the complete enhanced smart prompting system with AI citations."""
    
    print("🚀 Testing Complete Enhanced Smart Prompting System")
    print("=" * 60)
    
    # Create temporary .knowledges structure in project root
    project_root = Path(__file__).parent.parent
    knowledges_dir = project_root / ".knowledges_test"
    
    try:
        # Create test structure
        workflows_dir = knowledges_dir / "workflows"
        rules_dir = knowledges_dir / "rules"
        memories_dir = knowledges_dir / "memories"
        
        workflows_dir.mkdir(parents=True, exist_ok=True)
        rules_dir.mkdir(parents=True, exist_ok=True)
        memories_dir.mkdir(parents=True, exist_ok=True)
        
        # Create sample content
        workflow_content = """# API Development Workflow

## Development Steps
1. Design API endpoints
2. Write OpenAPI specification
3. Implement handlers
4. Add validation middleware
5. Write comprehensive tests
6. Update documentation

## Code Review Process
1. Self-review checklist
2. Peer review assignment
3. Address feedback
4. Final approval and merge

## Deployment
1. Run CI/CD pipeline
2. Deploy to staging environment
3. Run integration tests
4. Deploy to production"""

        rules_content = """# FastMCP Development Rules

## Architecture Standards
- Use FastMCP framework for all MCP servers
- Implement proper error handling
- Add comprehensive logging
- Follow async/await patterns

## Code Quality
- Type hints are mandatory
- Docstrings for all public functions
- Unit tests with >80% coverage
- Use proper exception handling

## Security Guidelines
- Validate all user inputs
- Use secure authentication
- Log security events
- Regular dependency updates"""

        memory_content = """# Project Lessons Learned

## FastMCP Integration Issues
Date: 2025-01-15
Issue: Client testing required specific attribute handling
Solution: Use result.data for tools, result.messages[0].content.text for prompts
Location: tests/test_modular_prompt_server.py:lines 45-50

## Virtual Environment Setup
Date: 2025-01-20  
Issue: macOS externally-managed-environment restrictions
Solution: Always use virtual environments for testing
Command: python3 -m venv test_env && source test_env/bin/activate

## Sub Server Architecture
Date: 2025-01-25
Lesson: Modular mounting pattern works well with FastMCP
Benefits: 64% code reduction while maintaining functionality
Files: src/prompts/prompt_server.py, src/prompts/sub_servers/"""

        # Write files
        (workflows_dir / "api-development.md").write_text(workflow_content)
        (rules_dir / "fastmcp-standards.md").write_text(rules_content)
        (memories_dir / "project-lessons.md").write_text(memory_content)
        
        print(f"📁 Created test knowledge base: {knowledges_dir}")
        
        # Test with FastMCP client (simulating no workspace - will show formatted error)
        print(f"\n🧪 Testing smart prompting tool with enhanced citations...")
        
        async with Client(smart_prompting_app) as client:
            # List available tools
            tools = await client.list_tools()
            print(f"🛠️ Available tools: {[tool.name for tool in tools]}")
            
            # Test the ask_mcp_advance tool
            try:
                result = await client.call_tool("ask_mcp_advance", {
                    "intended_action": "implement new API endpoint",
                    "task_description": "Create a new REST API endpoint for user management with proper validation and testing",
                    "scope": "feature"
                })
                
                guidance = result.data
                print(f"\n📋 **Enhanced Guidance Response:**")
                print("-" * 50)
                print(guidance)
                print("-" * 50)
                
                # Verify enhancement features in response
                print(f"\n✅ **Enhancement Verification:**")
                
                # Check that the response asks for citations (even though workspace isn't available)
                has_citation_requirement = "file citations" in guidance.lower() or "backticks" in guidance.lower()
                print(f"   📝 Citation requirement mentioned: {'✅ YES' if has_citation_requirement else '❌ NO'}")
                
                # Check error handling for no workspace
                has_workspace_guidance = "workspace" in guidance.lower() and "permissions" in guidance.lower()
                print(f"   🏠 Workspace guidance provided: {'✅ YES' if has_workspace_guidance else '❌ NO'}")
                
                # Verify structured format
                has_structured_format = "**" in guidance and "Error" in guidance
                print(f"   📋 Structured format: {'✅ YES' if has_structured_format else '❌ NO'}")
                
            except Exception as e:
                print(f"❌ Tool call failed: {str(e)}")
        
        print(f"\n🎯 **Expected Behavior with Real Workspace:**")
        print(f"   📁 Tool would load from: `{knowledges_dir}/`")
        print(f"   📄 Files with line numbers: workflows/api-development.md:1-20")
        print(f"   🤖 AI would include citations like: `rules/fastmcp-standards.md:8-12`")
        print(f"   📝 User could then ask agent to edit specific lines")
        
        print(f"\n💡 **Citation Examples AI Should Provide:**")
        print(f"   ✅ 'Follow API development process in `workflows/api-development.md:3-8`'")
        print(f"   ✅ 'Apply FastMCP standards from `rules/fastmcp-standards.md:4-7`'")
        print(f"   ✅ 'Remember testing lessons from `memories/project-lessons.md:3-5`'")
        
        return True
        
    finally:
        # Cleanup test directory
        if knowledges_dir.exists():
            import shutil
            shutil.rmtree(knowledges_dir)
            print(f"\n🧹 Cleaned up test directory: {knowledges_dir}")

if __name__ == "__main__":
    asyncio.run(test_complete_enhanced_system())
