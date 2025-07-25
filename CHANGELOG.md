# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.3] - 2025-07-25

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.4] - 2025-07-25

### ✨ Added
- **New Prompt**: Added `copilot_instructions` prompt to provide AI assistants direct access to behavioral guidelines
- **Enhanced Prompt Server**: Now includes both `mcp_usage_guide` and `copilot_instructions` prompts
- **AI Assistant Guidelines**: Complete behavioral protocols and mandatory workflows accessible via MCP

### 🔧 Fixed
- **PyPI Entry Point**: Fixed incorrect entry point in published package (was pointing to non-existent `src.fastmcp_server`)
- **Import Error**: Resolved `ModuleNotFoundError: No module named 'src.fastmcp_server'` when installing from PyPI
- **Package Consistency**: Ensured all entry points correctly reference `src.main_server:cli_main`

### 🚀 Improved  
- **Build Process**: Enhanced package building with proper validation of entry points
- **Version Management**: Updated version consistency across all package files
- **Documentation**: Added PyPI installation troubleshooting guidance
- **CLI Output**: Updated to show both available prompts clearly

### 📚 Technical Details
- **Entry Point**: `agent-knowledge-mcp = "src.main_server:cli_main"`
- **New Helper Function**: `_load_copilot_instructions()` for secure file loading
- **Error Handling**: Comprehensive error handling for copilot instructions file access
- **Affected Installs**: uvx, pip, and other PyPI-based installations
- **Fix Status**: Immediately available on PyPI v2.0.4+

## [2.0.3] - 2025-07-25

### 🔧 Fixed
- **Version Consistency**: Updated pyproject.toml version from 2.0.2 to 2.0.3 for consistency
- **Build Process**: Ensured all version references are synchronized across package files
- **PyPI Publishing**: Successfully published with consistent version management

### 🚀 Improved
- **Package Metadata**: Enhanced package configuration with proper version alignment
- **Changelog**: Added comprehensive release documentation with build improvements

### 📚 Technical Details
- **pyproject.toml**: Version updated to maintain consistency with src/__init__.py
- **Build Output**: Generated agent_knowledge_mcp-2.0.3-py3-none-any.whl and .tar.gz
- **PyPI URL**: https://pypi.org/project/agent-knowledge-mcp/2.0.3/

## [2.0.0] - 2025-07-24

### 🎉 MAJOR RELEASE: FastMCP Migration

This is a major version release with significant architectural changes and breaking changes.

### ⚠️ BREAKING CHANGES
- **Complete Migration to FastMCP Framework**: Replaced legacy MCP implementation with modern FastMCP
- **New Server Architecture**: Redesigned server structure with `main_server.py` as primary entry point
- **Confirmation Middleware**: Implemented FastMCP-native confirmation middleware with better user experience
- **Enhanced Prompt Server**: Added comprehensive MCP usage guidance through integrated prompt server
- **Configuration Changes**: Updated configuration structure for FastMCP compatibility

### Added
- **FastMCP Framework Integration**: Complete migration from legacy MCP to FastMCP
  - Modern middleware support with separation of concerns
  - Enhanced error handling and user interaction patterns
  - Better tool registration and management
  - Improved performance and reliability

- **New Main Server Architecture**: `src/main_server.py`
  - Centralized server composition
  - FastMCP middleware integration
  - Streamlined tool mounting and configuration
  - Better separation between admin and core functionality

- **Advanced Confirmation Middleware**: `src/middleware/confirmation_middleware.py`
  - FastMCP-native middleware implementation
  - Configuration-driven confirmation rules
  - Simplified user experience with clean confirmation dialogs
  - Python 3.13 compatibility with proper typing

- **Comprehensive MCP Usage Guide**: `src/resources/mcp_usage_instructions.md`
  - 15,000+ character comprehensive usage documentation
  - 4 real-world workflow scenarios
  - 3 progressive difficulty tutorials
  - Complete tool reference with examples
  - Troubleshooting and best practices sections

