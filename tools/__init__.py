# Tools module initialization
import logging
import os
import sys

# Add the parent directory to sys.path to allow importing main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup logging
logger = logging.getLogger("mcp_server.tools")
logger.info("Initializing tools module")

# Import functions from tools/kubernetes/documentation.py
from tools.kubernetes.documentation import read_documentation, search_documentation, recommend

# Import the tool registry from main
from main import tool_registry

# Directly register the tools to the tool_registry
logger.info("Manually registering Kubernetes tools")
tool_registry["k8s_read_documentation"] = read_documentation
tool_registry["k8s_search_documentation"] = search_documentation
tool_registry["k8s_recommend"] = recommend

logger.info(f"Tools registered: {list(tool_registry.keys())}")