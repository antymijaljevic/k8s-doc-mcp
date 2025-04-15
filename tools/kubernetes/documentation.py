import os
import re
import json
import logging
import requests
import sys
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional, Union

# No longer needed since tools/__init__.py will register the tools
# import importlib.util
# spec = importlib.util.spec_from_file_location("main", 
#     os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "main.py"))
# main_module = importlib.util.module_from_spec(spec)
# spec.loader.exec_module(main_module)
# register_tool = main_module.register_tool

from . import logger

# Add debug logging for tool registration
logger.info("Loading Kubernetes documentation tools...")

# Base URL for Kubernetes documentation
K8S_DOCS_BASE_URL = "https://kubernetes.io/docs"
K8S_API_DOCS_BASE_URL = "https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.28"
K8S_SEARCH_API_URL = "https://kubernetes.io/docs/search/"

# Optional: Cache directory for storing fetched documentation
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "cache", "k8s_docs")
USE_CACHE = True

def ensure_cache_dir():
    """Ensure cache directory exists."""
    if USE_CACHE and not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR, exist_ok=True)

def get_cache_path(url: str) -> str:
    """Get cache file path for a URL."""
    # Create safe filename from URL
    filename = re.sub(r'[^\w]', '_', url) + '.html'
    return os.path.join(CACHE_DIR, filename)

