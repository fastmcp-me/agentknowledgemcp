#!/usr/bin/env python3
"""
Test Elasticsearch configuration changes and verification.
"""
import sys
import os
import json
from pathlib import Path

def load_config():
    """Load current configuration."""
    config_path = Path(__file__).parent.parent / "src" / "config.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def update_config(new_settings):
    """Update configuration with new settings."""
    config_path = Path(__file__).parent.parent / "src" / "config.json"
    
    # Load current config
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Update elasticsearch settings
    config["elasticsearch"].update(new_settings)
    
    # Save updated config
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    return config

def test_config_change():
    """Test changing Elasticsearch configuration."""
    print("🧪 Testing Elasticsearch Configuration Changes")
    print("=" * 60)
    print()
    
    # Show current config
    print("📄 Current Configuration:")
    current_config = load_config()
    es_config = current_config["elasticsearch"]
    for key, value in es_config.items():
        print(f"  - {key}: {value}")
    print()
    
    # Test 1: Change port to simulate different Elasticsearch instance
    print("📋 Test 1: Changing Elasticsearch port")
    original_port = es_config["port"]
    print(f"   Original port: {original_port}")
    
    # Change to a different port
    new_port = 9201 if original_port == 9200 else 9200
    print(f"   Changing to port: {new_port}")
    
    updated_config = update_config({"port": new_port})
    print("   ✅ Config updated successfully")
    
    # Verify the change
    verify_config = load_config()
    if verify_config["elasticsearch"]["port"] == new_port:
        print(f"   ✅ Configuration verified: port is now {new_port}")
    else:
        print(f"   ❌ Configuration mismatch!")
    print()
    
    # Test 2: Change host
    print("📋 Test 2: Changing Elasticsearch host")
    original_host = es_config["host"]
    print(f"   Original host: {original_host}")
    
    # Change to a different host
    new_host = "127.0.0.1" if original_host == "localhost" else "localhost"
    print(f"   Changing to host: {new_host}")
    
    updated_config = update_config({"host": new_host})
    print("   ✅ Config updated successfully")
    
    # Verify the change
    verify_config = load_config()
    if verify_config["elasticsearch"]["host"] == new_host:
        print(f"   ✅ Configuration verified: host is now {new_host}")
    else:
        print(f"   ❌ Configuration mismatch!")
    print()
    
    # Test 3: Restore original configuration
    print("📋 Test 3: Restoring original configuration")
    print(f"   Restoring: host={original_host}, port={original_port}")
    
    restored_config = update_config({
        "host": original_host,
        "port": original_port
    })
    print("   ✅ Original config restored")
    
    # Final verification
    final_config = load_config()
    final_es = final_config["elasticsearch"]
    print()
    print("📄 Final Configuration:")
    for key, value in final_es.items():
        print(f"  - {key}: {value}")
    
    print()
    print("🎯 Configuration change tests completed!")
    print("💡 Elasticsearch settings can be dynamically updated")
    print("🔧 Changes are persisted to config.json")

if __name__ == "__main__":
    test_config_change()
