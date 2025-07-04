#!/usr/bin/env python3
"""
Quick setup script for Elasticsearch MCP Server
"""
import json
import os
import sys
from pathlib import Path
import subprocess


def main():
    """Main setup function."""
    print("🚀 Elasticsearch MCP Server - Quick Setup")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Check if config exists
    config_path = Path("src/config.json")
    if not config_path.exists():
        print("\n📝 Creating configuration file...")
        
        # Get user's home directory for knowledge base
        home_dir = Path.home()
        knowledge_dir = home_dir / "knowledge-base"
        
        # Create config from example
        example_path = Path("src/config.json.example")
        if example_path.exists():
            with open(example_path) as f:
                config = json.load(f)
            
            # Update with user's directory
            config["security"]["allowed_base_directory"] = str(knowledge_dir)
            
            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)
            
            print(f"✅ Config created: {config_path}")
            print(f"📁 Knowledge base directory: {knowledge_dir}")
        else:
            print("❌ config.json.example not found")
            return
    
    # Create knowledge base directory
    config_path = Path("src/config.json")
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
        
        kb_dir = Path(config["security"]["allowed_base_directory"])
        if not kb_dir.exists():
            kb_dir.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created knowledge base directory: {kb_dir}")
    
    # Check dependencies
    print("\n📦 Checking dependencies...")
    try:
        import mcp
        print("✅ MCP library found")
    except ImportError:
        print("⚠️  MCP library not found, install with: pip install -r requirements.txt")
    
    # Test basic functionality
    print("\n🧪 Running basic tests...")
    try:
        result = subprocess.run([
            sys.executable, "test_file_paths.py"
        ], capture_output=True, text=True, cwd=".")
        
        if result.returncode == 0:
            print("✅ File operations test passed")
        else:
            print("⚠️  File operations test had issues")
    except FileNotFoundError:
        print("⚠️  Test files not found")
    
    # Setup instructions
    print("\n🎯 Next Steps:")
    print("\n1. Install dependencies:")
    print("   pip install -r requirements.txt")
    
    print("\n2. Configure your AI assistant:")
    print("   • Claude Desktop: Add to claude_desktop_config.json")
    print("   • Cursor: Add to settings.json")
    print("   • VS Code: Install MCP extension")
    print("   • Windsurf: Add to ~/.windsurf/config.json")
    
    print("\n3. Test the server:")
    print("   python3 src/server.py")
    
    print("\n4. See README.md for detailed configuration examples")
    
    print("\n🎉 Setup complete! Ready to enhance your AI assistant with powerful knowledge management!")


if __name__ == "__main__":
    main()
