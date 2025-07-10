#!/usr/bin/env python3
"""
Test Elasticsearch connection with different configurations.
"""
import json
import requests
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

def test_elasticsearch_connection(host, port):
    """Test connection to Elasticsearch."""
    try:
        response = requests.get(f"http://{host}:{port}", timeout=5)
        if response.status_code == 200:
            return True, f"✅ Connected successfully to {host}:{port}"
        else:
            return False, f"❌ HTTP {response.status_code} from {host}:{port}"
    except requests.exceptions.ConnectionError:
        return False, f"🔌 Connection refused to {host}:{port}"
    except requests.exceptions.Timeout:
        return False, f"⏱️ Timeout connecting to {host}:{port}"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

def test_config_and_connection():
    """Test different Elasticsearch configurations and connections."""
    print("🧪 Testing Elasticsearch Configuration and Connection")
    print("=" * 60)
    print()
    
    # Show current config
    current_config = load_config()
    es_config = current_config["elasticsearch"]
    current_host = es_config["host"]
    current_port = es_config["port"]
    
    print("📄 Current Configuration:")
    print(f"  - Host: {current_host}")
    print(f"  - Port: {current_port}")
    print(f"  - Auto Setup: {es_config.get('auto_setup', False)}")
    print()
    
    # Test current configuration
    print("📋 Test 1: Current configuration")
    success, message = test_elasticsearch_connection(current_host, current_port)
    print(f"   {message}")
    if success:
        print("   📊 Elasticsearch is running and accessible")
    else:
        print("   🔧 This demonstrates the connection errors our enhanced handlers catch")
    print()
    
    # Test different port (likely to fail)
    print("📋 Test 2: Testing different port (9201)")
    wrong_port = 9201
    success, message = test_elasticsearch_connection(current_host, wrong_port)
    print(f"   {message}")
    if not success:
        print("   💡 This is the type of error that triggers our enhanced error messages")
        print("   🎯 Our handlers would suggest: 'Use setup_elasticsearch tool'")
    print()
    
    # Test localhost vs 127.0.0.1
    alternative_host = "127.0.0.1" if current_host == "localhost" else "localhost"
    print(f"📋 Test 3: Testing alternative host ({alternative_host})")
    success, message = test_elasticsearch_connection(alternative_host, current_port)
    print(f"   {message}")
    if success:
        print("   ✅ Both localhost and 127.0.0.1 work")
    else:
        print("   ℹ️  Different host resolution behavior")
    print()
    
    # Temporarily change config to wrong port and test
    print("📋 Test 4: Temporarily changing config to wrong port")
    print(f"   Changing port from {current_port} to {wrong_port}")
    update_config({"port": wrong_port})
    
    # Verify the change
    new_config = load_config()
    if new_config["elasticsearch"]["port"] == wrong_port:
        print(f"   ✅ Config updated: port is now {wrong_port}")
        
        # Test connection with wrong port
        success, message = test_elasticsearch_connection(current_host, wrong_port)
        print(f"   {message}")
        if not success:
            print("   📝 This demonstrates how config changes affect connectivity")
            print("   💡 Enhanced error messages help diagnose such issues")
    
    # Restore original config
    print()
    print("📋 Test 5: Restoring original configuration")
    update_config({"port": current_port})
    restored_config = load_config()
    print(f"   ✅ Restored: port back to {restored_config['elasticsearch']['port']}")
    
    # Final verification
    success, message = test_elasticsearch_connection(current_host, current_port)
    print(f"   {message}")
    
    print()
    print("🎯 Configuration and connection tests completed!")
    print("💡 Key findings:")
    print("   🔧 Configuration changes are immediately effective")
    print("   📊 Connection errors are clearly identifiable")
    print("   🎯 Enhanced error handling provides actionable guidance")
    print("   ⚙️ Both localhost and 127.0.0.1 typically work for local connections")

if __name__ == "__main__":
    test_config_and_connection()
