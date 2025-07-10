#!/usr/bin/env python3
"""
Test reset_config tool functionality
"""
import json
import tempfile
from pathlib import Path
import sys
import os
import time
import asyncio

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from admin_handlers import handle_reset_config

async def test_reset_config():
    """Test reset_config tool functionality"""
    print("🧪 Testing reset_config tool...")
    
    # Create temporary directory for test
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test default config
        default_config = {
            "security": {
                "allowed_base_directory": "/default/path"
            },
            "elasticsearch": {
                "host": "localhost",
                "port": 9200
            },
            "server": {
                "version": "1.0.21"
            }
        }
        
        default_config_path = temp_path / "config.default.json"
        with open(default_config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2)
        
        # Create test current config (different from default)
        current_config = {
            "security": {
                "allowed_base_directory": "/custom/user/path"
            },
            "elasticsearch": {
                "host": "custom-host",
                "port": 9300,
                "index": "custom-index"
            },
            "server": {
                "version": "1.0.21"
            }
        }
        
        config_path = temp_path / "config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(current_config, f, indent=2)
        
        # Mock the config path in admin_handlers
        original_file = getattr(handle_reset_config, '__globals__', {}).get('__file__')
        if original_file:
            handle_reset_config.__globals__['__file__'] = str(temp_path / "fake_module.py")
        
        print("   • Current config has custom settings")
        print("   • Default config exists")
        
        # Test reset_config
        try:
            result = await handle_reset_config({})
            
            # Check result
            if result and len(result) > 0:
                message = result[0].text
                print(f"   • Reset result: {message}")
                
                if "✅ Configuration reset to defaults successfully!" in message:
                    print("   ✅ Reset reported success")
                    
                    # Verify config was actually reset
                    with open(config_path, 'r', encoding='utf-8') as f:
                        reset_config = json.load(f)
                    
                    if reset_config == default_config:
                        print("   ✅ Config successfully reset to defaults")
                    else:
                        print("   ❌ Config not properly reset")
                        print(f"   Expected: {default_config}")
                        print(f"   Got: {reset_config}")
                    
                    # Check if backup was created
                    backup_files = list(temp_path.glob("config.backup.*.json"))
                    if backup_files:
                        print(f"   ✅ Backup created: {backup_files[0].name}")
                        
                        # Verify backup contains original config
                        with open(backup_files[0], 'r', encoding='utf-8') as f:
                            backup_config = json.load(f)
                        
                        if backup_config == current_config:
                            print("   ✅ Backup contains original config")
                        else:
                            print("   ❌ Backup doesn't match original config")
                    else:
                        print("   ❌ No backup file created")
                        
                else:
                    print(f"   ❌ Reset failed: {message}")
            else:
                print("   ❌ No result returned")
                
        except Exception as e:
            print(f"   ❌ Exception during reset: {e}")
        finally:
            # Restore original __file__ if we modified it
            if original_file:
                handle_reset_config.__globals__['__file__'] = original_file

if __name__ == "__main__":
    asyncio.run(test_reset_config())
