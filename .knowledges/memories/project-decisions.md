# Project Memories and Lessons Learned

## Smart Prompting Implementation

### Key Decision: File-based vs Knowledge Base Storage
**Date**: July 2025
**Decision**: Use file-based storage in `.knowledges` directory instead of Elasticsearch
**Reasoning**: 
- Simpler project-specific organization
- AI-powered filtering provides intelligence without complexity
- Direct VS Code integration via `ctx.list_roots()`
- Easier maintenance and version control

### VS Code Workspace Root Detection
**Solution Found**: `ctx.list_roots()` function
- Returns array of workspace roots from VS Code
- First element is typically the main workspace
- Eliminates need for manual root path parameters
- Clean integration with MCP "roots" capability

## Common Issues and Solutions

### Index Document Error Pattern
**Issue**: `index_document` tool failing with path-related errors
**Root Cause**: File path handling in document processing
**Solution**: Always validate file paths and use absolute paths
**Prevention**: Add comprehensive path validation in all file operations

### Context Integration
**Pattern**: Always use Context parameter for MCP capabilities
- Logging: `await ctx.info()`, `await ctx.error()`
- AI Sampling: `await ctx.sample()`
- Workspace Access: `await ctx.list_roots()`
- Progress: `await ctx.report_progress()`

## Architecture Patterns

### MCP Tool Design
1. **Parameter Validation**: Always validate inputs first
2. **Context Logging**: Log progress and errors
3. **Error Handling**: Graceful degradation with helpful messages
4. **AI Integration**: Use `ctx.sample()` for intelligent processing

### Knowledge Management
- Structured organization in `.knowledges/{workflows,rules,memories}/`
- Markdown format for easy editing and version control
- AI filtering for relevant content synthesis
- Project-specific context preservation
