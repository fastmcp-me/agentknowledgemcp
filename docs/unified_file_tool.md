# Unified File Tool - Documentation

## Tổng quan

Tool `edit_file` là một công cụ thống nhất thay thế tất cả các tool file operations riêng lẻ trước đây. Thay vì có 10 tool khác nhau cho từng thao tác file, giờ chỉ cần 1 tool duy nhất `edit_file` hỗ trợ tất cả các thao tác.

## Các thao tác được hỗ trợ

Tool `edit_file` hỗ trợ 10 operation chính:

### 1. `read` - Đọc file
```python
edit_file(
    operation="read",
    path="/path/to/file.txt",
    encoding="utf-8"  # optional
)
```

### 2. `write` - Ghi file (tạo mới hoặc ghi đè)
```python
edit_file(
    operation="write",
    path="/path/to/file.txt",
    content="Nội dung file",
    encoding="utf-8",      # optional
    create_dirs=True,      # optional - tạo thư mục cha nếu chưa có
    overwrite=False        # optional - cho phép ghi đè file có sẵn
)
```

### 3. `append` - Thêm nội dung vào cuối file
```python
edit_file(
    operation="append",
    path="/path/to/file.txt",
    content="Nội dung thêm vào",
    encoding="utf-8"       # optional
)
```

### 4. `delete` - Xóa file
```python
edit_file(
    operation="delete",
    path="/path/to/file.txt"
)
```

### 5. `move` - Di chuyển/đổi tên file
```python
edit_file(
    operation="move",
    path="/path/to/source.txt",
    destination="/path/to/destination.txt",
    create_dirs=True,      # optional - tạo thư mục đích nếu chưa có
    overwrite=False        # optional - cho phép ghi đè file đích
)
```

### 6. `copy` - Sao chép file
```python
edit_file(
    operation="copy",
    path="/path/to/source.txt",
    destination="/path/to/copy.txt",
    create_dirs=True,      # optional - tạo thư mục đích nếu chưa có
    overwrite=False        # optional - cho phép ghi đè file đích
)
```

### 7. `info` - Lấy thông tin chi tiết về file/thư mục
```python
edit_file(
    operation="info",
    path="/path/to/file.txt"
)
```

### 8. `list` - Liệt kê nội dung thư mục
```python
edit_file(
    operation="list",
    path="/path/to/directory",
    recursive=False,       # optional - liệt kê đệ quy
    include_hidden=False   # optional - bao gồm file ẩn
)
```

### 9. `mkdir` - Tạo thư mục
```python
edit_file(
    operation="mkdir",
    path="/path/to/new/directory",
    create_dirs=True       # optional - tạo thư mục cha nếu chưa có
)
```

### 10. `rmdir` - Xóa thư mục
```python
edit_file(
    operation="rmdir",
    path="/path/to/directory",
    recursive=False        # optional - xóa đệ quy (cả nội dung bên trong)
)
```

## Thông số (Parameters)

### Bắt buộc
- `operation`: Loại thao tác cần thực hiện
- `path`: Đường dẫn file/thư mục chính

### Tùy chọn
- `content`: Nội dung (bắt buộc cho write/append)
- `destination`: Đường dẫn đích (bắt buộc cho move/copy)
- `encoding`: Mã hóa file (default: "utf-8")
- `create_dirs`: Tạo thư mục cha (default: True)
- `recursive`: Thao tác đệ quy (default: False)
- `include_hidden`: Bao gồm file ẩn (default: False)
- `overwrite`: Cho phép ghi đè (default: False)

## Ưu điểm của tool thống nhất

### 1. Đơn giản hóa API
- Chỉ cần nhớ 1 tool thay vì 10 tool
- Interface nhất quán cho tất cả thao tác
- Dễ sử dụng và dễ nhớ

### 2. Tính năng mạnh mẽ
- Hỗ trợ tất cả thao tác file/directory
- Error handling chi tiết và hướng dẫn rõ ràng
- Security validation tích hợp
- Flexible parameters cho từng use case

