# Elasticsearch MCP Server

A Model Context Protocol (MCP) server that provides integration with Elasticsearch, allowing you to search, index, and manage documents through AI assistants.

## Features

### Tools Available:
- **search**: Search documents in an Elasticsearch index with multi-field queries
- **index_document**: Index new documents into Elasticsearch
- **create_index**: Create new indices with custom mapping and settings
- **get_document**: Retrieve a specific document by ID
- **delete_document**: Delete a document by ID
- **list_indices**: List all available Elasticsearch indices
- **delete_index**: Delete an entire index

### Resources:
- **Index Information**: Browse Elasticsearch indices as resources to view mappings, settings, and stats

## Prerequisites

1. **Elasticsearch**: Running Elasticsearch instance (default: localhost:9200)
2. **Python**: Python 3.13 or higher
3. **UV**: Package manager for dependency management

## Installation

1. Clone or create the project:
```bash
git clone <repository-url>
cd elasticsearch-mcp
```

2. Install dependencies:
```bash
uv sync
```

3. Make sure Elasticsearch is running:
```bash
# If using Docker (from your existing setup):
docker-compose up -d
```

## Usage with Claude Desktop

The MCP server has been automatically configured to work with Claude Desktop. You can now use the following commands in Claude:

### Searching Documents
```
Search for "authentication" in the manually_indexed_docs index
```

### Indexing New Documents
```
Index a new document about API endpoints into the manually_indexed_docs index
```

### Managing Indices
```
List all available Elasticsearch indices
```

```
Create a new index called "new_docs" with text mapping
```

## Configuration

The server connects to Elasticsearch at `localhost:9200` by default. To modify the connection settings, edit the `get_es_client()` function in `src/elasticsearch_mcp/server.py`:

```python
def get_es_client():
    global es_client
    if es_client is None:
        es_client = Elasticsearch([
            {'host': 'your-host', 'port': 9200}
            # Add authentication if needed:
            # http_auth=('username', 'password'),
            # use_ssl=True,
        ])
    return es_client
```

### Claude Desktop Configuration

The server is automatically configured at:
- **MacOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

```json
"mcpServers": {
  "elasticsearch-mcp": {
    "command": "uv",
    "args": [
      "--directory",
      "/Users/nguyenkimchung/AgentKnowledgeMCP",
      "run",
      "elasticsearch-mcp"
    ]
  }
}
```

## Development

To run the server directly for testing:
```bash
uv run elasticsearch-mcp
```

The server communicates via stdin/stdout following the MCP protocol.

### Debugging with MCP Inspector

For debugging, use the MCP Inspector:
```bash
npx @modelcontextprotocol/inspector uv --directory /Users/nguyenkimchung/AgentKnowledgeMCP run elasticsearch-mcp
```

## Architecture

- **MCP Protocol**: Uses the Model Context Protocol for AI assistant integration
- **Elasticsearch Client**: Uses elasticsearch<7.14.0 for compatibility
- **Async Architecture**: Built with asyncio for concurrent operations

## Example Workflows

1. **Document Discovery**: Use the resources feature to browse available indices
2. **Content Search**: Use multi-field search with boosted fields (title^3, summary^2, etc.)
3. **Document Management**: Index, update, and delete documents as needed
4. **Index Management**: Create and configure new indices for different document types

## Vietnamese Content Support

The server includes proper Unicode handling for Vietnamese text content, ensuring accurate indexing and search results for multilingual documentation.

## Error Handling

The server includes comprehensive error handling for:
- Elasticsearch connection issues
- Invalid index or document operations
- Malformed queries
- Resource not found errors

All errors are returned as descriptive text responses to help with debugging.