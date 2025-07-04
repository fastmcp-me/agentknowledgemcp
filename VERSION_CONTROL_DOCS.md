# Version Control System Documentation

## Tổng quan

Hệ thống Version Control đã được tích hợp vào Elasticsearch MCP Server, hỗ trợ cả Git và SVN để quản lý phiên bản của các tài liệu trong knowledge base.

## Cấu hình

### config.json

Thêm section `version_control` vào file config:

```json
{
  "version_control": {
    "enabled": true,
    "type": "git",
    "auto_commit": false
  }
}
```

**Tùy chọn cấu hình:**

- `enabled` (boolean): Bật/tắt tính năng version control
- `type` (string): Loại VCS sử dụng ("git" hoặc "svn")
- `auto_commit` (boolean): Tự động commit khi thay đổi file (chưa implement)

## Tools Mới

### 1. setup_version_control

Thiết lập repository version control.

**Parameters:**
- `vcs_type` (optional, string): Loại VCS ("git" hoặc "svn"), mặc định từ config
- `force` (optional, boolean): Xóa repository cũ nếu tồn tại, mặc định `false`
- `initial_commit` (optional, boolean): Tạo commit đầu tiên, mặc định `true`

**Ví dụ:**
```json
{
  "vcs_type": "git",
  "force": true,
  "initial_commit": true
}
```

**Tính năng:**
- ✅ Kiểm tra và cài đặt Git/SVN
- ✅ Khởi tạo repository
- ✅ Cấu hình user cho Git
- ✅ Tạo .gitignore (cho Git)
- ✅ Commit đầu tiên với tất cả file hiện có
- ✅ Cập nhật config.json

### 2. commit_file

Commit một file cụ thể.

**Parameters:**
- `file_path` (required, string): Đường dẫn tương đối đến file
- `message` (required, string): Commit message
- `add_if_new` (optional, boolean): Thêm file mới vào VCS, mặc định `true`

**Ví dụ:**
```json
{
  "file_path": "documents/important_doc.md",
  "message": "Updated important document with new information",
  "add_if_new": true
}
```

**Tính năng:**
- ✅ Kiểm tra trạng thái file
- ✅ Tự động add file mới nếu cần
- ✅ Stage changes
- ✅ Commit với message
- ✅ Trả về thông tin commit (hash cho Git, revision cho SVN)

### 3. get_previous_file_version

Lấy phiên bản trước của một file.

**Parameters:**
- `file_path` (required, string): Đường dẫn tương đối đến file
- `commits_back` (optional, number): Số commit trở về, mặc định `1`

**Ví dụ:**
```json
{
  "file_path": "documents/important_doc.md",
  "commits_back": 2
}
```

**Tính năng:**
- ✅ Lấy lịch sử commit của file
- ✅ Lấy nội dung file từ commit cụ thể
- ✅ Hiển thị thông tin commit
- ✅ So sánh với phiên bản hiện tại

## Workflow Sử dụng

### Thiết lập ban đầu

1. **Cấu hình VCS trong config.json:**
   ```json
   {
     "version_control": {
       "enabled": true,
       "type": "git"
     }
   }
   ```

2. **Thiết lập repository:**
   ```json
   {
     "tool": "setup_version_control",
     "arguments": {
       "vcs_type": "git",
       "initial_commit": true
     }
   }
   ```

### Quản lý file hàng ngày

1. **Tạo/chỉnh sửa document:**
   - Sử dụng các tool `write_file`, `create_document_template` như bình thường

2. **Commit changes:**
   ```json
   {
     "tool": "commit_file",
     "arguments": {
       "file_path": "knowledge/new_document.md",
       "message": "Added comprehensive documentation for feature X"
     }
   }
   ```

3. **Xem lịch sử:**
   ```json
   {
     "tool": "get_previous_file_version",
     "arguments": {
       "file_path": "knowledge/new_document.md",
       "commits_back": 1
     }
   }
   ```

## So sánh Git vs SVN

| Tính năng | Git | SVN |
|-----------|-----|-----|
| Repository type | Distributed | Centralized |
| Offline work | ✅ Đầy đủ | ❌ Hạn chế |
| Setup complexity | 🟡 Trung bình | 🔴 Phức tạp |
| Performance | 🟢 Nhanh | 🟡 Chậm hơn |
| Learning curve | 🟡 Trung bình | 🟢 Đơn giản |
| Branching | 🟢 Mạnh | 🟡 Cơ bản |

## Lỗi thường gặp

### Git not found
```
❌ Error: GIT is not installed.
Please install: git (usually pre-installed on macOS/Linux)
```

**Giải pháp:**
- macOS: `xcode-select --install` hoặc `brew install git`
- Linux: `sudo apt install git` hoặc `sudo yum install git`

### SVN not found
```
❌ Error: SVN is not installed.
Please install: brew install subversion (on macOS)
```

**Giải pháp:**
- macOS: `brew install subversion`
- Linux: `sudo apt install subversion`

### Repository already exists
```
⚠️ GIT repository already exists in /path/to/repo
Use force=true to reinitialize
```

**Giải pháp:**
- Sử dụng `force: true` trong arguments để khởi tạo lại

## Kiến trúc Code

### Files mới được thêm:

1. **`src/version_control_handlers.py`**
   - Chứa implementation của 3 tools version control
   - Hỗ trợ cả Git và SVN
   - Error handling và validation

2. **`src/tools.py`** (updated)
   - Thêm function `get_version_control_tools()`
   - Định nghĩa 3 tools mới

3. **`src/server.py`** (updated)
   - Import version control handlers
   - Thêm mapping trong TOOL_HANDLERS

4. **`src/config.json`** (updated)
   - Thêm section version_control

### Test files:

1. **`test_version_control.py`** - Test comprehensive
2. **`test_simple_vcs.py`** - Test đơn giản và demo
3. **`demo_version_control.py`** - Demo MCP tools (có lỗi import)

## Roadmap tương lai

### Phase 1 (Completed) ✅
- [x] Basic Git support
- [x] Basic SVN support  
- [x] Setup, commit, và history tools
- [x] Config-driven VCS selection

### Phase 2 (Planned)
- [ ] Auto-commit on file changes
- [ ] Branch management
- [ ] Merge conflict resolution
- [ ] Remote repository support

### Phase 3 (Planned)
- [ ] Visual diff tools
- [ ] File blame/annotation
- [ ] Tag management
- [ ] Advanced search trong history

## Best Practices

1. **Commit Messages:**
   - Sử dụng format: "Added/Updated/Fixed + what + why"
   - Ví dụ: "Updated API documentation with new authentication methods"

2. **File Organization:**
   - Commit các file liên quan cùng nhau
   - Tránh commit quá nhiều thay đổi trong một lần

3. **Repository Structure:**
   - Sử dụng .gitignore để loại trừ temporary files
   - Organize files theo chủ đề/category

4. **Security:**
   - Không commit sensitive information
   - Sử dụng allowed_base_directory để hạn chế phạm vi