- **Enhanced Prompt Server**: `src/prompts/prompt_server.py`
  - MCP usage guidance delivery through LLM interactions
  - English language support for professional documentation
  - Integration with comprehensive usage instructions

- **Ask User Advice Tool**: Enhanced human-in-the-loop decision making
  - Multi-level urgency support (low/normal/high/urgent)
  - Comprehensive request formatting
  - Context-aware user guidance requests

### Changed
- **Server Entry Point**: Primary server now runs through `main_server.py` instead of legacy server
- **Middleware Architecture**: Moved from inline confirmation to proper FastMCP middleware patterns
- **Tool Organization**: Better separation between admin tools and core functionality
- **Configuration Management**: Enhanced configuration loading and validation
- **Error Handling**: Improved error messages and user feedback throughout the system

### Enhanced
- **User Experience**: Simplified confirmation dialogs and clearer user communication
- **Documentation**: Comprehensive usage guides and step-by-step tutorials
- **Development Experience**: Better code organization and maintainability
- **Performance**: FastMCP framework provides better performance and resource management
- **Reliability**: Enhanced error handling and graceful failure recovery

### Migration Notes
- **Existing Users**: This version includes breaking changes in server architecture
- **Configuration**: May require configuration updates for new FastMCP structure
- **Tool Usage**: All existing tools remain functional with improved user experience
- **Installation**: Use `uvx upgrade agent-knowledge-mcp` or reinstall for clean migration

### Technical Details
- **Framework**: FastMCP 0.15.0+ with full middleware support
- **Python**: 3.10+ with enhanced 3.13 compatibility
- **Architecture**: Modular design with proper separation of concerns
- **Middleware**: Confirmation, prompt delivery, and extensible architecture
- **Documentation**: Professional English documentation with comprehensive examples

## [1.0.28] - 2025-07-13

### Security
- **CRITICAL SECURITY FIX**: Fixed user_response tool auto-calling vulnerability
  - Agent was bypassing confirmation system by auto-calling user_response without user permission
  - Updated user_response tool description with explicit warning: "⚠️ CRITICAL: This tool MUST ONLY be called by the USER, NEVER by the agent!"
  - Enhanced parameter descriptions to prevent automatic response setting
  - Verification confirms agents now properly ask user for approval instead of auto-calling
  - Complete resolution of confirmation system bypass vulnerability

### Changed
- Enhanced security constraints in MCP tool definitions
- Improved agent behavior compliance with permission protocols

## [1.0.27] - 2025-07-13

### Added
- **Enhanced Confirmation System Configuration**: Improved configuration management for user confirmation requirements
  - Fixed duplicate configuration structure in confirmation section
  - Enabled confirmation for `index_document` operations by default for enhanced security
  - Streamlined configuration structure with proper validation
- **Configuration System Restoration**: Complete revert to original working state after user feedback
  - Restored `self.default_config` with hard-coded values in ConfirmationManager
  - Maintained both config.json and config.default.json with identical confirmation sections
  - Ensured proper backup/restore functionality for server upgrades
- **Test File Organization**: Improved project structure organization
  - Moved test files to appropriate tests directory for better organization
  - Enhanced project structure following Python best practices

### Fixed
- **Configuration Duplication**: Removed redundant configuration entries
- **File Organization**: Proper placement of test files in tests directory
- **Configuration Validation**: Fixed malformed JSON structure in confirmation configuration

### Changed
- **Default Security Posture**: Index operations now require confirmation by default
- **File Structure**: Test files properly organized in tests directory
- **Configuration Management**: Streamlined confirmation system configuration

## [1.0.26] - 2025-07-12

### Added
- **Time-Based Search Enhancement**: Comprehensive time filtering capabilities for search operations
  - `date_from` parameter: Filter documents from specific date (YYYY-MM-DD, YYYY-MM-DD HH:MM:SS, or relative: '7d', '1w', '1m')
  - `date_to` parameter: Filter documents until specific date (YYYY-MM-DD, YYYY-MM-DD HH:MM:SS, or 'now')
  - `time_period` parameter: Quick time shortcuts ('today', 'yesterday', 'week', 'month', 'year')
  - `sort_by_time` parameter: Control time-based sorting ('desc' or 'asc')
