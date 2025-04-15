INFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
INFO:     Finished server process [24225]
INFO:     Stopping reloader process [24220]
2025-04-15T08:27:05.111Z [k8s-docs-mcp] [info] Initializing server...
2025-04-15T08:27:05.156Z [k8s-docs-mcp] [info] Server started and connected successfully
2025-04-15T08:27:05.157Z [k8s-docs-mcp] [info] Message from client: {"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"claude-ai","version":"0.1.0"}},"jsonrpc":"2.0","id":0}
2025-04-15 10:27:05,491 - mcp_server.tools - INFO - Initializing tools module
2025-04-15 10:27:05,568 - mcp_server.tools.kubernetes - INFO - Loading Kubernetes documentation tools...
2025-04-15 10:27:05,568 - mcp_server.tools.kubernetes - INFO - Kubernetes documentation tools registered: k8s_read_documentation, k8s_search_documentation, k8s_recommend
2025-04-15 10:27:05,570 - mcp_server.tools - INFO - Manually registering Kubernetes tools
2025-04-15 10:27:05,570 - mcp_server.tools - INFO - Tools registered: ['k8s_read_documentation', 'k8s_search_documentation', 'k8s_recommend']
2025-04-15 10:27:05,570 - mcp_server - ERROR - MISSING TOOLS: ['k8s_read_documentation', 'k8s_search_documentation', 'k8s_recommend']
2025-04-15 10:27:05,570 - mcp_server - ERROR - Make sure tools/kubernetes/documentation.py is properly importing main.register_tool
2025-04-15 10:27:05,570 - mcp_server - WARNING - Server starting with missing tools. Functionality may be limited.
2025-04-15 10:27:05,570 - mcp_server - INFO - Starting MCP server on 0.0.0.0:8000 with timeout 60s
INFO:     Will watch for changes in these directories: ['/']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [24544] using StatReload
2025-04-15 10:27:05,808 - mcp_server.tools - INFO - Initializing tools module
2025-04-15 10:27:05,865 - mcp_server.tools.kubernetes - INFO - Loading Kubernetes documentation tools...
2025-04-15 10:27:05,865 - mcp_server.tools.kubernetes - INFO - Kubernetes documentation tools registered: k8s_read_documentation, k8s_search_documentation, k8s_recommend
2025-04-15 10:27:05,868 - mcp_server.tools - INFO - Manually registering Kubernetes tools
2025-04-15 10:27:05,868 - mcp_server.tools - INFO - Tools registered: ['k8s_read_documentation', 'k8s_search_documentation', 'k8s_recommend']
INFO:     Started server process [24549]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
2025-04-15T08:28:05.158Z [k8s-docs-mcp] [info] Message from client: {"jsonrpc":"2.0","method":"notifications/cancelled","params":{"requestId":0,"reason":"Error: MCP error -32001: Request timed out"}}
2025-04-15T08:28:05.158Z [k8s-docs-mcp] [info] Client transport closed
2025-04-15T08:28:05.159Z [k8s-docs-mcp] [info] Server transport closed
2025-04-15T08:28:05.159Z [k8s-docs-mcp] [info] Client transport closed
2025-04-15T08:28:05.159Z [k8s-docs-mcp] [info] Server transport closed unexpectedly, this is likely due to the process exiting early. If you are developing this MCP server you can add output to stderr (i.e. `console.error('...')` in JavaScript, `print('...', file=sys.stderr)` in python) and it will appear in this log.
2025-04-15T08:28:05.159Z [k8s-docs-mcp] [error] Server disconnected. For troubleshooting guidance, please visit our [debugging documentation](https://modelcontextprotocol.io/docs/tools/debugging) {"context":"connection"}
INFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
INFO:     Finished server process [24549]
INFO:     Stopping reloader process [24544]
2025-04-15T08:28:09.047Z [k8s-docs-mcp] [info] Server transport closed
2025-04-15T08:28:09.047Z [k8s-docs-mcp] [info] Client transport closed
