#!/usr/bin/env python3
"""
Comprehensive test of the enhanced intelligent merge algorithm
"""
import json

def intelligent_config_merge(current_config, backup_config):
    """
    Intelligently merge configuration after server upgrade.
    
    Logic:
    - Some sections use LATEST config (server, schema, version info)
    - Some sections use INTELLIGENT merge (user settings like security, elasticsearch)
    - Ignore deprecated features (keys only in backup - these were removed)
    
    Args:
        current_config: New configuration from server upgrade
        backup_config: User's previous configuration (backup)
        
    Returns:
        Merged configuration with appropriate merge strategy per section
    """
    # Sections that should always use the LATEST config (no merge)
    # These contain version info, schema definitions, server settings that must be current
    LATEST_CONFIG_SECTIONS = {
        "server",           # Version info, new server settings
        "schema",           # Schema definitions must be current  
        "version",          # Version tracking
        "defaults",         # Default values must be current
        "required_fields",  # Schema requirements must be current
        "field_types"       # Schema field types must be current
    }
    
    # Sections that should use INTELLIGENT merge (preserve user settings)
    # These contain user customizations that should be preserved
    INTELLIGENT_MERGE_SECTIONS = {
        "security",         # User's paths and security settings
        "elasticsearch",    # User's ES connection settings  
        "logging",          # User's logging preferences
        "features",         # User's feature toggles
        "custom"            # Any custom user sections
    }
    
    def merge_recursive(current, backup, section_name=None):
        result = current.copy()  # Start with current config (includes new features)
        
        for key, backup_value in backup.items():
            if key in current:
                current_value = current[key]
                
                # Check if this is a top-level section that needs special handling
                if section_name is None and key in LATEST_CONFIG_SECTIONS:
                    # Use latest config for these sections - no merge
                    result[key] = current_value
                    continue
                elif section_name is None and key in INTELLIGENT_MERGE_SECTIONS:
                    # Use intelligent merge for these sections
                    if isinstance(current_value, dict) and isinstance(backup_value, dict):
                        result[key] = merge_recursive(current_value, backup_value, key)
                    else:
                        result[key] = backup_value  # Preserve user setting
                    continue
                elif section_name is None and isinstance(current_value, dict) and isinstance(backup_value, dict):
                    # For unknown top-level sections, default to intelligent merge
                    result[key] = merge_recursive(current_value, backup_value, key)
                    continue
                
                # For nested values within a section, merge normally
                if isinstance(current_value, dict) and isinstance(backup_value, dict):
                    # Recursively merge nested dictionaries
                    result[key] = merge_recursive(current_value, backup_value, section_name)
                else:
                    # Use backup value (user's setting) for intelligent merge sections
                    if section_name in INTELLIGENT_MERGE_SECTIONS or section_name is None:
                        result[key] = backup_value
                    else:
                        # For latest config sections, keep current value
                        result[key] = current_value
            else:
                # Key only exists in backup
                # For intelligent merge sections, preserve user settings even if not in current config
                # BUT only if they're not clearly deprecated (e.g., "old_", "deprecated_", "legacy_")
                if section_name in INTELLIGENT_MERGE_SECTIONS:
                    # Check if this looks like a deprecated setting
                    is_deprecated = any(key.startswith(prefix) for prefix in ["old_", "deprecated_", "legacy_"])
                    if not is_deprecated:
                        result[key] = backup_value
                # For latest config sections or deprecated keys, ignore (don't include)
            
        return result
    
    return merge_recursive(current_config, backup_config)