- **Relative Date Support**: Natural language date parsing for flexible time filtering
  - '7d', '1w', '1m' style relative dates
  - Automatic conversion to Elasticsearch-compatible date ranges
  - Support for 'now' as end date reference
- **Intelligent Time-Based Sorting**: Dynamic sorting behavior based on time filtering usage
  - Time filtering enabled: Sort by time first, then relevance
  - No time filtering: Sort by relevance first, then recency (existing behavior)
- **Enhanced Search Guidance**: Time-specific suggestions when no results found with time filters

### Enhanced
- **Search Tool Schema**: Extended with comprehensive time-based parameters and documentation
- **Search Result Descriptions**: Clear indication of applied time filters and sorting behavior
- **Error Handling**: Time-specific suggestions for broadening search when time filters yield no results
- **User Experience**: Contextual guidance for time filter usage and optimization

### Technical
- **Date Parsing Engine**: Robust parsing for multiple date formats and relative date expressions
- **Elasticsearch Integration**: Proper range filters and bool queries for time-based search
- **Backward Compatibility**: All existing search functionality preserved, time parameters are optional

## [1.0.25] - 2025-07-12

### Added
- **Enhanced Error Pattern Matching**: Comprehensive detection of Elasticsearch index errors including `index_not_found_exception` and `no such index` patterns
- **4-Step Agent Guidance**: Structured guidance for agents when encountering index-related errors with specific tool recommendations
- **Improved Error Messages**: Clear distinction between index errors and document errors with actionable next steps

### Enhanced
- **Search Error Handling**: Now provides specific 4-step guidance when searching non-existent indices
- **Agent Experience**: From generic "Unknown Error" to detailed, actionable error messages with tool suggestions
- **Pattern Recognition**: Supports multiple error message variations including "does not exist" formats

### Fixed
- **Error Handler Coverage**: All Elasticsearch handlers now have comprehensive pattern matching for better error detection
- **User Experience**: Search operations now provide helpful guidance instead of cryptic error messages

## [1.0.24] - 2025-07-12

### Added
- **Knowledge Base Reorganization Guidance**: Automatic detection when search returns too many results (15+ documents)
- **Intelligent Search Result Analysis**: Extracts topics, content types, and priority distribution from search results
- **User Collaboration Workflow**: Step-by-step guidance for knowledge base reorganization with user confirmation
- **Duplicate Prevention Enhancement**: More explicit guidance in all index document functions to prevent duplicate creation

### Enhanced
- **Search Function Intelligence**: Now provides specific reorganization suggestions and user collaboration templates
- **Agent Guidance Clarity**: Enhanced visual prominence with warning levels (CRITICAL, MANDATORY, IMPORTANT)
- **Knowledge Quality Management**: Promotes "quality over quantity" approach with targeted cleanup recommendations

## [1.0.23] - 2025-07-11

### Added
- **Enhanced Agent Error Guidance**: Search errors now provide 4-step specific guidance for AI agents when indices don't exist
- **Content Management Strategy**: Intelligent guidance for when to create files vs index content directly (1000+ character threshold)
- **Search Optimization**: No-results scenarios trigger comprehensive keyword expansion suggestions and user collaboration prompts
- **Dual Result Sorting**: Search results now sorted by both relevance score and recent update time for better discovery

### Enhanced
- **File Permission Handling**: Enhanced error messages with specific tool suggestions and fallback strategies for permission issues
- **Agent Workflow Integration**: All error handling now includes actionable next steps specifically designed for AI agent workflows

## [1.0.22] - 2025-07-09

