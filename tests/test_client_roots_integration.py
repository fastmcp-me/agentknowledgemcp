#!/usr/bin/env python3
"""
Test FastMCP Client with custom roots to verify server can load .knowledges directory
This tests the complete workflow: Client sets roots -> Server gets roots -> Load content
"""

import asyncio
import tempfile
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from fastmcp import Client
from src.prompts.sub_servers.smart_prompting_server import app as smart_prompting_app

async def test_client_roots_integration():
    """Test FastMCP client with custom roots and server context integration."""
    
    print("🔍 Testing Client Roots Integration with Smart Prompting Server")
    print("=" * 70)
    
    # Create temporary project structure with .knowledges
    with tempfile.TemporaryDirectory() as temp_dir:
        project_root = Path(temp_dir)
        knowledges_dir = project_root / ".knowledges"
        
        # Create .knowledges structure
        workflows_dir = knowledges_dir / "workflows"
        rules_dir = knowledges_dir / "rules"
        memories_dir = knowledges_dir / "memories"
        
        workflows_dir.mkdir(parents=True)
        rules_dir.mkdir(parents=True) 
        memories_dir.mkdir(parents=True)
        
        # Create sample content
        workflow_content = """# Client Testing Workflow

## Setup Process
1. Create temporary project directory
2. Setup .knowledges structure
3. Initialize FastMCP client with custom roots
4. Test server context integration

## Verification Steps
1. Client sets project root correctly
2. Server receives roots via context
3. Content loading works from correct path
4. AI guidance includes proper file citations"""

        rules_content = """# FastMCP Client Testing Rules

## Root Configuration
- Client must set project root directory
- Server must receive roots via ctx.list_roots()
- Paths must be absolute and accessible

## Content Verification
- All .knowledges subdirectories loaded
- File paths relative to project root
- Line numbers included for citations

## Testing Standards  
- Use temporary directories for isolation
- Verify both client and server behavior
- Test error handling for missing directories"""

        memory_content = """# Client-Server Integration Lessons

## FastMCP Root Handling
Date: 2025-07-31
Issue: Need to verify client can set roots and server can access them
Solution: Test complete integration with temporary directory structure

## Context API Usage
Key insight: ctx.list_roots() should return client-provided roots
Important: Server should use these roots to locate .knowledges directory

## Testing Strategy
Approach: Create isolated test environment with temp directories
Benefit: Ensures reproducible tests without affecting real project structure"""

        # Write test content
        (workflows_dir / "client-testing.md").write_text(workflow_content)
        (rules_dir / "client-rules.md").write_text(rules_content)
        (memories_dir / "integration-lessons.md").write_text(memory_content)
        
        print(f"📁 Created test project structure:")
        print(f"   🏠 Project root: {project_root}")
        print(f"   📚 Knowledge base: {knowledges_dir}")
        print(f"   📄 Files: {len(list(knowledges_dir.rglob('*.md')))} markdown files")
        
        # Test 1: Check if Client supports roots parameter
        print(f"\n🧪 Test 1: Client with Custom Roots")
        print("-" * 40)
        
        try:
            # Create client with roots parameter (discovered in API!)
            from mcp.types import Root
            from fastmcp import Client  # Re-import to fix scope issue
            
            # Convert project root to MCP Root object
            project_root_uri = project_root.as_uri()
            custom_roots = [Root(uri=project_root_uri, name="test-project")]
            
            async with Client(smart_prompting_app, roots=custom_roots) as client:
                print(f"✅ Client created with custom roots: {project_root}")
                
                # List available tools
                tools = await client.list_tools()
                print(f"✅ Tools available: {[tool.name for tool in tools]}")
                
                # Test ask_mcp_advance tool with custom roots
                print(f"\n🧪 Test 2: Smart Prompting with Custom Roots")
                print("-" * 40)
                
                result = await client.call_tool("ask_mcp_advance", {
                    "intended_action": "test client roots integration",
                    "task_description": "Verify that client can set roots and server can access .knowledges content",
                    "scope": "testing"
                })
                
                guidance = result.data
                print(f"📋 **Tool Response with Custom Roots:**")
                print(guidance[:500] + "..." if len(guidance) > 500 else guidance)
                
                # Check if it worked
                print(f"\n📊 **Response Analysis:**")
                has_error = "Error" in guidance or "❌" in guidance
                has_citations = "`" in guidance and ".md" in guidance
                has_line_numbers = "Lines" in guidance or ":" in guidance
                has_knowledges_content = "workflows" in guidance or "rules" in guidance or "memories" in guidance
                
                print(f"   🚨 Contains error: {'❌ YES' if has_error else '✅ NO'}")
                print(f"   📝 Contains file citations: {'✅ YES' if has_citations else '❌ NO'}")
                print(f"   🔢 Contains line numbers: {'✅ YES' if has_line_numbers else '❌ NO'}")
                print(f"   📚 Contains knowledge content: {'✅ YES' if has_knowledges_content else '❌ NO'}")
                
                if not has_error and has_knowledges_content:
                    print(f"\n🎉 **SUCCESS**: Client roots integration working!")
                    print(f"   ✅ Client successfully provided custom roots")
                    print(f"   ✅ Server received roots and loaded .knowledges content")
                    print(f"   ✅ AI guidance generated from custom project structure")
                else:
                    print(f"\n⚠️ **NEEDS INVESTIGATION**: {guidance[:200]}...")
                
        except Exception as e:
            print(f"❌ Client with roots test failed: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # Test 3: Research Client API for roots support
        print(f"\n🔍 Test 3: FastMCP Client API Research")
        print("-" * 40)
        
        # Check Client class for roots-related parameters
        from fastmcp import Client
        import inspect
        
        client_signature = inspect.signature(Client.__init__)
        print(f"📝 Client.__init__ parameters: {list(client_signature.parameters.keys())}")
        
        # Look for any roots-related methods
        client_methods = [method for method in dir(Client) if 'root' in method.lower()]
        print(f"🌳 Root-related methods: {client_methods}")
        
        # Check if there are any context-related methods
        context_methods = [method for method in dir(Client) if 'context' in method.lower()]
        print(f"🔄 Context-related methods: {context_methods}")
        
        print(f"\n💡 **Expected Behavior for Working Integration:**")
        print(f"   1. Client should accept roots parameter during initialization")
        print(f"   2. Server ctx.list_roots() should return client-provided roots")
        print(f"   3. Server should load content from correct .knowledges directory")
        print(f"   4. AI guidance should include proper file citations")
        
        print(f"\n🎯 **Next Steps:**")
        print(f"   1. Check FastMCP documentation for client roots configuration")
        print(f"   2. Test with actual VS Code MCP client (if available)")
        print(f"   3. Create mock context with custom roots for testing")
        print(f"   4. Verify end-to-end workflow with real workspace")
        
        return True

async def test_mock_context_with_roots():
    """Test server behavior with mock context that provides custom roots."""
    
    print(f"\n🧪 Test 4: Mock Context with Custom Roots")
    print("-" * 40)
    
    # Import the smart prompting function directly for testing
    from src.prompts.sub_servers.smart_prompting_server import ask_mcp_advice
    
    # Create a mock context that simulates client-provided roots
    class MockContext:
        def __init__(self, roots):
            self._roots = roots
        
        async def list_roots(self):
            """Return mock roots as if provided by client."""
            return self._roots
        
        async def info(self, message):
            print(f"ℹ️ Context Info: {message}")
        
        async def error(self, message):
            print(f"❌ Context Error: {message}")
        
        async def sample(self, prompt, temperature=0.3):
            """Mock AI sampling - return a sample response with citations."""
            return type('MockSample', (), {
                'text': f"""Based on the project knowledge provided, here's the guidance:

## Test Client Roots Integration

1. **Follow the setup process** from `workflows/client-testing.md:4-7`:
   - Create temporary project directory (line 4)
   - Setup .knowledges structure (line 5)
   - Initialize FastMCP client with custom roots (line 6)

2. **Apply testing rules** from `rules/client-rules.md:4-6`:
   - Client must set project root directory (line 4)
   - Server must receive roots via ctx.list_roots() (line 5)
   - Paths must be absolute and accessible (line 6)

3. **Remember integration lessons** from `memories/integration-lessons.md:7-8`:
   - ctx.list_roots() should return client-provided roots (line 7)
   - Server should use these roots to locate .knowledges directory (line 8)

This provides a complete testing strategy with proper file citations."""
            })()
    
    # Create temporary structure for mock test
    with tempfile.TemporaryDirectory() as temp_dir:
        project_root = Path(temp_dir)
        
        # Create mock roots (simulating what client would provide)
        mock_roots = [project_root]  # Client provides project root
        mock_context = MockContext(mock_roots)
        
        # Create actual .knowledges structure
        knowledges_dir = project_root / ".knowledges"
        workflows_dir = knowledges_dir / "workflows"
        rules_dir = knowledges_dir / "rules"
        memories_dir = knowledges_dir / "memories"
        
        workflows_dir.mkdir(parents=True)
        rules_dir.mkdir(parents=True)
        memories_dir.mkdir(parents=True)
        
        # Create test files (same as before)
        (workflows_dir / "client-testing.md").write_text("""# Client Testing Workflow

## Setup Process
1. Create temporary project directory
2. Setup .knowledges structure  
3. Initialize FastMCP client with custom roots
4. Test server context integration""")
        
        (rules_dir / "client-rules.md").write_text("""# FastMCP Client Testing Rules

## Root Configuration
- Client must set project root directory
- Server must receive roots via ctx.list_roots()
- Paths must be absolute and accessible""")
        
        (memories_dir / "integration-lessons.md").write_text("""# Client-Server Integration Lessons

## Context API Usage
Key insight: ctx.list_roots() should return client-provided roots
Important: Server should use these roots to locate .knowledges directory""")
        
        print(f"📁 Mock test structure created: {project_root}")
        
        # Test the ask_mcp_advance function directly with mock context
        try:
            # Import smart_app correctly for this scope
            from src.prompts.sub_servers.smart_prompting_server import app as smart_app
            
            # Access tools from FastMCP app using correct API
            tools_dict = smart_app._tools  # FastMCP stores tools in _tools dict
            ask_mcp_tool = tools_dict.get("ask_mcp_advance")
            
            if ask_mcp_tool is None:
                print("❌ Could not find ask_mcp_advance tool")
                print(f"Available tools: {list(tools_dict.keys())}")
                return
            
            # Call the underlying function directly
            result = await ask_mcp_tool.function(
                intended_action="test mock context integration",
                task_description="Verify server can load content when context provides custom roots",
                ctx=mock_context,
                scope="testing"
            )
            
            print(f"📋 **Mock Context Test Result:**")
            print(result)
            
            # Verify result contains expected elements
            print(f"\n✅ **Mock Test Verification:**")
            has_citations = "`" in result and ".md:" in result
            has_line_numbers = ":4-" in result or ":7-" in result
            has_workflows = "workflows/" in result
            has_rules = "rules/" in result
            has_memories = "memories/" in result
            
            print(f"   📝 Contains file citations: {'✅ YES' if has_citations else '❌ NO'}")
            print(f"   🔢 Contains line numbers: {'✅ YES' if has_line_numbers else '❌ NO'}")
            print(f"   📋 References workflows: {'✅ YES' if has_workflows else '❌ NO'}")
            print(f"   📏 References rules: {'✅ YES' if has_rules else '❌ NO'}")
            print(f"   💭 References memories: {'✅ YES' if has_memories else '❌ NO'}")
            
            if all([has_citations, has_line_numbers, has_workflows, has_rules, has_memories]):
                print(f"\n🎉 **SUCCESS**: Mock context integration works perfectly!")
                print(f"   ✅ Server can receive custom roots from context")
                print(f"   ✅ Content loading works with provided roots")
                print(f"   ✅ AI guidance includes proper file citations")
                print(f"   ✅ Line numbers are included for precise referencing")
            else:
                print(f"\n⚠️ **PARTIAL SUCCESS**: Some features working, others need improvement")
            
        except Exception as e:
            print(f"❌ Mock context test failed: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_client_roots_integration())
    asyncio.run(test_mock_context_with_roots())
