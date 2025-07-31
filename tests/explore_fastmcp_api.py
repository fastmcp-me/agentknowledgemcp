#!/usr/bin/env python3
"""
Simple FastMCP API exploration to understand the correct attribute names.
"""

import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from fastmcp import Client
from src.prompts.prompt_server import app as main_prompt_app

async def explore_api():
    """Explore FastMCP API to understand correct attribute names."""
    print("🔍 Exploring FastMCP Client API...")
    
    async with Client(main_prompt_app) as client:
        # Test tools
        print("\n📋 Testing tools...")
        tools = await client.list_tools()
        print(f"   Type: {type(tools)}")
        print(f"   Length: {len(tools)}")
        if tools:
            tool = tools[0]
            print(f"   First tool type: {type(tool)}")
            print(f"   First tool attributes: {dir(tool)}")
            print(f"   First tool name: {tool.name}")
            
            # Test tool call
            result = await client.call_tool(tool.name, {
                "intended_action": "test api",
                "task_description": "Testing API structure"
            })
            print(f"   Tool call result type: {type(result)}")
            print(f"   Tool call result attributes: {dir(result)}")
            # Try different possible attributes
            for attr in ['text', 'content', 'result', 'data', 'message']:
                if hasattr(result, attr):
                    val = getattr(result, attr)
                    print(f"   Has attribute '{attr}': {type(val)} = {str(val)[:100]}...")
        
        # Test prompts  
        print("\n📝 Testing prompts...")
        prompts = await client.list_prompts()
        print(f"   Type: {type(prompts)}")
        print(f"   Length: {len(prompts)}")
        if prompts:
            prompt = prompts[0]
            print(f"   First prompt type: {type(prompt)}")
            print(f"   First prompt attributes: {dir(prompt)}")
            print(f"   First prompt name: {prompt.name}")
            
            # Test prompt call
            result = await client.get_prompt(prompt.name)
            print(f"   Prompt result type: {type(result)}")
            print(f"   Prompt result attributes: {dir(result)}")
            # Try different possible attributes
            for attr in ['text', 'content', 'result', 'data', 'message', 'messages']:
                if hasattr(result, attr):
                    val = getattr(result, attr)
                    print(f"   Has attribute '{attr}': {type(val)} = {str(val)[:100]}...")

if __name__ == "__main__":
    asyncio.run(explore_api())
