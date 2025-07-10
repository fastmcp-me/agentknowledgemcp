#!/usr/bin/env python3
"""
Test Elasticsearch configuration changes without external dependencies.
"""
import json
import socket
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

def test_port_connection(host, port, timeout=3):
    """Test if a port is open using socket."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        if result == 0:
            return True, f"✅ Port {port} is open on {host}"
        else:
            return False, f"🔌 Port {port} is closed on {host}"
    except socket.gaierror:
        return False, f"❌ Cannot resolve hostname {host}"
    except Exception as e:
        return False, f"❌ Error testing {host}:{port} - {str(e)}"

def test_configuration_scenarios():
    """Test various Elasticsearch configuration scenarios."""
    print("🧪 Testing Elasticsearch Configuration Scenarios")
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
    print("📋 Test 1: Current configuration connectivity")
    success, message = test_port_connection(current_host, current_port)
    print(f"   {message}")
    if success:
        print("   📊 Elasticsearch port is reachable")
        print("   ✅ This means Elasticsearch is likely running")
    else:
        print("   🔧 Port not reachable - demonstrates connection error scenario")
        print("   💡 Our enhanced error messages would guide users to:")
        print("      🎯 Use 'setup_elasticsearch' tool")
        print("      ⚙️ Check configuration with 'get_config' tool")
    print()
    
    # Test common alternative ports
    test_ports = [9201, 9202, 9300]
    print("📋 Test 2: Testing alternative ports (likely to fail)")
    for test_port in test_ports:
        success, message = test_port_connection(current_host, test_port)
        print(f"   {message}")
        if not success:
            print(f"      💡 Connection to {test_port} failed - example of config mismatch")
    print()
    
    # Test host variations
    print("📋 Test 3: Testing host variations")
    test_hosts = ["localhost", "127.0.0.1"]
    for test_host in test_hosts:
        success, message = test_port_connection(test_host, current_port)
        print(f"   {message}")
        if success:
            print(f"      ✅ {test_host} resolves and port is reachable")
        else:
            print(f"      ℹ️  {test_host} connection failed")
    print()
    
    # Demonstrate config change impact
    print("📋 Test 4: Demonstrating configuration change impact")
    wrong_port = 9999
    print(f"   Temporarily changing port from {current_port} to {wrong_port}")
    
    # Save original for restoration
    original_config = current_config.copy()
    
    # Update to wrong port
    update_config({"port": wrong_port})
    updated_config = load_config()
    print(f"   ✅ Config updated: port is now {updated_config['elasticsearch']['port']}")
    
    # Test connection with wrong port
    success, message = test_port_connection(current_host, wrong_port)
    print(f"   {message}")
    if not success:
        print("   📝 This demonstrates how incorrect config causes connection failures")
        print("   🎯 Enhanced error handling helps identify such configuration issues")
    print()
    
    # Restore original config
    print("📋 Test 5: Restoring original configuration")
    update_config({"port": current_port})
    restored_config = load_config()
    print(f"   ✅ Restored: port back to {restored_config['elasticsearch']['port']}")
    
    # Verify restoration
    success, message = test_port_connection(current_host, current_port)
    print(f"   {message}")
    print()
    
    # Summary of error handling improvements
    print("🎯 Configuration Testing Summary:")
    print("💡 Key benefits of enhanced error handling:")
    print("   📊 Clear error categorization (Connection, Timeout, Index, etc.)")
    print("   📍 Specific problem identification")
    print("   💡 Actionable solutions with tool suggestions")
    print("   🔧 Guidance for configuration issues")
    print("   ⚙️ Help with Elasticsearch setup and troubleshooting")
    print()
    print("🔧 Error scenarios tested:")
    print("   🔌 Connection refused (port closed)")
    print("   ⚙️ Configuration mismatch (wrong port)")
    print("   🌐 Host resolution variations")
    print("   📝 Configuration persistence and restoration")

if __name__ == "__main__":
    test_configuration_scenarios()
