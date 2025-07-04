# Elasticsearch Auto-Setup Feature

## 🚀 Tính năng mới: Tự động setup Elasticsearch

Server MCP Elasticsearch hiện đã có khả năng **tự động setup Elasticsearch** bằng Docker nếu chưa được cấu hình hoặc không thể kết nối.

## 📋 Cách hoạt động

### 1. **Auto-detection khi khởi động**
Khi server khởi động, nó sẽ:
- ✅ Kiểm tra cấu hình Elasticsearch hiện tại
- ✅ Thử kết nối đến Elasticsearch
- ✅ Nếu không kết nối được → Tự động setup Docker containers

### 2. **Docker Container Setup**
Nếu cần setup, server sẽ:
- 🐳 Tạo Elasticsearch container với cấu hình tối ưu
- 📊 Tạo Kibana container (tùy chọn)
- ⚙️ Cập nhật file `config.json` tự động
- 🔄 Reload configuration trong runtime

## 🛠️ Tools mới

### `setup_elasticsearch`
Setup Elasticsearch bằng Docker (có thể gọi thủ công)

**Parameters:**
- `include_kibana` (boolean, default: true) - Có setup Kibana không
- `force_recreate` (boolean, default: false) - Force tạo lại containers

**Ví dụ:**
```bash
# Setup với Kibana
"Hãy setup Elasticsearch với Kibana"

# Setup chỉ Elasticsearch
"Setup Elasticsearch nhưng không cần Kibana"

# Force recreate containers
"Setup lại Elasticsearch từ đầu"
```

### `elasticsearch_status`
Kiểm tra trạng thái containers và cấu hình

**Ví dụ:**
```bash
"Kiểm tra trạng thái Elasticsearch"
"Elasticsearch đang chạy không?"
```

## ⚙️ Cấu hình

### File config.json mới
```json
{
  "elasticsearch": {
    "host": "localhost",
    "port": 9200,
    "auto_setup": true,
    "docker_image": "docker.elastic.co/elasticsearch/elasticsearch:8.14.1"
  },
  "kibana": {
    "enabled": true,
    "host": "localhost",
    "port": 5601,
    "docker_image": "docker.elastic.co/kibana/kibana:8.14.1"
  },
  "server": {
    "auto_setup_elasticsearch": true
  }
}
```

### Tắt auto-setup
Để tắt tính năng auto-setup, set:
```json
{
  "server": {
    "auto_setup_elasticsearch": false
  }
}
```

## 🐳 Docker Requirements

### Prerequisites
- Docker Desktop phải được cài đặt và chạy
- User phải có quyền truy cập Docker
- Port 9200 (Elasticsearch) và 5601 (Kibana) phải available

### Container Names
- Elasticsearch: `elasticsearch-mcp`
- Kibana: `kibana-mcp`

### Container Configuration
- **Memory**: 512MB cho Elasticsearch
- **Restart Policy**: unless-stopped
- **Network**: Bridge network với linking
- **Persistence**: Data không persist (development mode)

## 📊 Monitoring & Logs

### Server Startup Logs
```bash
🔧 Checking Elasticsearch configuration...
✅ Elasticsearch already configured  # Nếu đã có
# Hoặc
🚀 Creating new Elasticsearch container elasticsearch-mcp  # Nếu setup mới
📦 Container elasticsearch-mcp created
⏳ Waiting for Elasticsearch at localhost:9200...
✅ Elasticsearch is ready!
🎉 Elasticsearch setup completed!
```

### Status Check
Sử dụng tool `elasticsearch_status` để xem:
- Container existence và status
- Running ports và URLs
- Current configuration

## 🔧 Troubleshooting

### Common Issues

**1. Docker không chạy**
```
Error: Cannot connect to Docker. Is Docker running?
```
→ Khởi động Docker Desktop

**2. Port đã được sử dụng**
```
Error: Port 9200 already in use
```
→ Stop existing Elasticsearch hoặc change port

**3. Permission denied**
```
Error: Permission denied accessing Docker
```
→ Add user to docker group hoặc run with sudo

### Manual Commands

**Stop containers:**
```bash
docker stop elasticsearch-mcp kibana-mcp
```

**Remove containers:**
```bash
docker rm elasticsearch-mcp kibana-mcp
```

**Check container status:**
```bash
docker ps -a | grep mcp
```

## 🎯 Use Cases

### 1. **Development Setup**
- Clone project → Run server → Auto Elasticsearch setup
- No manual Docker commands needed

### 2. **Demo Environment**
- Quick setup for demonstrations
- Self-contained environment

### 3. **Testing**
- Fresh Elasticsearch for each test run
- Force recreate containers

### 4. **Production**
- Disable auto-setup
- Use existing Elasticsearch cluster
- Manual configuration

## ✨ Benefits

1. **Zero Configuration**: Setup tự động khi cần
2. **Developer Friendly**: Không cần biết Docker commands
3. **Consistent Environment**: Same setup across machines
4. **Hot Reload**: Configuration updates without restart
5. **Status Monitoring**: Easy health checking

---

**🎉 Giờ đây việc setup Elasticsearch đã được tự động hóa hoàn toàn!** Chỉ cần chạy server và mọi thứ sẽ được chuẩn bị sẵn sàng! 🚀