### Added
- **Section-Specific Intelligent Merge**: Enhanced configuration merge algorithm with differentiated handling for different config sections
- **reset_config Tool**: New manual reset tool that overwrites config with defaults while creating timestamped backups
- **Deprecated Settings Detection**: Automatic filtering of deprecated settings using pattern detection for 'old_', 'deprecated_', 'legacy_' prefixes
- **User-Only Settings Preservation**: Intelligent merge now preserves user settings even if they don't exist in new config

### Enhanced
- **server_upgrade Tool**: Now automatically backs up and intelligently restores user configuration during upgrades
- **Configuration Management**: Two-tier approach with manual reset vs automatic intelligent restore
- **LATEST CONFIG Sections**: server, schema, version sections always use newest config for compatibility
- **INTELLIGENT MERGE Sections**: security, elasticsearch, logging sections preserve user settings while adding new features

### Removed
- **restore_config Tool**: Replaced by automatic restoration in server_upgrade process

### Technical
- **Algorithm Enhancement**: Recursive merge with section-aware logic for optimal configuration handling
- **Comprehensive Testing**: Added extensive test coverage for section-specific behavior and real-world upgrade scenarios

## [1.0.21] - 2025-07-09

### Enhanced
- **Schema Configuration**: Added `content` field to `required_fields` in default configuration schema
- **Configuration Consistency**: Ensured content field is properly included in document schema validation
- **Documentation Updates**: Improved schema documentation and examples

### Fixed
- **Configuration Schema**: Resolved inconsistency where content field was missing from required_fields list
- **Schema Validation**: Enhanced schema validation to properly handle content field requirements

## [1.0.20] - 2025-07-09

### BREAKING CHANGES ⚠️
- **Strict Configuration Mode**: Removed ALL fallback mechanisms from configuration loading. Server now requires proper `config.json` with `document_schema` and `document_validation` sections or will fail to start with clear error messages.
- **No Emergency Fallbacks**: Eliminated `EMERGENCY_FALLBACK_SCHEMA` and all silent configuration defaults. Configuration errors now cause immediate RuntimeError with detailed fix suggestions.

### Added
- **Configuration Backup/Restore System**: Implemented comprehensive backup and restore system for server upgrades
  - `config.default.json` - Automatic backup file created from current configuration
  - `restore_config` - New admin tool to manually restore configuration from backup
  - **Smart Fallback**: Automatic fallback to `config.default.json` when `config.json` is missing after server upgrades
  - **Clear User Messaging**: Explicit notifications when fallback configuration is used

### Enhanced
- **Strict Error Handling**: Implemented zero-tolerance configuration validation with comprehensive error messages and solution guidance
- **Boolean Type Conversion**: Enhanced validation config loading to properly handle string boolean values (`"false"` → `false`) from JSON configuration
- **Production Safety**: Server will fail fast on startup if configuration is invalid, preventing silent degradation in production environments
- **Upgrade Resilience**: Server upgrades no longer cause configuration loss with automatic backup/restore system

### Documentation
- **Comprehensive Guide**: Added `strict-configuration-validation-implementation-v1020.md` with complete implementation details, testing results, and migration guidance
- **Backup/Restore Guide**: Added `configuration-backup-restore-system-v1020.md` with detailed upgrade workflow and recovery procedures
- **Configuration Examples**: Updated all config examples (`config.json.example`, `config.example.json`) with proper document_schema sections

### Technical Improvements
- **Zero Fallback Architecture**: Complete removal of fallback code paths ensures predictable behavior and prevents configuration drift
- **Enhanced Error Messages**: Configuration errors include exact file paths, missing sections, and specific fix instructions
- **Runtime Safety**: Strict validation prevents server startup with incomplete or invalid configurations
- **Multi-tier Fallback**: Controlled fallback system for server upgrade scenarios while maintaining strict validation in normal operation

## [1.0.19] - 2025-07-08

