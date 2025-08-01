# Release Process Workflow - AgentKnowledgeMCP

## Đơn giản hoá quy trình release theo KB thực tế

Quy trình này đã được xác thực thành công với các releases v2.0.4, v2.0.5, v2.0.6, v2.0.7.

## Version Updating Locations

Cập nhật version ở **5 files** (QUAN TRỌNG - phải đồng nhất):

1. **pyproject.toml** - `version = "X.Y.Z"`
2. **src/__init__.py** - `__version__ = "X.Y.Z"`  
3. **src/config.json** - `"version": "X.Y.Z"`
4. **src/config.default.json** - `"version": "X.Y.Z"`
5. **CHANGELOG.md** - Thêm entry mới cho version

## Quy trình Release Đơn giản

### Bước 1: Cập nhật Version (5 files)
```bash
# Cập nhật version ở cả 5 files trên
# Ví dụ: 2.1.0 → 2.1.1
```

### Bước 2: Build và Publish với Twine
```bash
# Clean previous builds
make clean
# Hoặc: rm -rf dist/ build/ *.egg-info/

# Build package  
python3 -m build

# Quality check
python3 -m twine check dist/*

# Upload to PyPI
python3 -m twine upload dist/* --repository pypi --verbose
```

### Bước 3: Xác nhận
- Kiểm tra PyPI: https://pypi.org/project/agent-knowledge-mcp/X.Y.Z/
- Test cài đặt: `pip install agent-knowledge-mcp==X.Y.Z`

## Lưu ý Quan trọng

- **Version đồng nhất**: Cả 5 files phải có cùng version
- **CHANGELOG**: Luôn cập nhật với features mới  
- **Twine**: Sử dụng twine để publish, không cần git operations phức tạp
- **Đơn giản**: Chỉ cần 5 files + twine, không cần test suite đầy đủ

## Example: Release v2.1.1

```bash
# 1. Cập nhật version ở 5 files (pyproject.toml, __init__.py, config.json, config.default.json, CHANGELOG.md)
# 2. Build và publish:
make clean
python3 -m build  
python3 -m twine upload dist/*
```

**Thành công**: Package được publish lên PyPI và sẵn sàng cài đặt.

---
*Workflow này đã được xác thực với releases v2.0.4-v2.0.7 thành công*
