#!/usr/bin/env python3
"""
Test script to diagnose tool registration issues
"""
import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=getattr(logging, "DEBUG"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("test_script")

# Initialize tool registry
tool_registry = {}

def register_tool(name):
    def decorator(func):
        logger.info(f"Registering tool: {name}")
        tool_registry[name] = func
        return func
    return decorator

logger.info("Importing tools/kubernetes/documentation.py directly")

# Try direct import of documentation module
try:
    # Import function without register_tool decorator
    # Add the parent directory to sys.path to ensure imports work
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    from tools.kubernetes.documentation import read_documentation, search_documentation, recommend
    
    # Manually register the tools
    tool_registry["k8s_read_documentation"] = read_documentation
    tool_registry["k8s_search_documentation"] = search_documentation
    tool_registry["k8s_recommend"] = recommend
    
    logger.info(f"Successfully registered tools: {list(tool_registry.keys())}")
    
    # Test a tool call
    logger.info("Testing k8s_read_documentation tool...")
    result = read_documentation(url="https://kubernetes.io/docs/concepts/workloads/pods/", max_length=100)
    logger.info(f"Tool returned: {result.keys() if isinstance(result, dict) else 'Error'}")
    
except Exception as e:
    logger.error(f"Error: {str(e)}")
    import traceback
    logger.error(traceback.format_exc())

logger.info("Test complete") 