# Elasticsearch MCP Server Configuration

## File cấu hình

Server sử dụng file `config.json` để cấu hình các thông số. Nếu file không tồn tại, server sẽ sử dụng cấu hình mặc định.

### Cấu trúc file config.json

```json
{
  "elasticsearch": {
    "host": "localhost",
    "port": 9200
  },
  "security": {
    "allowed_base_directory": "/Users/nguyenkimchung/ElasticSearch"
  },
  "server": {
    "name": "elasticsearch-mcp",
    "version": "0.1.0"
  }
}
```

### Các tham số cấu hình

#### elasticsearch
- `host`: Địa chỉ Elasticsearch server (mặc định: localhost)
- `port`: Port của Elasticsearch server (mặc định: 9200)

#### security
- `allowed_base_directory`: Thư mục gốc được phép truy cập cho các thao tác file

#### server
- `name`: Tên của MCP server
- `version`: Phiên bản của server

### Cách thay đổi cấu hình

1. **Chỉnh sửa file config.json trực tiếp:**
   ```bash
   vi src/elasticsearch_mcp/config.json
   ```

2. **Sử dụng tool `reload_config` để tải lại cấu hình:**
   - Tool này sẽ đọc lại file config.json mà không cần restart server
   - Hữu ích khi bạn muốn thay đổi allowed_base_directory

3. **Sử dụng tool `set_allowed_directory` để thay đổi thư mục được phép:**
   - Thay đổi tạm thời trong runtime
   - Không lưu vào file config.json

### Ví dụ sử dụng

```bash
# Copy file mẫu
cp src/elasticsearch_mcp/config.example.json src/elasticsearch_mcp/config.json

# Chỉnh sửa theo nhu cầu
vi src/elasticsearch_mcp/config.json

# Restart server hoặc sử dụng reload_config tool
```

### Lưu ý bảo mật

- `allowed_base_directory` giới hạn quyền truy cập file của agent
- Chỉ có thể truy cập files/directories bên trong thư mục này
- Không thể truy cập các thư mục hệ thống quan trọng
