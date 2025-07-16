#!/usr/bin/env python3
"""
Simple test script for composed FastMCP server.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.composed_server import app
    print("✅ Composed server imported successfully")
    print(f"Server name: {app.name}")
    print(f"Server version: {app.version}")
    print("🎉 Basic test passed!")
    
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)
