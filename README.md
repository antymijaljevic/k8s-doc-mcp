# Kubernetes Documentation MCP Server

A Model Context Protocol (MCP) server for accessing Kubernetes documentation, designed for integration with AI assistants like Claude.

## Features

- **Read Documentation**: Fetch and convert Kubernetes documentation pages to markdown format
- **Search Documentation**: Search Kubernetes documentation using keywords
- **Recommend Related Content**: Get content recommendations for Kubernetes documentation pages

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python main.py
```

The server will start on http://localhost:8000 by default.

## Using the Kubernetes Documentation Tools

This MCP server provides three main tools for working with Kubernetes documentation:

1. **k8s_read_documentation**: Fetches a Kubernetes documentation page and converts it to markdown
   - Parameters:
     - `url`: URL of the K8s documentation page (must be from kubernetes.io/docs)
     - `max_length`: Maximum number of characters to return (default: 5000)
     - `start_index`: Starting character index for pagination (default: 0)

2. **k8s_search_documentation**: Searches the Kubernetes documentation
   - Parameters:
     - `search_phrase`: The search query
     - `limit`: Maximum number of results to return (default: 10)

3. **k8s_recommend**: Gets content recommendations for a K8s documentation page
   - Parameters:
     - `url`: URL of the K8s documentation page to get recommendations for

## Example Client

Run the example client script to see how to use the Kubernetes documentation MCP server:

```bash
python k8s_client_example.py
```

## Integration with AI Assistants

### Claude Desktop Integration

Add this to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "k8s-docs-mcp": {
      "command": "python3",
      "args": [
        "/path/to/this/repo/main.py"
      ],
      "env": {
        "PORT": "8000",
        "HOST": "0.0.0.0"
      }
    }
  }
}
```

### Cursor Integration

Configure Cursor to connect to this MCP server by setting the API endpoint to `http://localhost:8000`.