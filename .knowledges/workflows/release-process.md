# Release Process Workflow

## Version Updating Locations

When releasing a new version, update version numbers in these 4 locations:

1. **pyproject.toml** - Main project version
2. **src/__init__.py** - Package version  
3. **src/main_server.py** - Server version info
4. **src/config.json** - Configuration version reference

## Release Steps

1. **Update Version Numbers**
   - Update all 4 locations listed above
   - Use semantic versioning (major.minor.patch)
   - Ensure consistency across all files

2. **Update CHANGELOG.md**
   - Add new version section
   - List all changes, fixes, and new features
   - Follow existing format and style

3. **Testing**
   - Run full test suite: `python tests/run_all_tests.py`
   - Test MCP server functionality
   - Verify all tools work correctly

4. **Git Operations**
   - Commit all changes
   - Create git tag: `git tag v1.0.X`
   - Push to repository with tags

5. **Build and Publish**
   - Build package: `python -m build`
   - Publish to PyPI (if applicable)
   - Update documentation

## Post-Release

- Monitor for issues
- Update knowledge base with any lessons learned
- Plan next version features