### Fixed
- **Function Signature Bug**: Fixed critical bug in `get_example_document()` function that was causing "takes 0 positional arguments but 1 was given" error when strict validation was enabled during `index_document` operations
- **Document Schema Validation**: Removed duplicate `format_validation_error` functions that were causing conflicts in document validation workflow
- **Test Infrastructure**: Updated test import paths for proper module loading without MCP dependencies

### Enhanced
- **Error Handling**: Improved error messages for validation failures with proper context handling
- **Strict Validation**: Strict schema validation now works correctly without function signature errors
- **Knowledge Base**: Added comprehensive documentation of the bug fix for future reference

## [1.0.18] - 2025-07-09

### Fixed
- **Index Document Bug**: Fixed critical bug in `handle_index_document` function where documents were validated but not actually indexed to Elasticsearch when `validate_schema=True`. The function now properly proceeds to index documents after successful validation.

## [1.0.17] - 2025-07-07

### Changed
- **Packaging**: Added `config.json` and example files to the package distribution in `pyproject.toml`. This makes the server more robust by providing a fallback configuration if a local `config.json` is missing or invalid when run via `uvx`.

## [1.0.16] - 2025-07-07

### Fixed
- **Version Consistency**: Corrected the `__version__` in `src/__init__.py` to match the `pyproject.toml` version. The `1.0.15` release had an incorrect internal version number.

## [1.0.15] - 2025-07-07

### Fixed
- **Tool Definition Bug**: Corrected the `inputSchema` for the `update_config` tool in `src/tools.py` to match the actual implementation in `src/admin_handlers.py`. This resolves a critical bug that made the tool unusable.

### Added
- **Knowledge Base Documentation**:
  - Added a detailed guide on how to configure the MCP client for local development using `.vscode/mcp.json`.
  - Added a comprehensive guide for the Python package release process.

## [1.0.14] - 2025-07-07

### Added
- **New get_prompt_guidance tool**: Provides GitHub link to copilot instructions for effective MCP server usage
- Simple English message directing users to comprehensive prompting documentation
- Zero-parameter tool for easy access to guidance resources

### Enhanced
- Admin tools category expanded with user guidance functionality
- Improved user onboarding experience with direct access to effective prompting strategies

## [1.0.13] - 2025-07-07

### Testing
- **Auto-Upgrade Workflow Validation**: Final testing of improved server_upgrade tool
- Testing complete PyPI API integration and version-specific installation
- Validating fallback mechanisms for UV index sync delays
- Comprehensive end-to-end auto-upgrade testing from 1.0.10 → 1.0.13

### Technical
- No functional changes, version bump for testing improved auto-upgrade implementation
- All enhanced auto-upgrade functionality operational and ready for production use

## [1.0.12] - 2025-07-07

### Enhanced
- Improved server_upgrade tool with robust fallback mechanism
- Direct version-specific installation from PyPI API
- Clean cache + force install approach for reliable upgrades
- Better error handling and upgrade detection
- Fallback to latest available version when specific version fails

### Fixed
- Auto-upgrade reliability issues with UV index sync delays
- Enhanced upgrade detection from installation output
- Better user messaging for upgrade success/failure

## [1.0.11] - 2025-07-07

### Enhanced
- Improved server_upgrade tool with direct cache clean + force install approach
- Better upgrade reliability: `uv cache clean && uv tool install agent-knowledge-mcp==version --force`
- Enhanced output parsing to detect successful upgrades vs reinstalls
- Improved error handling with detailed manual fallback instructions

### Testing
- Validated new upgrade approach: cache clean + specific version install
- Confirmed reliability over standard `uv tool upgrade` command
- Better handling of PyPI propagation delays

## [1.0.10] - 2025-07-07

### Improved
- Enhanced server_upgrade tool with direct upgrade attempt before cache clean
- Better error handling and fallback mechanisms for auto-upgrade
- Improved user instructions for manual upgrade when needed
- Added PyPI propagation delay handling

### Testing
- Comprehensive auto-upgrade workflow testing
- Validated cache cleaning functionality
- Confirmed version detection accuracy

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
