# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
