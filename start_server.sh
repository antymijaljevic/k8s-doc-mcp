#!/bin/bash

# Script to kill any processes using port 8000 and free it for MCP client
# This script also supports using a custom port if 8000 is busy

# Default port
PORT=8000

# Check if a custom port was provided
if [ -n "$1" ] && [[ "$1" =~ ^[0-9]+$ ]]; then
  PORT=$1
  echo "Using custom port: $PORT"
fi

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
  echo "Starting server with debug logging using run_server.py..."
  
  # Start the server in debug mode to see tool registration
  LOG_LEVEL=DEBUG TIMEOUT=60 PORT=$PORT /opt/homebrew/bin/python3 run_server.py
fi 