# Workflow: Development Without Server Restart

## Overview
This workflow enables efficient development and testing of AgentKnowledgeMCP without needing to manually restart the server after code changes. It uses hot-reloading and automated testing to accelerate the development cycle.

## Prerequisites
- Python 3.8+ with project dependencies installed
- AgentKnowledgeMCP project set up in development environment
- Access to VS Code or compatible IDE
- Testing environment configured

## Steps

### 1. Setup Hot-Reloading Development Server
```bash
# Install watchdog for file monitoring (if not already installed)
pip install watchdog

# Start MCP server with auto-reload capability
python -m src --reload
# OR use uvicorn if FastAPI components are involved
uvicorn src.main_server:app --reload --port 8000
```

### 2. Configure Development Environment
- **File Organization**: Keep servers in separate files by functionality
- **Descriptive Naming**: Use clear, descriptive filenames (e.g., `elasticsearch_document.py`, `prompt_server.py`)
- **Citation**: `.knowledges/rules/development-standards.md:19-23`

### 3. Follow Coding Standards During Development
Before making any code changes:
```bash
# Run linter to check code quality
flake8 src/
# OR
pylint src/
```

**Required Standards**:
- Follow PEP 8 formatting
- Use type hints for all functions
- Include comprehensive docstrings
- **Citation**: `.knowledges/rules/development-standards.md:5-10`

### 4. Implement Code Changes
When developing new features or fixing bugs:

- **Path Validation**: Always validate file paths and use absolute paths
- **Context Usage**: Use Context parameter for logging, workspace access, and progress reporting
- **Error Handling**: Include comprehensive error handling with user-friendly messages
- **Citation**: `.knowledges/memories/project-decisions.md:24-35`

### 5. Test Changes Automatically
Hot-reloading allows immediate testing:
```bash
# Changes are automatically detected and server reloads
# Test functionality through VS Code MCP integration
# OR test directly via API/CLI

# Run comprehensive test suite before committing
python tests/run_all_tests.py
```

### 6. Validate Before Commit
**Pre-commit Checklist**:
- [ ] All tests pass (including new tests for new features)
- [ ] Code follows PEP 8 and project standards
- [ ] Type hints added to all new functions
- [ ] Docstrings added/updated
- [ ] Error cases covered by tests
- **Citation**: `.knowledges/rules/development-standards.md:33-37`, `.knowledges/workflows/release-process.md:25`

### 7. Document Lessons Learned
If any new insights or decisions are discovered during development:
```bash
# Add to project memories
echo "New insight about [topic]" >> .knowledges/memories/$(date +%Y-%m-%d)-development-insight.md
```

## Expected Outcomes
- **Faster Development Cycle**: No manual server restarts needed
- **Immediate Feedback**: Code changes reflected instantly
- **Quality Assurance**: Automated testing catches issues early
- **Consistent Standards**: All code follows project conventions
- **Better Documentation**: Development insights captured for future reference

## Notes

### Hot-Reloading Options
1. **Watchdog**: General Python file monitoring
2. **Uvicorn --reload**: For ASGI/FastAPI components
3. **VS Code Auto-Reload**: IDE-integrated solutions

### Common Issues & Solutions
- **Path Errors**: Always use absolute paths and validate before use
- **Context Missing**: Remember to use Context parameter for MCP operations
- **Test Coverage**: Ensure both success and error cases are tested
- **Citation**: `.knowledges/memories/project-decisions.md:24-35`

### Development Best Practices
- Keep changes small and focused
- Test frequently during development
- Document any architectural decisions
- Follow the established server organization patterns

## Troubleshooting

### Server Won't Hot-Reload
```bash
# Check if watchdog is properly installed
pip list | grep watchdog

# Restart with explicit reload flag
python -m src --reload --verbose
```

### Tests Failing After Changes
```bash
# Run specific test modules
python -m pytest tests/test_specific_module.py -v

# Check for import errors
python -c "import src; print('Import successful')"
```

### Path-Related Errors
- Verify all file paths are absolute
- Check workspace root detection
- Validate Context.list_roots() usage

---
*Created: 2025-07-31*
*Citations: `.knowledges/workflows/release-process.md:24-28`, `.knowledges/rules/development-standards.md:5-23,33-37`, `.knowledges/memories/project-decisions.md:24-35,45-46`*