def fetch_url(url: str) -> str:
    """Fetch content from URL with caching."""
    if not url.startswith(("https://kubernetes.io", "http://kubernetes.io")):
        raise ValueError(f"URL must be from kubernetes.io domain: {url}")
    
    # Check cache first if enabled
    if USE_CACHE:
        ensure_cache_dir()
        cache_path = get_cache_path(url)
        if os.path.exists(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                logger.info(f"Using cached content for {url}")
                return f.read()
    
    # Fetch from web
    logger.info(f"Fetching content from {url}")
    headers = {
        "User-Agent": "Kubernetes-Documentation-MCP-Server/1.0"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    content = response.text
    
    # Save to cache if enabled
    if USE_CACHE:
        with open(get_cache_path(url), 'w', encoding='utf-8') as f:
            f.write(content)
    
    return content

def html_to_markdown(html_content: str) -> str:
    """Convert HTML content to markdown with enhanced formatting."""
    # First parse with BeautifulSoup to clean and structure the HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove navigation, footers, etc.
    for elem in soup.select('nav, footer, script, style, .js-toolbar-action'):
        if elem:
            elem.decompose()
    
    # Extract the main content area if possible
    main_content = soup.select_one('main') or soup.select_one('article') or soup.select_one('body')
    
    # Simple HTML to markdown conversion
    html_to_convert = str(main_content) if main_content else str(soup)
    
    # Basic conversion of common HTML elements to markdown
    md_content = html_to_convert
    
    # Replace headings
    for i in range(6, 0, -1):
        pattern = f'<h{i}[^>]*>(.*?)</h{i}>'
        replacement = '#' * i + ' \\1\n\n'
        md_content = re.sub(pattern, replacement, md_content, flags=re.DOTALL)
    
    # Replace paragraphs
    md_content = re.sub(r'<p[^>]*>(.*?)</p>', '\\1\n\n', md_content, flags=re.DOTALL)
    
    # Replace links
    md_content = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', '[\\2](\\1)', md_content, flags=re.DOTALL)
    
    # Replace lists
    md_content = re.sub(r'<ul[^>]*>(.*?)</ul>', '\\1\n', md_content, flags=re.DOTALL)
    md_content = re.sub(r'<ol[^>]*>(.*?)</ol>', '\\1\n', md_content, flags=re.DOTALL)
    md_content = re.sub(r'<li[^>]*>(.*?)</li>', '- \\1\n', md_content, flags=re.DOTALL)
    
    # Replace code blocks
    md_content = re.sub(r'<pre[^>]*><code[^>]*>(.*?)</code></pre>', '```\n\\1\n```\n\n', md_content, flags=re.DOTALL)
    md_content = re.sub(r'<code[^>]*>(.*?)</code>', '`\\1`', md_content, flags=re.DOTALL)
    
    # Replace bold and italic
    md_content = re.sub(r'<strong[^>]*>(.*?)</strong>', '**\\1**', md_content, flags=re.DOTALL)
    md_content = re.sub(r'<em[^>]*>(.*?)</em>', '*\\1*', md_content, flags=re.DOTALL)
    
    # Replace line breaks
    md_content = re.sub(r'<br[^>]*>', '\n', md_content)
    
    # Clean up HTML tags
    md_content = re.sub(r'<[^>]*>', '', md_content)
    
    # Clean up HTML entities
    md_content = md_content.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
    
    # Clean up multiple blank lines
    md_content = re.sub(r'\n{3,}', '\n\n', md_content)
    
    return md_content

def read_documentation(url: str, max_length: int = 5000, start_index: int = 0) -> Dict[str, Any]:
    """
    Fetch and convert a Kubernetes documentation page to markdown format.
    
    Args:
        url: URL of the Kubernetes documentation page to read
        max_length: Maximum number of characters to return
        start_index: Starting character index for returned content
    
    Returns:
        Dict containing markdown content and metadata
    """
    logger.info(f"Tool k8s_read_documentation called with URL: {url}")
    try:
        # Validate URL
        if not url.startswith(("https://kubernetes.io/docs", "http://kubernetes.io/docs")):
            return {
                "error": "URL must be from kubernetes.io/docs domain"
            }
        
        # Fetch content
        html_content = fetch_url(url)
        
        # Convert to markdown
        md_content = html_to_markdown(html_content)
        
        # Get the title
        soup = BeautifulSoup(html_content, 'html.parser')
        title = soup.title.string if soup.title else url.split('/')[-1]
        
        # Calculate content length and truncate if needed
        total_length = len(md_content)
        end_index = min(start_index + max_length, total_length)
        truncated_content = md_content[start_index:end_index]
        
        # Prepare response
        response = {
            "title": title,
            "url": url,
            "content": truncated_content,
            "start_index": start_index,
            "end_index": end_index,
            "total_length": total_length,
            "is_truncated": end_index < total_length
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Error reading Kubernetes documentation: {str(e)}")
        return {"error": str(e)}

def search_documentation(search_phrase: str, limit: int = 10) -> Dict[str, Any]:
    """
    Search Kubernetes documentation using a search phrase.
    
    Args:
        search_phrase: The search phrase to look for
        limit: Maximum number of results to return
    
    Returns:
        Dict containing search results
    """
    logger.info("Tool k8s_search_documentation called")
    try:
        # Use Kubernetes site search or Google CSE
        # Here we're simulating a search by directly querying the K8s site
        # In a production environment, you might want to use a proper search API
        
        search_url = f"{K8S_SEARCH_API_URL}?q={search_phrase}"
        headers = {
            "User-Agent": "Kubernetes-Documentation-MCP-Server/1.0",
            "Accept": "application/json"
        }
        
        # For demonstration, we'll fetch the search page and parse results
        # This is a simplification; a real implementation would use the search API
        response = requests.get(search_url, headers=headers)
        
        # Mock search results based on common K8s topics
        # In a real implementation, we would parse the actual search results
        mock_results = []
        keywords = search_phrase.lower().split()
        
        # Common K8s topics for demonstration
        topics = [
            {"title": "Pods", "url": "https://kubernetes.io/docs/concepts/workloads/pods/"},
            {"title": "Deployments", "url": "https://kubernetes.io/docs/concepts/workloads/controllers/deployment/"},
            {"title": "Services", "url": "https://kubernetes.io/docs/concepts/services-networking/service/"},
            {"title": "ConfigMaps", "url": "https://kubernetes.io/docs/concepts/configuration/configmap/"},
            {"title": "Secrets", "url": "https://kubernetes.io/docs/concepts/configuration/secret/"},
            {"title": "Volumes", "url": "https://kubernetes.io/docs/concepts/storage/volumes/"},
            {"title": "Namespaces", "url": "https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/"},
            {"title": "Kubectl Commands", "url": "https://kubernetes.io/docs/reference/kubectl/"},
            {"title": "Kubernetes API", "url": "https://kubernetes.io/docs/reference/kubernetes-api/"},
            {"title": "Cluster Architecture", "url": "https://kubernetes.io/docs/concepts/architecture/"},
        ]
        
        # Filter topics based on keywords
        for topic in topics:
            for keyword in keywords:
                if keyword in topic["title"].lower():
                    excerpt = f"Documentation about Kubernetes {topic['title']}"
                    mock_results.append({
                        "title": topic["title"],
                        "url": topic["url"],
                        "excerpt": excerpt
                    })
                    break
        
        # Limit results
        if len(mock_results) > limit:
            mock_results = mock_results[:limit]
            
        # If no results found, return some common docs
        if not mock_results:
            mock_results = [
                {"title": "Kubernetes Documentation", "url": "https://kubernetes.io/docs/home/", 
                 "excerpt": "Home page for Kubernetes documentation."},
                {"title": "Kubernetes Concepts", "url": "https://kubernetes.io/docs/concepts/", 
                 "excerpt": "Overview of Kubernetes concepts and components."}
            ]
        
        return {
            "query": search_phrase,
            "results": mock_results,
            "total_results": len(mock_results)
        }
        
    except Exception as e:
        logger.error(f"Error searching Kubernetes documentation: {str(e)}")
        return {"error": str(e)}

def recommend(url: str) -> Dict[str, Any]:
    """
    Get content recommendations for a Kubernetes documentation page.
    
    Args:
        url: URL of the Kubernetes documentation page to get recommendations for
    
    Returns:
        Dict containing recommended pages with URLs, titles, and context
    """
    logger.info("Tool k8s_recommend called")
    try:
        # Validate URL
        if not url.startswith(("https://kubernetes.io/docs", "http://kubernetes.io/docs")):
            return {
                "error": "URL must be from kubernetes.io/docs domain"
            }
        
        # Extract the path components to identify the content type
        path_parts = url.replace("https://kubernetes.io/docs/", "").split("/")
        category = path_parts[0] if path_parts else ""
        
        # Generate recommendations based on the category
        recommendations = {
            "highly_rated": [],
            "new": [],
            "similar": [],
            "journey": []
        }
        
        # Map of categories to related content
        category_recommendations = {
            "concepts": [
                {"title": "Pods", "url": "https://kubernetes.io/docs/concepts/workloads/pods/"},
                {"title": "Deployments", "url": "https://kubernetes.io/docs/concepts/workloads/controllers/deployment/"},
                {"title": "Services", "url": "https://kubernetes.io/docs/concepts/services-networking/service/"},
                {"title": "Storage", "url": "https://kubernetes.io/docs/concepts/storage/"},
            ],
            "tasks": [
                {"title": "Configure a Pod to Use a ConfigMap", "url": "https://kubernetes.io/docs/tasks/configure-pod-container/configure-pod-configmap/"},
                {"title": "Configure a Pod to Use a Secret", "url": "https://kubernetes.io/docs/tasks/inject-data-application/distribute-credentials-secure/"},
                {"title": "Use Port Forwarding", "url": "https://kubernetes.io/docs/tasks/access-application-cluster/port-forward-access-application-cluster/"},
            ],
            "reference": [
                {"title": "Kubernetes API Reference", "url": "https://kubernetes.io/docs/reference/kubernetes-api/"},
                {"title": "kubectl Commands", "url": "https://kubernetes.io/docs/reference/kubectl/"},
                {"title": "Well-Known Labels, Annotations and Taints", "url": "https://kubernetes.io/docs/reference/labels-annotations-taints/"},
            ],
            "tutorials": [
                {"title": "Kubernetes Basics", "url": "https://kubernetes.io/docs/tutorials/kubernetes-basics/"},
                {"title": "Stateless Application", "url": "https://kubernetes.io/docs/tutorials/stateless-application/"},
                {"title": "Stateful Application", "url": "https://kubernetes.io/docs/tutorials/stateful-application/"},
            ]
        }
        
        # Add recommendations based on the URL category
        if category in category_recommendations:
            recommendations["similar"] = category_recommendations[category]
        else:
            # Default recommendations if category not recognized
            recommendations["similar"] = [
                {"title": "Kubernetes Concepts", "url": "https://kubernetes.io/docs/concepts/"},
                {"title": "Kubernetes Tasks", "url": "https://kubernetes.io/docs/tasks/"},
                {"title": "Kubernetes Tutorials", "url": "https://kubernetes.io/docs/tutorials/"}
            ]
        
        # Add some highly rated content
        recommendations["highly_rated"] = [
            {"title": "Kubernetes Components", "url": "https://kubernetes.io/docs/concepts/overview/components/", 
             "context": "Understanding the core components of Kubernetes architecture"},
            {"title": "Kubernetes API", "url": "https://kubernetes.io/docs/concepts/overview/kubernetes-api/", 
             "context": "How to interact with the Kubernetes API"},
            {"title": "Working with kubectl", "url": "https://kubernetes.io/docs/reference/kubectl/", 
             "context": "Essential kubectl commands for managing Kubernetes resources"}
        ]
        
        # Add some new content
        recommendations["new"] = [
            {"title": "What's new in Kubernetes v1.28", "url": "https://kubernetes.io/blog/2023/08/15/kubernetes-v1-28-release/", 
             "context": "Latest features in Kubernetes v1.28"},
            {"title": "Validating API Field Selectors", "url": "https://kubernetes.io/docs/reference/using-api/api-concepts/#field-validation", 
             "context": "New field validation features"},
            {"title": "Job API Updates", "url": "https://kubernetes.io/docs/concepts/workloads/controllers/job/", 
             "context": "Recent updates to the Job API"}
        ]
        
        # Add journey recommendations (what to read next)
        recommendations["journey"] = [
            {"title": "Kubernetes Troubleshooting", "url": "https://kubernetes.io/docs/tasks/debug/", 
             "context": "Common troubleshooting scenarios"},
            {"title": "Kubernetes Best Practices", "url": "https://kubernetes.io/docs/setup/best-practices/", 
             "context": "Best practices for configuring Kubernetes"},
            {"title": "Kubernetes Security", "url": "https://kubernetes.io/docs/concepts/security/", 
             "context": "Security concepts and best practices"}
        ]
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Error getting recommendations for Kubernetes documentation: {str(e)}")
        return {"error": str(e)}

# Log that tools were registered
logger.info("Kubernetes documentation tools registered: k8s_read_documentation, k8s_search_documentation, k8s_recommend") 