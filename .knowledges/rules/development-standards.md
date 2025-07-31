# Development Rules and Standards

## Code Style

### Python Standards
- Follow PEP 8 for code formatting
- Use type hints for all function parameters and returns
- Maximum line length: 120 characters
- Use docstrings for all public functions and classes

### FastMCP Conventions
- Use descriptive tool names with clear purposes
- Include comprehensive docstrings for all MCP tools
- Add appropriate tags for tool categorization
- Handle errors gracefully with user-friendly messages

## File Organization

### Server Structure
- Keep servers in separate files by functionality
- Use clear, descriptive filenames
- Maintain consistent import structure
- Group related functionality together

### Tool Development
- One tool per logical function
- Clear parameter validation
- Comprehensive error handling
- Context logging for debugging

## Testing Requirements

### Before Commits
- All new tools must have tests
- Test both success and error cases  
- Verify MCP protocol compliance
- Check integration with knowledge base

### Documentation
- Update README for new features
- Add usage examples for complex tools
- Maintain changelog entries
- Update copilot instructions if needed
