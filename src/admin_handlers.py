"""
Admin tool handlers.
"""
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any

import mcp.types as types
from .config import load_config
from .security import get_allowed_base_dir, set_allowed_base_dir, init_security
from .elasticsearch_client import reset_es_client, init_elasticsearch
from .elasticsearch_setup import auto_setup_elasticsearch, ElasticsearchSetup


async def handle_get_config(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle get_config tool."""
    try:
        config = load_config()
        config_str = json.dumps(config, indent=2, ensure_ascii=False)
        
        return [
            types.TextContent(
                type="text",
                text=f"📄 Current configuration:\n\n```json\n{config_str}\n```"
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"Error getting configuration: {str(e)}"
            )
        ]


async def handle_update_config(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle update_config tool."""
    try:
        config_section = arguments.get("config_section")
        config_key = arguments.get("config_key") 
        config_value = arguments.get("config_value")
        full_config = arguments.get("full_config")
        
        config_path = Path(__file__).parent / "config.json"
        
        if full_config:
            # Update entire config
            if isinstance(full_config, str):
                new_config = json.loads(full_config)
            else:
                new_config = full_config
                
            # Validate new config structure
            required_sections = ["elasticsearch", "security", "document_validation", "version_control", "server"]
            for section in required_sections:
                if section not in new_config:
                    return [
                        types.TextContent(
                            type="text",
                            text=f"❌ Error: Missing required config section '{section}'"
                        )
                    ]
            
            # Write new config
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(new_config, f, indent=2, ensure_ascii=False)
                
            message = "✅ Full configuration updated successfully!"
            
        elif config_section and config_key is not None:
            # Update specific key
            config = load_config()
            
            if config_section not in config:
                return [
                    types.TextContent(
                        type="text",
                        text=f"❌ Error: Config section '{config_section}' not found"
                    )
                ]
            
            # Store old value for comparison
            old_value = config[config_section].get(config_key, "<not set>")
            
            # Update the value
            config[config_section][config_key] = config_value
            
            # Write updated config
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
            message = f"✅ Configuration updated successfully!\n"
            message += f"Section: {config_section}\n"
            message += f"Key: {config_key}\n"
            message += f"Old value: {old_value}\n"
            message += f"New value: {config_value}"
            
        else:
            return [
                types.TextContent(
                    type="text",
                    text="❌ Error: Must provide either 'full_config' or both 'config_section' and 'config_key'"
                )
            ]
        
        # Reload configuration in current session
        new_config = load_config()
        
        # Reinitialize security if security section was updated
        if (config_section == "security" and config_key == "allowed_base_directory") or full_config:
            init_security(new_config["security"]["allowed_base_directory"])
        
        # Reinitialize Elasticsearch if elasticsearch section was updated
        if (config_section == "elasticsearch") or full_config:
            init_elasticsearch(new_config)
            reset_es_client()
        
        return [
            types.TextContent(
                type="text",
                text=message + f"\n\n💡 Configuration reloaded automatically."
            )
        ]
        
    except json.JSONDecodeError as e:
        return [
            types.TextContent(
                type="text",
                text=f"❌ Error: Invalid JSON format in full_config: {str(e)}"
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"❌ Error updating configuration: {str(e)}"
            )
        ]


async def handle_validate_config(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle validate_config tool."""
    try:
        config_data = arguments.get("config_data")
        
        if isinstance(config_data, str):
            config = json.loads(config_data)
        else:
            config = config_data or load_config()
        
        errors = []
        warnings = []
        
        # Validate structure
        required_sections = ["elasticsearch", "security", "document_validation", "document_schema", "version_control", "server"]
        for section in required_sections:
            if section not in config:
                errors.append(f"Missing required section: {section}")
        
        # Validate elasticsearch section
        if "elasticsearch" in config:
            es_config = config["elasticsearch"]
            if "host" not in es_config:
                errors.append("elasticsearch.host is required")
            if "port" not in es_config:
                errors.append("elasticsearch.port is required")
            elif not isinstance(es_config["port"], int):
                errors.append("elasticsearch.port must be an integer")
        
        # Validate security section
        if "security" in config:
            sec_config = config["security"]
            if "allowed_base_directory" not in sec_config:
                errors.append("security.allowed_base_directory is required")
            else:
                base_dir = Path(sec_config["allowed_base_directory"])
                if not base_dir.exists():
                    warnings.append(f"security.allowed_base_directory does not exist: {base_dir}")
        
        # Validate document_validation section
        if "document_validation" in config:
            doc_config = config["document_validation"]
            bool_fields = ["strict_schema_validation", "allow_extra_fields", "required_fields_only", "auto_correct_paths"]
            for field in bool_fields:
                if field in doc_config and not isinstance(doc_config[field], bool):
                    errors.append(f"document_validation.{field} must be a boolean")
            
            # Validate content limits
            int_fields = ["content_max_length", "content_max_lines"]
            for field in int_fields:
                if field in doc_config:
                    if not isinstance(doc_config[field], int):
                        errors.append(f"document_validation.{field} must be an integer")
                    elif doc_config[field] <= 0:
                        errors.append(f"document_validation.{field} must be positive")
        
        # Validate document_schema section
        if "document_schema" in config:
            schema_config = config["document_schema"]
            required_schema_fields = ["required_fields", "field_types", "priority_values", "source_types"]
            for field in required_schema_fields:
                if field not in schema_config:
                    errors.append(f"document_schema.{field} is required")
                    
            # Validate required_fields is a list
            if "required_fields" in schema_config and not isinstance(schema_config["required_fields"], list):
                errors.append("document_schema.required_fields must be a list")
                
            # Validate field_types is a dict
            if "field_types" in schema_config and not isinstance(schema_config["field_types"], dict):
                errors.append("document_schema.field_types must be a dictionary")
                
            # Validate priority_values is a list
            if "priority_values" in schema_config and not isinstance(schema_config["priority_values"], list):
                errors.append("document_schema.priority_values must be a list")
                
            # Validate source_types is a list
            if "source_types" in schema_config and not isinstance(schema_config["source_types"], list):
                errors.append("document_schema.source_types must be a list")
        
        # Validate version_control section
        if "version_control" in config:
            vc_config = config["version_control"]
            if "enabled" in vc_config and not isinstance(vc_config["enabled"], bool):
                errors.append("version_control.enabled must be a boolean")
            if "type" in vc_config and vc_config["type"] not in ["git", "svn"]:
                errors.append("version_control.type must be 'git' or 'svn'")
        
        # Prepare result message
        if errors:
            message = f"❌ Configuration validation failed!\n\nErrors:\n"
            for error in errors:
                message += f"  • {error}\n"
        else:
            message = "✅ Configuration validation passed!"
        
        if warnings:
            message += f"\n⚠️  Warnings:\n"
            for warning in warnings:
                message += f"  • {warning}\n"
        
        # Show current validation settings
        if "document_validation" in config:
            doc_val = config["document_validation"]
            message += f"\n📋 Current document validation settings:\n"
            message += f"  • Strict schema validation: {doc_val.get('strict_schema_validation', False)}\n"
            message += f"  • Allow extra fields: {doc_val.get('allow_extra_fields', True)}\n"
            message += f"  • Required fields only: {doc_val.get('required_fields_only', False)}\n"
            message += f"  • Auto correct paths: {doc_val.get('auto_correct_paths', True)}\n"
        
        return [
            types.TextContent(
                type="text",
                text=message
            )
        ]
        
    except json.JSONDecodeError as e:
        return [
            types.TextContent(
                type="text",
                text=f"❌ Error: Invalid JSON format: {str(e)}"
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"❌ Error validating configuration: {str(e)}"
            )
        ]


# Keep backward compatibility
async def handle_get_allowed_directory(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle get_allowed_directory tool (deprecated - use get_config instead)."""
    return [
        types.TextContent(
            type="text",
            text=f"⚠️  Note: This tool is deprecated. Use 'get_config' instead.\n\nCurrent allowed base directory: {get_allowed_base_dir()}"
        )
    ]


async def handle_set_allowed_directory(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle set_allowed_directory tool (deprecated - use update_config instead)."""
    directory_path = arguments.get("directory_path")
    
    try:
        new_path = Path(directory_path).resolve()
        
        if not new_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        if not new_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {directory_path}")
        
        # Use the new update_config approach
        result = await handle_update_config({
            "config_section": "security",
            "config_key": "allowed_base_directory",
            "config_value": str(new_path)
        })
        
        return [
            types.TextContent(
                type="text",
                text=f"⚠️  Note: This tool is deprecated. Use 'update_config' instead.\n\n{result[0].text}"
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"❌ Error setting allowed directory to '{directory_path}': {str(e)}\n\n💡 Consider using 'update_config' tool instead."
            )
        ]


async def handle_reload_config(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle reload_config tool."""
    try:
        # Reload configuration
        config = load_config()
        
        # Reinitialize security with new allowed directory
        init_security(config["security"]["allowed_base_directory"])
        
        # Reinitialize Elasticsearch with new config
        init_elasticsearch(config)
        reset_es_client()
        
        return [
            types.TextContent(
                type="text",
                text=f"Configuration reloaded successfully.\nNew allowed directory: {get_allowed_base_dir()}\nElasticsearch: {config['elasticsearch']['host']}:{config['elasticsearch']['port']}"
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"Error reloading configuration: {str(e)}"
            )
        ]


async def handle_setup_elasticsearch(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle setup_elasticsearch tool."""
    try:
        include_kibana = arguments.get("include_kibana", True)
        force_recreate = arguments.get("force_recreate", False)
        
        # Get config path
        config_path = Path(__file__).parent / "config.json"
        config = load_config()
        
        if force_recreate:
            # Stop existing containers first
            setup = ElasticsearchSetup(config_path)
            stop_result = setup.stop_containers()
            
            # Wait a bit for containers to stop
            import time
            time.sleep(5)
        
        # Run auto setup
        result = auto_setup_elasticsearch(config_path, config)
        
        if result["status"] == "already_configured":
            return [
                types.TextContent(
                    type="text",
                    text=f"✅ Elasticsearch is already configured and running at {result['host']}:{result['port']}"
                )
            ]
        elif result["status"] == "setup_completed":
            es_info = result["elasticsearch"]
            kibana_info = result.get("kibana")
            
            message = f"🎉 Elasticsearch setup completed!\n"
            message += f"📍 Elasticsearch: http://{es_info['host']}:{es_info['port']}\n"
            
            if kibana_info and kibana_info.get("status") in ["running", "already_running"]:
                message += f"📊 Kibana: http://{kibana_info['host']}:{kibana_info['port']}\n"
            elif kibana_info and "error" in kibana_info:
                message += f"⚠️  Kibana setup failed: {kibana_info['error']}\n"
            
            message += "\n💡 Configuration has been updated automatically."
            
            # Reload configuration in current session
            new_config = load_config()
            init_elasticsearch(new_config)
            reset_es_client()
            
            return [
                types.TextContent(
                    type="text",
                    text=message
                )
            ]
        else:
            error_msg = result.get("error", "Unknown error")
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ Failed to setup Elasticsearch: {error_msg}"
                )
            ]
            
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"Error setting up Elasticsearch: {str(e)}"
            )
        ]


async def handle_elasticsearch_status(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle elasticsearch_status tool."""
    try:
        config_path = Path(__file__).parent / "config.json"
        setup = ElasticsearchSetup(config_path)
        
        status = setup.get_container_status()
        
        if "error" in status:
            return [
                types.TextContent(
                    type="text",
                    text=f"Error checking container status: {status['error']}"
                )
            ]
        
        message = "📊 Elasticsearch & Kibana Container Status:\n\n"
        
        # Elasticsearch status
        es_status = status["elasticsearch"]
        message += f"🔍 Elasticsearch ({es_status['container_name']}):\n"
        message += f"  - Exists: {'✅' if es_status['exists'] else '❌'}\n"
        message += f"  - Running: {'✅' if es_status['running'] else '❌'}\n"
        
        if es_status['running']:
            message += f"  - URL: http://localhost:9200\n"
        
        message += "\n"
        
        # Kibana status
        kibana_status = status["kibana"]
        message += f"📊 Kibana ({kibana_status['container_name']}):\n"
        message += f"  - Exists: {'✅' if kibana_status['exists'] else '❌'}\n"
        message += f"  - Running: {'✅' if kibana_status['running'] else '❌'}\n"
        
        if kibana_status['running']:
            message += f"  - URL: http://localhost:5601\n"
        
        # Current config
        config = load_config()
        message += f"\n⚙️ Current Configuration:\n"
        message += f"  - Host: {config['elasticsearch']['host']}\n"
        message += f"  - Port: {config['elasticsearch']['port']}\n"
        
        return [
            types.TextContent(
                type="text",
                text=message
            )
        ]
        
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"Error checking Elasticsearch status: {str(e)}"
            )
        ]


async def handle_server_status(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle server_status tool - check server status, version and updates."""
    try:
        check_updates = arguments.get("check_updates", True)
        
        # Get current version
        current_version = "unknown"
        try:
            # When running from uvx package, use standard import
            try:
                import importlib.metadata
                current_version = importlib.metadata.version("agent-knowledge-mcp")
            except:
                # Fallback to local import (for development)
                try:
                    from . import __version__ as current_version
                except ImportError:
                    try:
                        from src import __version__ as current_version
                    except ImportError:
                        # Last resort - fallback
                        pass
        except Exception:
            pass
        
        # Get server status
        config = load_config()
        server_status = "running"
        
        # Check installation method
        installation_method = "unknown"
        try:
            # Check if installed via uvx
            result = subprocess.run(
                ["uv", "tool", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0 and "agent-knowledge-mcp" in result.stdout:
                installation_method = "uvx"
        except:
            pass
        
        # Check for updates if requested
        latest_version = None
        update_available = False
        recommendation = ""
        
        if check_updates and installation_method == "uvx":
            try:
                import requests
                response = requests.get(
                    "https://pypi.org/pypi/agent-knowledge-mcp/json",
                    timeout=5
                )
                if response.status_code == 200:
                    data = response.json()
                    latest_version = data["info"]["version"]
                    
                    # Simple version comparison (works for semver)
                    if latest_version != current_version:
                        update_available = True
                        recommendation = f"🔄 New version {latest_version} available! Use 'server_upgrade' to update."
            except Exception as e:
                latest_version = f"Error checking: {str(e)}"
        
        # Build status message
        message = f"🖥️  Server Status Report:\n\n"
        message += f"📍 Current Version: {current_version}\n"
        
        if latest_version:
            message += f"📦 Latest Version: {latest_version}\n"
        
        message += f"🔧 Installation Method: {installation_method}\n"
        message += f"⚡ Server Status: {server_status}\n"
        message += f"🗂️  Elasticsearch: {config['elasticsearch']['host']}:{config['elasticsearch']['port']}\n"
        
        if update_available:
            message += f"\n✨ {recommendation}\n"
        elif check_updates and latest_version and not update_available:
            message += f"\n✅ You are running the latest version!\n"
        
        if installation_method != "uvx":
            message += f"\n💡 Note: Server management tools only work with uvx installation.\n"
            message += f"   Install via: uvx install agent-knowledge-mcp\n"
        
        return [
            types.TextContent(
                type="text",
                text=message
            )
        ]
        
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"❌ Error checking server status: {str(e)}"
            )
        ]


async def handle_server_upgrade(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle server_upgrade tool - backup config, upgrade server, and restore settings automatically."""
    try:
        # Check if uv is available
        try:
            subprocess.run(["uv", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return [
                types.TextContent(
                    type="text",
                    text="❌ Error: uv is not installed or not available in PATH.\n\n"
                         "Please install uv first."
                )
            ]
        
        # Check if this package is installed via uvx
        try:
            list_result = subprocess.run(
                ["uv", "tool", "list"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if "agent-knowledge-mcp" not in list_result.stdout:
                return [
                    types.TextContent(
                        type="text",
                        text="⚠️ Agent Knowledge MCP server is not installed via uv tool.\n\n"
                             "This tool only works when the server was installed using:\n"
                             "uv tool install agent-knowledge-mcp\n\n"
                             f"Current uv tool packages:\n{list_result.stdout.strip() or 'None'}"
                    )
                ]
        except:
            return [
                types.TextContent(
                    type="text",
                    text="⚠️ Cannot verify uvx installation. Please ensure agent-knowledge-mcp is installed via uvx."
                )
            ]
        
        # Step 1: Backup current configuration
        config_path = Path(__file__).parent / "config.json"
        backup_config = None
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    backup_config = json.load(f)
                print("✅ Configuration backed up for restoration")
            except Exception as e:
                print(f"⚠️ Warning: Could not backup config: {e}")
        else:
            print("ℹ️ No existing config.json to backup")
        
        # Get the latest version from PyPI first
        latest_version = None
        try:
            import requests
            response = requests.get(
                "https://pypi.org/pypi/agent-knowledge-mcp/json",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                latest_version = data["info"]["version"]
        except Exception as e:
            print(f"Warning: Could not fetch latest version: {e}")
        
        # Clean UV cache first
        print("Cleaning UV cache...")
        cache_result = subprocess.run(
            ["uv", "cache", "clean"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if cache_result.returncode != 0:
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ Failed to clean UV cache:\n{cache_result.stderr.strip() or 'Unknown error'}"
                )
            ]
        
        # Force reinstall with specific version if available
        if latest_version:
            print(f"Force installing agent-knowledge-mcp=={latest_version}...")
            install_cmd = ["uv", "tool", "install", f"agent-knowledge-mcp=={latest_version}", "--force"]
            
            result = subprocess.run(
                install_cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            # If specific version fails, try without version constraint
            if result.returncode != 0:
                print(f"Specific version failed, trying latest available...")
                install_cmd = ["uv", "tool", "install", "agent-knowledge-mcp", "--force"]
                result = subprocess.run(
                    install_cmd,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
        else:
            print("Force installing latest agent-knowledge-mcp...")
            install_cmd = ["uv", "tool", "install", "agent-knowledge-mcp", "--force"]
            result = subprocess.run(
                install_cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
        
        if result.returncode == 0:
            # Parse installation output to check if upgrade happened
            output = result.stdout.strip()
            upgrade_detected = False
            installed_version = "unknown"
            
            # Look for upgrade indicators in output
            if "+" in output and "agent-knowledge-mcp" in output:
                for line in output.split('\n'):
                    if line.strip().startswith('+ agent-knowledge-mcp=='):
                        installed_version = line.split('==')[1].strip()
                        upgrade_detected = True
                        break
                    elif line.strip().startswith('- agent-knowledge-mcp==') and '+ agent-knowledge-mcp==' in output:
                        upgrade_detected = True
            
            if upgrade_detected:
                message = f"🎉 Agent Knowledge MCP server upgraded successfully!\n\n"
                if installed_version != "unknown":
                    message += f"📦 Installed version: {installed_version}\n\n"
            else:
                message = f"🔄 Agent Knowledge MCP server reinstalled successfully!\n\n"
            
            # Step 3: Restore configuration intelligently
            config_restored = False
            if backup_config:
                try:
                    # Check if config.json exists after upgrade (it should)
                    if config_path.exists():
                        # Load new config from upgrade
                        with open(config_path, 'r', encoding='utf-8') as f:
                            new_config = json.load(f)
                        
                        # Perform intelligent merge
                        merged_config = intelligent_config_merge(new_config, backup_config)
                        
                        # Write merged config back
                        with open(config_path, 'w', encoding='utf-8') as f:
                            json.dump(merged_config, f, indent=2, ensure_ascii=False)
                        
                        # Reload configuration after restore
                        config = load_config()
                        
                        # Reinitialize components with restored config
                        init_security(config["security"]["allowed_base_directory"])
                        init_elasticsearch(config)
                        reset_es_client()
                        
                        config_restored = True
                        message += "🔧 Configuration automatically restored with intelligent merge!\n"
                        message += "   • Your custom settings preserved\n"
                        message += "   • New features from upgrade included\n"
                        message += "   • Deprecated settings removed\n\n"
                    else:
                        message += "⚠️ New config.json not found after upgrade\n\n"
                        
                except Exception as e:
                    message += f"⚠️ Warning: Could not restore configuration: {e}\n"
                    message += "💡 Use 'get_config' to review and 'update_config' to customize\n\n"
            
            if not config_restored and not backup_config:
                message += "ℹ️ No previous configuration to restore\n\n"
            
            message += f"🔄 Please restart your MCP client to use the updated version:\n\n"
            message += f"   • VS Code: Reload window (Ctrl/Cmd + Shift + P → 'Reload Window')\n"
            message += f"   • Claude Desktop: Restart the application\n"
            message += f"   • Other clients: Restart/reload the client\n\n"
            
            if output:
                message += f"Installation output:\n{output}\n\n"
            
            message += f"✅ Installation completed! Restart your client to use the latest version."
            
            return [
                types.TextContent(
                    type="text",
                    text=message
                )
            ]
        else:
            error_msg = f"❌ Failed to install/upgrade agent-knowledge-mcp\n\n"
            error_msg += f"Return code: {result.returncode}\n"
            if result.stderr.strip():
                error_msg += f"Error output:\n{result.stderr.strip()}\n"
            if result.stdout.strip():
                error_msg += f"Standard output:\n{result.stdout.strip()}\n"
            
            error_msg += f"\n💡 You can manually run:\n"
            error_msg += f"   uv cache clean && uv tool install agent-knowledge-mcp --force"
            
            return [
                types.TextContent(
                    type="text",
                    text=error_msg
                )
            ]
            
    except subprocess.TimeoutExpired:
        return [
            types.TextContent(
                type="text",
                text="❌ Timeout: Cache clean took too long. Please try again."
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"❌ Error during upgrade process: {str(e)}\n\n"
                     f"💡 You can manually restart your MCP client to check for updates."
            )
        ]


async def handle_get_comprehensive_usage_guide(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle get_comprehensive_usage_guide tool."""
    try:
        section = arguments.get("section", "all")
        
        # Read guide content from markdown file
        guide_path = Path(__file__).parent / "comprehensive_usage_guide.md"
        
        if not guide_path.exists():
            return [
                types.TextContent(
                    type="text",
                    text="❌ Error: Comprehensive usage guide file not found. Please ensure 'comprehensive_usage_guide.md' exists in the src directory."
                )
            ]
        
        # Read the full guide content
        with open(guide_path, 'r', encoding='utf-8') as f:
            guide_content = f.read()
        
        # Filter by section if requested
        if section != "all":
            guide_content = extract_section_content(guide_content, section)
        
        return [
            types.TextContent(
                type="text",
                text=guide_content
            )
        ]
        
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"❌ Error getting comprehensive usage guide: {str(e)}"
            )
        ]


def extract_section_content(full_content: str, section: str) -> str:
    """Extract specific section from full guide content."""
    lines = full_content.split('\n')
    section_lines = []
    in_section = False
    
    # Section mappings
    section_headers = {
        "quick_start": "## 🚀 **Quick Start",
        "workflows": "## 📚 **Core Workflows",
        "advanced": "## ⚡ **Power Commands",
        "troubleshooting": "## 🔧 **Troubleshooting Guide", 
        "best_practices": "## 🎓 **Best Practices"
    }
    
    target_header = section_headers.get(section)
    if not target_header:
        return full_content  # Return full content if section not found
    
    # Always include the prompting instructions at the beginning
    prompt_instruction = """# 🚀 AgentKnowledgeMCP - Complete Usage Guide

## ⚡ **Before Getting Started - IMPORTANT!**

> 💡 **Pro Tip for Maximum Effectiveness**: 
> For the most effective experience with this MCP server, you should attach this instructions file to each prompt:
> 
> 📚 **https://github.com/itshare4u/AgentKnowledgeMCP/blob/main/.github/copilot-instructions.md**
> 
> This file contains guidelines that help AI assistants understand and use the MCP server optimally!

---

"""
    
    # Extract specific section
    for line in lines:
        if target_header in line:
            in_section = True
            section_lines.append(line)
        elif in_section and line.startswith('## ') and target_header not in line:
            break  # Stop when we reach the next section
        elif in_section:
            section_lines.append(line)
    
    if section_lines:
        return prompt_instruction + '\n'.join(section_lines)
    else:
        return full_content  # Return full content if section extraction fails


def intelligent_config_merge(current_config: Dict[str, Any], backup_config: Dict[str, Any]) -> Dict[str, Any]:
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
    
    def merge_recursive(current: Dict[str, Any], backup: Dict[str, Any], section_name: str = None) -> Dict[str, Any]:
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


async def handle_reset_config(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle reset_config tool - reset config.json to defaults from config.default.json."""
    try:
        config_path = Path(__file__).parent / "config.json"
        default_config_path = Path(__file__).parent / "config.default.json"
        
        # Check if config.default.json exists
        if not default_config_path.exists():
            return [
                types.TextContent(
                    type="text", 
                    text="❌ Default configuration file config.default.json not found.\n"
                         "💡 Cannot reset configuration without default template."
                )
            ]
        
        # Create backup of current config if it exists
        backup_created = False
        if config_path.exists():
            import time
            timestamp = int(time.time())
            backup_path = config_path.with_name(f"config.backup.{timestamp}.json")
            import shutil
            shutil.copy2(config_path, backup_path)
            backup_created = True
        
        # Copy config.default.json to config.json (overwrite)
        import shutil
        shutil.copy2(default_config_path, config_path)
        
        # Reload configuration after reset
        config = load_config()
        
        # Reinitialize components with reset config
        init_security(config["security"]["allowed_base_directory"])
        init_elasticsearch(config)
        reset_es_client()
        
        message = "✅ Configuration reset to defaults successfully!\n\n"
        if backup_created:
            message += f"📁 Previous configuration backed up as: {backup_path.name}\n\n"
        message += "🔄 All components reinitialized with default settings.\n"
        message += "💡 Use 'update_config' to customize settings as needed."
        
        return [
            types.TextContent(
                type="text",
                text=message
            )
        ]
        
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"❌ Error resetting configuration: {str(e)}\n\n"
                     "💡 You may need to manually copy config.default.json to config.json"
            )
        ]
