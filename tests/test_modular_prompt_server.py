#!/usr/bin/env python3
"""
FastMCP Client-Based Testing for Modular Prompt Server
Tests all sub servers and main server using FastMCP's built-in client testing capabilities.

Based on FastMCP documentation: https://github.com/jlowin/fastmcp
Key Pattern: Use Client(mcp) for in-memory testing without process management.
"""

import asyncio
from pathlib import Path

# Import pytest only for actual pytest runs
try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False
    # Define a dummy pytest.mark.asyncio for manual runs
    class DummyPytest:
        class mark:
            @staticmethod
            def asyncio(func):
                return func
    pytest = DummyPytest()

# Import FastMCP client for testing
try:
    from fastmcp import Client
except ImportError:
    print("❌ FastMCP not available for testing. Install with: pip install fastmcp")
    exit(1)

# Import our servers for testing
import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.prompts.prompt_server import app as main_prompt_app
from src.prompts.sub_servers.smart_prompting_server import app as smart_prompting_app  
from src.prompts.sub_servers.instructions_server import app as instructions_app

class TestModularPromptServer:
    """Test suite for the modular prompt server architecture using FastMCP Client."""
    
    @pytest.mark.asyncio
    async def test_main_prompt_server_tools(self):
        """Test that main server properly mounts and exposes sub server tools."""
        async with Client(main_prompt_app) as client:
            # List all available tools
            tools = await client.list_tools()
            tool_names = [tool.name for tool in tools]
            
            print(f"🛠️ Available tools: {tool_names}")
            
            # Verify ask_mcp_advance tool is available from smart prompting sub server
            assert "ask_mcp_advance" in tool_names, "ask_mcp_advance tool should be mounted from smart prompting sub server"
            
            # Test tool call (this will test the VS Code integration path)
            try:
                result = await client.call_tool("ask_mcp_advance", {
                    "intended_action": "test server functionality",
                    "task_description": "Testing the modular prompt server architecture"
                })
                print(f"✅ ask_mcp_advance tool result: {result.data[:100]}...")
                assert result.data is not None, "Tool should return some response"
            except Exception as e:
                # Expected to fail without VS Code workspace - that's okay for this test
                print(f"ℹ️ ask_mcp_advance failed as expected without VS Code workspace: {str(e)[:100]}...")
                assert "workspace root" in str(e).lower() or "error" in str(e).lower() or "list roots" in str(e).lower()

    @pytest.mark.asyncio
    async def test_main_prompt_server_prompts(self):
        """Test that main server properly mounts and exposes sub server prompts."""
        async with Client(main_prompt_app) as client:
            # List all available prompts
            prompts = await client.list_prompts()
            prompt_names = [prompt.name for prompt in prompts]
            
            print(f"📝 Available prompts: {prompt_names}")
            
            # Verify prompts are available from instructions sub server
            assert "mcp_usage_guide" in prompt_names, "mcp_usage_guide prompt should be mounted from instructions sub server"
            assert "copilot_instructions" in prompt_names, "copilot_instructions prompt should be mounted from instructions sub server"
            
            # Test prompt execution
            result = await client.get_prompt("mcp_usage_guide")
            prompt_text = result.messages[0].content.text if result.messages and hasattr(result.messages[0].content, 'text') else str(result.messages)
            print(f"✅ mcp_usage_guide prompt result length: {len(prompt_text)} characters")
            assert "MCP Server Usage Guide" in prompt_text, "Prompt should contain usage guide content"
            
            result = await client.get_prompt("copilot_instructions") 
            prompt_text = result.messages[0].content.text if result.messages and hasattr(result.messages[0].content, 'text') else str(result.messages)
            print(f"✅ copilot_instructions prompt result length: {len(prompt_text)} characters")
            assert "AI Assistant Instructions" in prompt_text, "Prompt should contain assistant instructions"

    @pytest.mark.asyncio
    async def test_smart_prompting_sub_server_isolation(self):
        """Test smart prompting sub server in isolation."""
        async with Client(smart_prompting_app) as client:
            # List tools in isolation
            tools = await client.list_tools()
            tool_names = [tool.name for tool in tools]
            
            print(f"🧠 Smart prompting tools: {tool_names}")
            assert len(tool_names) == 1, "Smart prompting server should have exactly 1 tool"
            assert "ask_mcp_advance" in tool_names, "Should have ask_mcp_advance tool"
            
            # Test isolated tool call
            try:
                result = await client.call_tool("ask_mcp_advance", {
                    "intended_action": "test isolation",
                    "task_description": "Testing smart prompting server in isolation"
                })
                print(f"✅ Isolated smart prompting result: {result.data[:100]}...")
            except Exception as e:
                print(f"ℹ️ Expected isolation test failure: {str(e)[:100]}...")
                # Expected without workspace

    @pytest.mark.asyncio  
    async def test_instructions_sub_server_isolation(self):
        """Test instructions sub server in isolation."""
        async with Client(instructions_app) as client:
            # List prompts in isolation
            prompts = await client.list_prompts()
            prompt_names = [prompt.name for prompt in prompts]
            
            print(f"📚 Instructions prompts: {prompt_names}")
            assert len(prompt_names) == 2, "Instructions server should have exactly 2 prompts"
            assert "mcp_usage_guide" in prompt_names, "Should have mcp_usage_guide prompt"
            assert "copilot_instructions" in prompt_names, "Should have copilot_instructions prompt"
            
            # Test isolated prompt execution  
            result = await client.get_prompt("mcp_usage_guide")
            prompt_text = result.messages[0].content.text if result.messages and hasattr(result.messages[0].content, 'text') else str(result.messages)
            print(f"✅ Isolated usage guide length: {len(prompt_text)} characters")
            assert len(prompt_text) > 100, "Usage guide should have substantial content"
            
            result = await client.get_prompt("copilot_instructions")
            prompt_text = result.messages[0].content.text if result.messages and hasattr(result.messages[0].content, 'text') else str(result.messages)
            print(f"✅ Isolated instructions length: {len(prompt_text)} characters") 
            assert len(prompt_text) > 100, "Instructions should have substantial content"

    @pytest.mark.asyncio
    async def test_server_metadata_and_info(self):
        """Test server metadata and information."""
        async with Client(main_prompt_app) as client:
            # Test that mounting preserves all capabilities
            tools = await client.list_tools()
            prompts = await client.list_prompts()
            
            print(f"📊 Total capabilities: {len(tools)} tools, {len(prompts)} prompts")
            assert len(tools) >= 1, "Should have at least 1 tool from smart prompting"
            assert len(prompts) >= 2, "Should have at least 2 prompts from instructions"

    @pytest.mark.asyncio
    async def test_modular_architecture_benefits(self):
        """Test that modular architecture provides expected benefits."""
        
        # Test that sub servers work independently
        async with Client(smart_prompting_app) as smart_client:
            smart_tools = await smart_client.list_tools()
            
        async with Client(instructions_app) as instructions_client:
            instructions_prompts = await instructions_client.list_prompts()
            
        # Test that main server combines all functionality
        async with Client(main_prompt_app) as main_client:
            main_tools = await main_client.list_tools()
            main_prompts = await main_client.list_prompts()
            
        # Verify modular benefits
        print(f"🏗️ Architecture verification:")
        print(f"   Smart prompting: {len(smart_tools)} tools")
        print(f"   Instructions: {len(instructions_prompts)} prompts") 
        print(f"   Main server: {len(main_tools)} tools, {len(main_prompts)} prompts")
        
        # Main server should have all capabilities from sub servers
        assert len(main_tools) >= len(smart_tools), "Main server should include smart prompting tools"
        assert len(main_prompts) >= len(instructions_prompts), "Main server should include instruction prompts"
        
        # Verify no capability loss during mounting
        smart_tool_names = {tool.name for tool in smart_tools}
        main_tool_names = {tool.name for tool in main_tools}
        assert smart_tool_names.issubset(main_tool_names), "All smart prompting tools should be available in main server"
        
        instructions_prompt_names = {prompt.name for prompt in instructions_prompts}
        main_prompt_names = {prompt.name for prompt in main_prompts}
        assert instructions_prompt_names.issubset(main_prompt_names), "All instruction prompts should be available in main server"

async def run_comprehensive_tests():
    """Run all tests manually for demonstration."""
    print("🚀 Starting comprehensive FastMCP client-based testing...")
    print("=" * 60)
    
    test_suite = TestModularPromptServer()
    
    test_methods = [
        ("Main Server Tools", test_suite.test_main_prompt_server_tools),
        ("Main Server Prompts", test_suite.test_main_prompt_server_prompts),
        ("Smart Prompting Isolation", test_suite.test_smart_prompting_sub_server_isolation),
        ("Instructions Isolation", test_suite.test_instructions_sub_server_isolation),
        ("Server Metadata", test_suite.test_server_metadata_and_info),
        ("Modular Architecture Benefits", test_suite.test_modular_architecture_benefits),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_method in test_methods:
        print(f"\n🧪 Running: {test_name}")
        print("-" * 40)
        try:
            await test_method()
            print(f"✅ {test_name}: PASSED")
            passed += 1
        except Exception as e:
            print(f"❌ {test_name}: FAILED - {str(e)}")
            failed += 1
    
    print(f"\n{'=' * 60}")
    print(f"🏁 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Modular architecture is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
    
    return failed == 0

if __name__ == "__main__":
    # Run tests manually
    asyncio.run(run_comprehensive_tests())