### 3. Maintainability
- Code tập trung trong 1 file
- Dễ bảo trì và cập nhật
- Logic xử lý lỗi thống nhất

## Ví dụ sử dụng

### Workflow đầy đủ
```python
# 1. Tạo thư mục
edit_file(operation="mkdir", path="/tmp/test")

# 2. Tạo file mới
edit_file(
    operation="write", 
    path="/tmp/test/example.txt",
    content="Hello World!\nThis is line 2."
)

# 3. Đọc file
edit_file(operation="read", path="/tmp/test/example.txt")

# 4. Thêm nội dung
edit_file(
    operation="append",
    path="/tmp/test/example.txt", 
    content="\nLine 3 added."
)

# 5. Lấy thông tin file
edit_file(operation="info", path="/tmp/test/example.txt")

# 6. Sao chép file
edit_file(
    operation="copy",
    path="/tmp/test/example.txt",
    destination="/tmp/test/backup.txt"
)

# 7. Liệt kê thư mục
edit_file(operation="list", path="/tmp/test")

# 8. Di chuyển file
edit_file(
    operation="move",
    path="/tmp/test/example.txt",
    destination="/tmp/test/renamed.txt"
)

# 9. Xóa file
edit_file(operation="delete", path="/tmp/test/backup.txt")

# 10. Xóa thư mục (đệ quy)
edit_file(operation="rmdir", path="/tmp/test", recursive=True)
```

## Migration từ tools cũ

### Mapping từ tools cũ sang tool mới

| Tool cũ | Tool mới |
|---------|----------|
| `read_file` | `edit_file(operation="read")` |
| `write_file` | `edit_file(operation="write")` |
| `append_file` | `edit_file(operation="append")` |
| `delete_file` | `edit_file(operation="delete")` |
| `move_file` | `edit_file(operation="move")` |
| `copy_file` | `edit_file(operation="copy")` |
| `file_info` | `edit_file(operation="info")` |
| `list_directory` | `edit_file(operation="list")` |
| `create_directory` | `edit_file(operation="mkdir")` |
| `delete_directory` | `edit_file(operation="rmdir")` |

### Ví dụ migration

**Cũ:**
```python
# Trước đây cần 3 tool calls
read_file(file_path="/path/file.txt")
write_file(file_path="/path/new.txt", content="data")
list_directory(directory_path="/path")
```

**Mới:**
```python
# Giờ chỉ cần 1 tool với 3 operations
edit_file(operation="read", path="/path/file.txt")
edit_file(operation="write", path="/path/new.txt", content="data")
edit_file(operation="list", path="/path")
```

## Error Handling

Tool cung cấp error messages chi tiết với gợi ý khắc phục:

### Permission errors
```
❌ Permission Error: Access denied to file or directory
💡 Suggestions for agents:
   1. Check if you have write access to the directory
   2. Ask user to change working directory using 'update_config' tool
   3. Use 'get_config' to check current allowed_base_directory
```

### File not found
```
❌ File Not Found: The specified path does not exist
💡 Try: Check path spelling and use operation='info' to verify location
```

### Security errors
```
❌ Security error: Path '/forbidden/path' is outside allowed base directory
```

## Implementation Details

- **Security**: Tích hợp `validate_path()` cho tất cả operations
- **Encoding**: Hỗ trợ utf-8, utf-16, ascii, latin-1
- **Cross-platform**: Hoạt động trên Windows, macOS, Linux
- **Performance**: Optimized cho các file operations thường dùng
- **Memory**: Efficient handling cho files lớn

## Testing

Tool đã được test với:
- ✅ Tất cả 10 operations cơ bản
- ✅ Error handling scenarios
- ✅ Security validation
- ✅ Cross-platform compatibility
- ✅ Integration với FastMCP server

## Kết luận

Tool `edit_file` thống nhất đã đơn giản hóa đáng kể việc làm việc với files, từ 10 tools riêng lẻ xuống chỉ còn 1 tool duy nhất với interface nhất quán và tính năng mạnh mẽ.
