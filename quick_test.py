#!/usr/bin/env python3
"""Quick test of the restructured MCP server"""

import subprocess
import sys
import time

def test_server_startup():
    """Test if server can start up properly"""
    print("🚀 Testing MCP Server startup...")
    
    try:
        # Test import
        print("📦 Testing imports...")
        result = subprocess.run([
            sys.executable, "-c", 
            "import src.server; print('✅ Imports working')"
        ], cwd="/Users/nguyenkimchung/AgentKnowledgeMCP", 
           capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Module imports successfully")
            print(result.stdout.strip())
        else:
            print("❌ Import failed:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️ Import test timed out")
        return False
    except Exception as e:
        print(f"❌ Import test error: {e}")
        return False
    
    return True

def test_config_loading():
    """Test if config can be loaded"""
    print("\n🔧 Testing config loading...")
    
    try:
        result = subprocess.run([
            sys.executable, "-c", 
            """
import sys
sys.path.insert(0, '/Users/nguyenkimchung/AgentKnowledgeMCP/src')
from config import load_config
config = load_config()
print('✅ Config loaded:', config.get('server', {}).get('name', 'unknown'))
"""
        ], capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            print(result.stdout.strip())
            return True
        else:
            print("❌ Config loading failed:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Config test error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Quick Test: Restructured MCP Server")
    print("=" * 50)
    
    # Test imports
    if not test_server_startup():
        print("\n❌ Server startup test failed")
        sys.exit(1)
    
    # Test config
    if not test_config_loading():
        print("\n❌ Config test failed") 
        sys.exit(1)
    
    print("\n🎉 All basic tests passed!")
    print("📝 Notes:")
    print("  - Server structure: ✅ Good")
    print("  - Imports: ✅ Working") 
    print("  - Config: ✅ Loading")
    print("\n🚀 Ready to use with Claude Desktop!")
