# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.9] - 2025-07-07

### Testing
- **Auto-Upgrade Feature Final Test**: Version bump to test complete auto-upgrade workflow with MCP server tools
  - Test server_status detecting version 1.0.8 vs latest 1.0.9
  - Test server_upgrade tool performing cache clean and instructing user reload
  - Validate end-to-end auto-upgrade experience using built-in MCP server tools

### Technical
- No functional changes, version bump for comprehensive auto-upgrade testing
- All auto-upgrade functionality ready for production use

## [1.0.8] - 2025-07-07

### Fixed
- **Server Upgrade Tool**: Fixed detection to use `uv tool list` instead of `uvx list`
  - Corrected package installation verification for modern uv tool workflow
  - Updated error messages to reference correct installation method
  - Enhanced compatibility with current uv tool ecosystem

### Technical
- All admin tools now properly support uv tool installation method
- Improved error handling and user guidance in server_upgrade tool

## [1.0.7] - 2025-07-07

### Testing
- **Auto-Upgrade Feature Test**: Version bump to test the complete auto-upgrade workflow
  - Test server_status tool detecting version mismatch
  - Test server_upgrade tool with cache cleaning and user instructions
  - Validate complete upgrade cycle: detect → clean → reload → verify

### Technical
- No functional changes, version bump for testing auto-upgrade feature
- All existing functionality remains unchanged

## [1.0.6] - 2025-07-07

### Fixed
- **Version Detection**: Fixed version detection in uvx environment for server_status tool
  - Enhanced `importlib.metadata` usage for proper package version detection
  - Improved import fallback logic for different runtime environments
  - Fixed installation method detection using correct `uv tool list` command
- **Auto-Upgrade Feature**: Version detection now works correctly enabling proper auto-upgrade workflow
  - Server can now detect current version vs latest PyPI version
  - Upgrade recommendation and workflow function properly
  - Clean cache and reload workflow operational

### Technical
- Removed deprecated `pkg_resources` dependency
- Improved error handling in version detection logic
- Enhanced compatibility with uvx installation method

## [1.0.5] - 2025-07-07

### Removed
- **Server Uninstall Tool**: Removed `server_uninstall` tool and handler for improved safety
  - Removed `handle_server_uninstall` function from admin_handlers.py
  - Removed `server_uninstall` tool definition from tools.py
  - Removed import and mapping from server.py
  - Users should manually uninstall via `uvx uninstall agent-knowledge-mcp` if needed

### Changed
- **Cross-Platform Compatibility**: Removed emoji characters from all print statements for better Windows terminal compatibility
  - Updated print statements across all Python files to use plain text
  - Improved compatibility with older Windows terminal environments
  - Maintained functionality while ensuring consistent display across platforms
- **Server Upgrade Workflow**: Fixed `server_upgrade` function to use proper uvx workflow
  - Changed from non-existent `uvx upgrade` to `uv cache clean` approach
  - Added proper user instructions for restarting Claude Desktop client
  - Improved error handling and user guidance for update process

### Fixed
- Corrected uvx upgrade process since uvx doesn't support direct upgrade commands
- Enhanced Windows terminal compatibility by removing emoji dependencies
- Improved user experience with clearer update instructions

### Technical
- Reduced total tool count from 34 to 33 tools
- Maintained all core functionality while improving safety and compatibility
- Enhanced code maintainability by removing complex uninstall logic

## [1.0.4] - 2025-07-05

### Added
- **Server Management Tools**: Three new admin tools for MCP server self-management
  - `server_status` - Check server version, installation method, and available updates with PyPI integration
  - `server_upgrade` - Upgrade MCP server via uvx with comprehensive error handling and user guidance
  - `server_uninstall` - Safely uninstall MCP server via uvx with confirmation requirements
- **Version Detection**: PyPI API integration for automatic update checking in agent workflows
- **Enhanced Admin Capabilities**: Expanded from 8 to 11 admin tools for complete server lifecycle management

### Changed
- Updated tool count from 31 to 34 tools total
- Enhanced README.md with new admin tool documentation
- Improved admin_handlers.py with uvx command integration and subprocess management
- Updated server.py with new tool handler registrations

### Fixed
- Added proper error handling for uvx availability and installation verification
- Enhanced safety mechanisms with confirmation requirements for destructive operations

### Security
- All server management operations validate uvx installation method before proceeding
- Confirmation required for server uninstall to prevent accidental removal
- Comprehensive error messages guide users for proper installation and usage

## [1.0.3] - 2025-07-05

### Added
- **Community Support Features**: Complete sponsorship and contribution system
  - GitHub Sponsors integration with `.github/FUNDING.yml`
  - Buy Me Coffee integration (https://coff.ee/itshare4u)
  - Multiple sponsorship platforms (PayPal, Ko-fi, GitHub Sponsors)
  - Sponsor tier system with clear benefits and recognition
  - Comprehensive CONTRIBUTING.md with financial support guidelines
- **Enhanced README**: Auto-update installation buttons and sponsorship sections
  - Auto-update installation buttons for VS Code with `--upgrade` flag
  - Multiple configuration options (stable, pinned, latest, development)
  - Detailed update instructions for all AI assistant platforms
  - Beautiful sponsor badges and call-to-action sections
- **Strict Schema Validation**: Configurable strict mode to prevent extra fields in documents
- **Enhanced Configuration Management**: New tools for complete config modification and validation
  - `get_config` - View complete configuration
  - `update_config` - Modify entire configuration with validation
  - `validate_config` - Validate configuration before applying
- **Document Validation Controls**: Fine-grained control over schema enforcement
  - `strict_schema_validation` - Enable/disable strict mode
  - `allow_extra_fields` - Control extra field behavior
  - `required_fields_only` - Enforce only required fields
  - `auto_correct_paths` - Automatic path normalization
- **Enhanced Document Schema**: Support for different validation levels for knowledge base vs custom documents

### Changed
- Updated README.md with comprehensive documentation of new features
- Enhanced tool count from 28 to 31 tools
- Improved error messages with clear validation feedback
- Enhanced `validate_document_structure()` function with `is_knowledge_doc` parameter

### Fixed
- Resolved issue where agents could add arbitrary fields bypassing schema validation
- Improved configuration loading with better error handling

### Deprecated
- `get_allowed_directory` and `set_allowed_directory` are now deprecated in favor of comprehensive config management tools (but still functional for backward compatibility)

### Testing
- Added `test_strict_validation.py` for testing strict schema validation
- Added `demo_config_management.py` for demonstrating new config features
- Moved test files to proper `tests/` directory structure

## [1.0.2] - 2025-01-03

### Added
- Initial PyPI publication
- Comprehensive MCP server with 28 tools
- Elasticsearch integration with full CRUD operations
- File system management with cross-platform support
- Version control integration (Git/SVN)
- Document validation and schema enforcement
- Security controls and sandboxed operations

### Features
- 9 Elasticsearch tools for search and document management
- 11 File system tools for comprehensive file operations
- 5 Administration tools for system management
- 3 Version control tools for Git/SVN operations
- Complete MCP protocol compliance
- Auto-setup capabilities for Elasticsearch

### Documentation
- Comprehensive README with installation and usage examples
- Test suite with multiple demo workflows
- Cross-platform compatibility documentation
- Security and privacy guidelines

## [1.0.1] - 2025-01-02

### Fixed
- Initial package structure and dependencies
- Cross-platform path handling improvements

## [1.0.0] - 2025-01-01

### Added
- Initial release of AgentKnowledgeMCP
- Basic MCP server functionality
- Core Elasticsearch operations
- File system operations
- Document validation framework
