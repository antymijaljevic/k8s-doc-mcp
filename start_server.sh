#!/bin/bash

# Script to kill any processes using port 8000 and start the k8s-doc-mcp server

echo "Checking for processes using port 8000..."
# Find processes using port 8000
port_processes=$(lsof -ti:8000)

if [ -n "$port_processes" ]; then
  echo "Found processes using port 8000: $port_processes"
  echo "Killing processes..."
  kill $port_processes
  sleep 1
  
  # Check if some processes are still using the port (force kill)
  stubborn_processes=$(lsof -ti:8000)
  if [ -n "$stubborn_processes" ]; then
    echo "Some processes still running. Force killing..."
    kill -9 $stubborn_processes
    sleep 1
  fi
else
  echo "No processes found using port 8000"
fi

# Verify the port is now free
if lsof -ti:8000 >/dev/null; then
  echo "ERROR: Port 8000 is still in use. Failed to free up the port."
  exit 1
else
  echo "Port 8000 is free"
fi

# echo "Starting k8s-doc-mcp server..."
# # Start the server using the Homebrew Python installation
# /opt/homebrew/bin/python3 /Users/amijaljevic/Downloads/k8s-doc-mcp/main.py 