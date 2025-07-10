# Release Process - Complete Version Update Checklist

## 🎯 Problem Identified

When releasing to PyPI, we need to update version in **multiple locations** but currently miss some files, specifically `config.json` which was missed in recent releases.

## 📋 MANDATORY Version Update Locations

### 1. Core Package Files
- [ ] **`src/__init__.py`** - `__version__ = "X.X.X"`
- [ ] **`pyproject.toml`** - `version = "X.X.X"`

### 2. Configuration Files ⚠️ **OFTEN MISSED**
- [ ] **`src/config.json`** - `"server": {"version": "X.X.X"}`
- [ ] **`src/config.json.example`** - `"server": {"version": "X.X.X"}`
- [ ] **`src/config.example.json`** - `"server": {"version": "X.X.X"}`

### 3. Documentation Files
- [ ] **`CHANGELOG.md`** - Add new version entry at top
- [ ] **`README.md`** - Update any version references if needed

### 4. Test Files (if needed)
- [ ] **`tests/__init__.py`** - Update if version-specific tests
- [ ] **`tests/demo_config_management.py`** - Update test version if needed

## 🚀 Complete Release Workflow

### Step 1: Pre-Release Preparation
```bash
# 1. Check current version in all files
grep -r "version.*1\." src/ tests/ pyproject.toml CHANGELOG.md

# 2. Determine new version (semantic versioning)
# MAJOR.MINOR.PATCH
# - MAJOR: breaking changes  
# - MINOR: new features, backward compatible
# - PATCH: bug fixes, backward compatible

# 3. Update CHANGELOG.md first
# Add new section at top with changes
```

### Step 2: Version Updates (MANDATORY CHECKLIST)
```bash
# Core package files
echo '__version__ = "X.X.X"' > src/__init__.py
sed -i 's/version = ".*"/version = "X.X.X"/' pyproject.toml

# Configuration files (CRITICAL - often missed!)
sed -i 's/"version": ".*"/"version": "X.X.X"/' src/config.json
sed -i 's/"version": ".*"/"version": "X.X.X"/' src/config.json.example  
sed -i 's/"version": ".*"/"version": "X.X.X"/' src/config.example.json

# Verify all updates
grep -r "version.*X\.X\.X" src/ pyproject.toml
```

### Step 3: Testing & Validation
```bash
# 1. Run all tests
python3 tests/test_strict_validation.py
python3 tests/test_file_paths.py
python3 tests/test_version_control.py

# 2. Test specific bug fixes (if applicable)
# For function signature fixes:
python3 -c "from src.document_schema import format_validation_error, DocumentValidationError; format_validation_error(DocumentValidationError('test'), 'general')"

# 3. Test package build
uv build

# 4. Test installation locally
uv tool install dist/agent_knowledge_mcp-X.X.X-py3-none-any.whl --force

# 5. Test basic functionality
# (Start MCP client and verify tools work)

# 6. Verify version consistency across all files
grep -r "X\.X\.X" src/ pyproject.toml | grep version
```

### Step 4: Commit & Tag
```bash
# 1. Commit all version changes
git add -A
git commit -m "Release vX.X.X: [brief description of changes]"

# 2. Create annotated tag
git tag -a vX.X.X -m "Release vX.X.X"

# 3. Push changes and tags
git push origin main
git push origin vX.X.X
```

### Step 5: PyPI Publication
```bash
# 1. Build package
uv build

# 2. Upload to PyPI
uv publish --token $PYPI_TOKEN

# 3. Verify on PyPI
# Check https://pypi.org/project/agent-knowledge-mcp/
```

### Step 6: Post-Release Verification
```bash
# 1. Test auto-upgrade works
uvx upgrade agent-knowledge-mcp

# 2. Test new installation
uvx install agent-knowledge-mcp

# 3. Update documentation if needed
# 4. Announce release (GitHub, social media, etc.)
```

## ⚠️ Critical Notes

### Version Consistency Issues Prevented
- **Config files contain server version** - must match package version
- **Users see version in server status** - comes from config.json
- **MCP clients may cache old versions** - consistent versioning prevents confusion

### Common Mistakes to Avoid
- ❌ **Forgetting config.json version** (happened in v1.0.19 - CRITICAL LESSON)
- ❌ **Function signature mismatches** during validation fixes (happened in v1.0.19)
- ❌ **Inconsistent version numbers** across files
- ❌ **Not testing before PyPI upload**
- ❌ **Missing CHANGELOG.md updates**
- ❌ **Not creating Git tags**
- ❌ **Duplicate function definitions** causing conflicts

## 🔧 Automation Suggestions

### Create Release Script
```bash
#!/bin/bash
# release.sh - Automated release script

NEW_VERSION=$1
if [ -z "$NEW_VERSION" ]; then
    echo "Usage: ./release.sh X.X.X"
    exit 1
fi

echo "🚀 Releasing version $NEW_VERSION"

# Update all version files
echo "📝 Updating version files..."
echo "__version__ = \"$NEW_VERSION\"" > src/__init__.py
sed -i "s/version = \".*\"/version = \"$NEW_VERSION\"/" pyproject.toml
sed -i "s/\"version\": \".*\"/\"version\": \"$NEW_VERSION\"/" src/config.json
sed -i "s/\"version\": \".*\"/\"version\": \"$NEW_VERSION\"/" src/config.json.example
sed -i "s/\"version\": \".*\"/\"version\": \"$NEW_VERSION\"/" src/config.example.json

# Verify updates
echo "🔍 Verifying version updates..."
grep -r "version.*$NEW_VERSION" src/ pyproject.toml

echo "✅ Version updated to $NEW_VERSION"
echo "📋 Next steps:"
echo "   1. Update CHANGELOG.md"
echo "   2. Run tests"
echo "   3. Commit and tag"
echo "   4. Build and publish"
```

## 📝 Version History Lessons

### Recent Issues
- **v1.0.19**: `config.json` not updated (still shows 1.0.18) - **JUST IDENTIFIED**
- **v1.0.19**: Bug fix release for `get_example_document()` function signature error
- **v1.0.15**: `__init__.py` version mismatch with pyproject.toml
- **v1.0.X**: Multiple inconsistencies in config files

### Success Patterns
- **Complete checklist follow-through**
- **Automated version verification**
- **Testing before PyPI upload**
- **Consistent documentation updates**

## 🏷️ Tags

- release-process
- version-management
- pypi-deployment
- config-json-updates
- automation
- quality-assurance
- deployment-checklist

## 📅 Last Updated

July 10, 2025 - After fixing get_example_document() bug and identifying config.json version inconsistency in v1.0.19
