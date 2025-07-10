#!/usr/bin/env python3
"""
Test intelligent_config_merge function standalone
"""
import json

def intelligent_config_merge(current_config, backup_config):
    """
    Intelligently merge configuration after server upgrade.
    
    Logic:
    - Keep new features from current_config (new keys in current)
    - Restore user settings from backup_config (existing keys in both)  
    - Ignore deprecated features (keys only in backup - these were removed)
    
    Args:
        current_config: New configuration from server upgrade
        backup_config: User's previous configuration (backup)
        
    Returns:
        Merged configuration with user settings preserved and new features added
    """
    def merge_recursive(current, backup):
        result = current.copy()  # Start with current config (includes new features)
        
        for key, backup_value in backup.items():
            if key in current:
                # Key exists in both - restore user setting
                current_value = current[key]
                if isinstance(current_value, dict) and isinstance(backup_value, dict):
                    # Recursively merge nested dictionaries
                    result[key] = merge_recursive(current_value, backup_value)
                else:
                    # Use backup value (user's setting)
                    result[key] = backup_value
            # If key only exists in backup, ignore it (deprecated key)
            
        return result
    
    return merge_recursive(current_config, backup_config)


def test_intelligent_merge():
    """Test intelligent configuration merge algorithm"""
    print("🧪 Testing intelligent_config_merge function...")
    
    # Test Case 1: Basic merge with new features and user settings
    print("\n📋 Test Case 1: Basic merge")
    
    current_config = {
        "security": {
            "allowed_base_directory": "/default/path"
        },
        "elasticsearch": {
            "host": "localhost",
            "port": 9200,
            "new_feature": "enabled"  # New feature in upgrade
        },
        "server": {
            "version": "1.0.21",
            "new_setting": "default"  # New setting in upgrade
        }
    }
    
    backup_config = {
        "security": {
            "allowed_base_directory": "/custom/user/path"  # User's setting
        },
        "elasticsearch": {
            "host": "custom-host",  # User's setting
            "port": 9300,  # User's setting
            "old_deprecated": "should_be_ignored"  # Deprecated - only in backup
        },
        "server": {
            "version": "1.0.20"  # Old version
        }
    }
    
    result = intelligent_config_merge(current_config, backup_config)
    
    print(f"   Current (new): {json.dumps(current_config, indent=2)}")
    print(f"   Backup (user): {json.dumps(backup_config, indent=2)}")
    print(f"   Result (merged): {json.dumps(result, indent=2)}")
    
    # Verify key aspects
    checks = [
        (result["security"]["allowed_base_directory"] == "/custom/user/path", "User's directory preserved"),
        (result["elasticsearch"]["host"] == "custom-host", "User's elasticsearch host preserved"),
        (result["elasticsearch"]["port"] == 9300, "User's elasticsearch port preserved"),
        (result["elasticsearch"]["new_feature"] == "enabled", "New feature included"),
        (result["server"]["new_setting"] == "default", "New setting included"),
        ("old_deprecated" not in result["elasticsearch"], "Deprecated setting ignored"),
    ]
    
    for check_passed, description in checks:
        status = "✅" if check_passed else "❌"
        print(f"   {status} {description}")
    
    # Test Case 2: Nested merge
    print("\n📋 Test Case 2: Nested configuration merge")
    
    current_nested = {
        "level1": {
            "level2": {
                "setting1": "default1",
                "setting2": "default2",
                "new_setting": "new_value"
            }
        }
    }
    
    backup_nested = {
        "level1": {
            "level2": {
                "setting1": "user1",
                "deprecated_setting": "old_value"
            }
        }
    }
    
    result_nested = intelligent_config_merge(current_nested, backup_nested)
    
    print(f"   Result nested: {json.dumps(result_nested, indent=2)}")
    
    nested_checks = [
        (result_nested["level1"]["level2"]["setting1"] == "user1", "Nested user setting preserved"),
        (result_nested["level1"]["level2"]["setting2"] == "default2", "Nested new setting included"),
        (result_nested["level1"]["level2"]["new_setting"] == "new_value", "Nested new feature included"),
        ("deprecated_setting" not in result_nested["level1"]["level2"], "Nested deprecated setting ignored"),
    ]
    
    for check_passed, description in nested_checks:
        status = "✅" if check_passed else "❌"
        print(f"   {status} {description}")
    
    print("\n✅ Intelligent merge algorithm test completed!")

if __name__ == "__main__":
    test_intelligent_merge()
