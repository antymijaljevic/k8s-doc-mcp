#!/bin/bash

# Script to kill any processes using port 8000 and free it for MCP client
# This script can be used with the MCP client configuration

# Default port
PORT=8000

echo "Checking for processes using port $PORT..."
# Find processes using the port
port_processes=$(lsof -ti:$PORT)

if [ -n "$port_processes" ]; then
  echo "Found processes using port $PORT: $port_processes"
  echo "Killing processes..."
  kill $port_processes
  sleep 2
  
  # Check if some processes are still using the port (force kill)
  stubborn_processes=$(lsof -ti:$PORT)
  if [ -n "$stubborn_processes" ]; then
    echo "Some processes still running. Force killing..."
    kill -9 $stubborn_processes
    sleep 2
  fi
else
  echo "No processes found using port $PORT"
fi

# Verify the port is now free
if lsof -ti:$PORT >/dev/null; then
  echo "WARNING: Port $PORT is still in use despite attempts to free it."
  echo "You may want to restart your system or try a different port."
  exit 1
else
  echo "Port $PORT is now free and available for the MCP client"
  echo ""
  echo "MCP client configuration:"
  echo ""
  echo '"k8s-docs-mcp": {'
  echo '  "command": "/opt/homebrew/bin/python3",'
  echo '  "args": ['
  echo '    "/Users/amijaljevic/Downloads/k8s-doc-mcp/run_server.py"'
  echo '  ],'
  echo '  "env": {'
  echo '    "PORT": "8000",'
  echo '    "HOST": "0.0.0.0",'
  echo '    "TIMEOUT": "60",'
  echo '    "LOG_LEVEL": "DEBUG"'
  echo '  }'
  echo '}'
fi 