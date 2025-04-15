#!/usr/bin/env python3
"""
Improved server script to run the Kubernetes Documentation MCP Server
This script avoids circular import issues by setting up the FastAPI app
and registering tools separately.
"""
import os
import sys
import json
import logging
from typing import Dict, List, Optional, Any, Union
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename=os.getenv("LOG_FILE"),  # None means log to stdout
)
logger = logging.getLogger("mcp_server")

# Initialize tool registry
tool_registry = {}

def register_tool(name):
    """Decorator to register tools in the tool registry."""
    def decorator(func):
        logger.info(f"Registering tool: {name}")
        tool_registry[name] = func
        return func
    return decorator

# Import tools directly
try:
    from tools.kubernetes.documentation import read_documentation, search_documentation, recommend
    
    # Register tools manually
    tool_registry["k8s_read_documentation"] = read_documentation
    tool_registry["k8s_search_documentation"] = search_documentation
    tool_registry["k8s_recommend"] = recommend
    
    logger.info(f"Successfully registered tools: {list(tool_registry.keys())}")
except Exception as e:
    logger.error(f"Error importing and registering tools: {str(e)}")
    import traceback
    logger.error(traceback.format_exc())

# Define models
class ToolParameter(BaseModel):
    name: str
    value: Any

class ToolCall(BaseModel):
    name: str
    parameters: List[ToolParameter]

class ToolRequest(BaseModel):
    tool_calls: List[ToolCall]
    
class ToolResponseItem(BaseModel):
    tool_name: str
    output: Any
    error: Optional[str] = None

class ToolResponse(BaseModel):
    responses: List[ToolResponseItem]

# Create FastAPI app
app = FastAPI(title="Kubernetes Documentation MCP Server")

# CORS settings
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basic security check if enabled
async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    if os.getenv("ENABLE_AUTH", "false").lower() == "true":
        expected_key = os.getenv("API_KEY")
        if not expected_key or x_api_key != expected_key:
            raise HTTPException(status_code=401, detail="Invalid API key")
    return True

# Routes
@app.get("/")
async def root():
    return {"message": "Kubernetes Documentation MCP Server", "version": "0.1.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/tool", response_model=ToolResponse)
async def handle_tool_call(request: ToolRequest, authorized: bool = Depends(verify_api_key)):
    responses = []
    
    for tool_call in request.tool_calls:
        tool_name = tool_call.name
        
        if tool_name not in tool_registry:
            responses.append(ToolResponseItem(
                tool_name=tool_name,
                output=None,
                error=f"Tool '{tool_name}' not found"
            ))
            continue
            
        tool_func = tool_registry[tool_name]
        params = {param.name: param.value for param in tool_call.parameters}
        
        try:
            result = tool_func(**params)
            responses.append(ToolResponseItem(
                tool_name=tool_name,
                output=result
            ))
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {str(e)}")
            responses.append(ToolResponseItem(
                tool_name=tool_name,
                output=None,
                error=str(e)
            ))
    
    return ToolResponse(responses=responses)

# Raw request handler (alternative for compatibility)
@app.post("/raw_tool")
async def handle_raw_tool_call(request: Request, authorized: bool = Depends(verify_api_key)):
    try:
        data = await request.json()
        tool_name = data.get("name")
        parameters = data.get("parameters", {})
        
        if tool_name not in tool_registry:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
            
        tool_func = tool_registry[tool_name]
        result = tool_func(**parameters)
        
        return {
            "tool_name": tool_name,
            "output": result,
            "error": None
        }
    except Exception as e:
        logger.error(f"Error in raw tool call: {str(e)}")
        return {
            "tool_name": tool_name if 'tool_name' in locals() else "unknown",
            "output": None,
            "error": str(e)
        }

@app.get("/tools/list")
async def list_tools(authorized: bool = Depends(verify_api_key)):
    """List all available tools."""
    logger.info(f"Available tools: {list(tool_registry.keys())}")
    return {"tools": list(tool_registry.keys())}

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    timeout = int(os.getenv("TIMEOUT", "60"))  # Default timeout is 60 seconds
    
    logger.info(f"Starting MCP server on {host}:{port} with timeout {timeout}s")
    
    # Configure uvicorn with timeout settings
    uvicorn.run(
        "run_server:app", 
        host=host, 
        port=port, 
        reload=True,
        timeout_keep_alive=timeout,  # Keep-alive timeout
        timeout_graceful_shutdown=timeout  # Graceful shutdown timeout
    ) 