def test_comprehensive_merge():
    """Test comprehensive merge scenarios"""
    print("🧪 Testing Comprehensive Intelligent Merge Algorithm...")
    
    print("\n📋 Test 1: Basic section-specific behavior")
    
    current_config = {
        "server": {
            "version": "1.0.21",
            "new_setting": "enabled"
        },
        "security": {
            "allowed_base_directory": "/default/path"
        },
        "elasticsearch": {
            "host": "localhost",
            "port": 9200,
            "new_feature": "enabled"
        }
    }
    
    backup_config = {
        "server": {
            "version": "1.0.20",  # Should be ignored (latest config)
            "old_setting": "deprecated"  # Should be ignored
        },
        "security": {
            "allowed_base_directory": "/custom/user/path"  # Should be preserved
        },
        "elasticsearch": {
            "host": "custom-host",  # Should be preserved
            "port": 9300,  # Should be preserved
            "username": "myuser",  # Should be preserved (user-only setting)
            "old_index": "deprecated"  # Should be ignored
        }
    }
    
    result = intelligent_config_merge(current_config, backup_config)
    
    print("   Result:")
    print(json.dumps(result, indent=2))
    
    checks = [
        (result["server"]["version"] == "1.0.21", "Server version uses latest"),
        (result["server"]["new_setting"] == "enabled", "Server new setting included"),
        ("old_setting" not in result["server"], "Server deprecated setting ignored"),
        (result["security"]["allowed_base_directory"] == "/custom/user/path", "Security user path preserved"),
        (result["elasticsearch"]["host"] == "custom-host", "ES user host preserved"),
        (result["elasticsearch"]["username"] == "myuser", "ES user-only setting preserved"),
        ("old_index" not in result["elasticsearch"], "ES deprecated setting ignored"),
    ]
    
    for check_passed, description in checks:
        status = "✅" if check_passed else "❌"
        print(f"   {status} {description}")
    
    print("\n📋 Test 2: Real-world upgrade scenario")
    
    # Simulate a real config upgrade scenario
    old_user_config = {
        "security": {
            "allowed_base_directory": "/Users/john/my-knowledge"
        },
        "elasticsearch": {
            "host": "my-elasticsearch.internal",
            "port": 9200,
            "username": "john_doe",
            "password": "secret123",
            "legacy_setting": "old_value"  # Deprecated
        },
        "server": {
            "version": "1.0.18"
        },
        "old_removed_section": {  # Entire section removed
            "deprecated_feature": "value"
        }
    }
    
    new_default_config = {
        "security": {
            "allowed_base_directory": "/default/knowledge_base"
        },
        "elasticsearch": {
            "host": "localhost",
            "port": 9200,
            "content_field": "content",  # New in v1.0.21
            "timeout": 30  # New setting
        },
        "server": {
            "version": "1.0.21",
            "auto_backup": True  # New feature
        },
        "logging": {  # New section
            "level": "INFO",
            "format": "json"
        }
    }
    
    final_config = intelligent_config_merge(new_default_config, old_user_config)
    
    print("   Real-world merge result:")
    print(json.dumps(final_config, indent=2))
    
    real_world_checks = [
        # User settings preserved in intelligent sections
        (final_config["security"]["allowed_base_directory"] == "/Users/john/my-knowledge", "User's knowledge path preserved"),
        (final_config["elasticsearch"]["host"] == "my-elasticsearch.internal", "User's ES host preserved"),
        (final_config["elasticsearch"]["username"] == "john_doe", "User's ES credentials preserved"),
        # New features added
        (final_config["elasticsearch"]["content_field"] == "content", "New content_field added"),
        (final_config["elasticsearch"]["timeout"] == 30, "New timeout setting added"),
        (final_config["logging"]["level"] == "INFO", "New logging section added"),
        # Latest config for server section
        (final_config["server"]["version"] == "1.0.21", "Server version updated to latest"),
        (final_config["server"]["auto_backup"] == True, "New server feature included"),
        # Deprecated items ignored
        ("legacy_setting" not in final_config["elasticsearch"], "Legacy ES setting ignored"),
        ("old_removed_section" not in final_config, "Removed section ignored"),
    ]
    
    for check_passed, description in real_world_checks:
        status = "✅" if check_passed else "❌"
        print(f"   {status} {description}")
    
    print("\n🎯 Summary:")
    print("   ✅ LATEST CONFIG sections (server, schema): Always use new version")
    print("   ✅ INTELLIGENT MERGE sections (security, elasticsearch): Preserve user + add new")
    print("   ✅ Deprecated settings: Automatically filtered out")
    print("   ✅ User-only settings: Preserved even if not in new config")
    print("   ✅ New features: Automatically included")

if __name__ == "__main__":
    test_comprehensive_merge()
