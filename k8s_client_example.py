#!/usr/bin/env python3
import requests
import json
import sys

# MCP Server URL
MCP_SERVER_URL = "http://localhost:8000"

def call_tool(tool_name, **parameters):
    """Call a tool on the MCP server."""
    # Convert parameters to the expected format
    params = [{"name": name, "value": value} for name, value in parameters.items()]
    
    # Create the request payload
    payload = {
        "tool_calls": [
            {
                "name": tool_name,
                "parameters": params
            }
        ]
    }
    
    # Make the request
    response = requests.post(
        f"{MCP_SERVER_URL}/tool",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return None
        
    result = response.json()
    
    # Return the first tool response
    if result.get("responses") and len(result["responses"]) > 0:
        tool_response = result["responses"][0]
        if tool_response.get("error"):
            print(f"Tool Error: {tool_response['error']}")
        return tool_response.get("output")
    
    return None

def list_available_tools():
    """List all available tools on the server."""
    response = requests.get(f"{MCP_SERVER_URL}/tools/list")
    if response.status_code == 200:
        return response.json().get("tools", [])
    else:
        print(f"Error listing tools: {response.status_code} - {response.text}")
        return []

def ping_server():
    """Check if the server is running."""
    try:
        response = requests.get(f"{MCP_SERVER_URL}/health")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False

def display_markdown_content(content, max_lines=25):
    """Display markdown content with optional truncation."""
    lines = content.split('\n')
    if len(lines) > max_lines:
        print('\n'.join(lines[:max_lines]))
        print(f"\n... (Truncated, {len(lines) - max_lines} more lines)")
    else:
        print(content)

def main():
    """Main function to demonstrate K8s MCP client usage."""
    print("Kubernetes Documentation MCP Client Example")
    print("-----------------------------------------")
    
    # Check if server is running
    if not ping_server():
        print("Error: MCP server is not running or not accessible.")
        print(f"Make sure the server is running at {MCP_SERVER_URL}")
        sys.exit(1)
    
    print("Server is running!")
    
    # List available tools
    print("\nAvailable tools:")
    tools = list_available_tools()
    k8s_tools = [tool for tool in tools if tool.startswith('k8s_')]
    
    if not k8s_tools:
        print("No Kubernetes documentation tools found!")
        sys.exit(1)
        
    for tool in k8s_tools:
        print(f"- {tool}")
    
    # Example tool calls
    print("\nPerforming example Kubernetes documentation tool calls:")
    
    # Example 1: Read documentation
    print("\n1. Reading Kubernetes Pod documentation:")
    result = call_tool("k8s_read_documentation", 
                      url="https://kubernetes.io/docs/concepts/workloads/pods/")
    
    if result and "content" in result:
        print(f"Title: {result.get('title', 'Unknown')}")
        print(f"Total length: {result.get('total_length', 0)} characters")
        print(f"Truncated: {result.get('is_truncated', False)}")
        print("\nContent preview:")
        display_markdown_content(result["content"])
    
    # Example 2: Search documentation
    print("\n2. Searching for 'deployment' in Kubernetes documentation:")
    result = call_tool("k8s_search_documentation", search_phrase="deployment", limit=5)
    
    if result and "results" in result:
        print(f"Query: {result.get('query')}")
        print(f"Total results: {result.get('total_results', 0)}")
        print("\nSearch results:")
        for idx, item in enumerate(result["results"], 1):
            print(f"{idx}. {item['title']}")
            print(f"   URL: {item['url']}")
            if "excerpt" in item:
                print(f"   {item['excerpt']}")
            print()
    
    # Example 3: Get recommendations
    print("\n3. Getting recommendations for Kubernetes Pod documentation:")
    result = call_tool("k8s_recommend", 
                      url="https://kubernetes.io/docs/concepts/workloads/pods/")
    
    if result:
        print("\nHighly rated related content:")
        for item in result.get("highly_rated", []):
            print(f"- {item['title']}")
            print(f"  URL: {item['url']}")
            if "context" in item:
                print(f"  Context: {item['context']}")
            print()
        
        print("\nSimilar content:")
        for item in result.get("similar", []):
            print(f"- {item['title']}")
            print(f"  URL: {item['url']}")
            if "context" in item:
                print(f"  Context: {item['context']}")
        
        print("\nSuggested journey (what to read next):")
        for item in result.get("journey", []):
            print(f"- {item['title']}")
            print(f"  URL: {item['url']}")
            if "context" in item:
                print(f"  Context: {item['context']}")
    
    print("\nAll operations completed!")

if __name__ == "__main__":
    main() 