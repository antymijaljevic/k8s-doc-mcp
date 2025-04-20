🔍 Key Features

Fetches Kubernetes documentation pages and converts them into Markdown format, making them easily readable and integrable into various development environments.

Search Documentation
Utilizes the official Kubernetes Documentation Search API to perform keyword-based searches across Kubernetes documentation, returning relevant results to assist in development tasks.

Recommendations
Provides content recommendations related to specific Kubernetes documentation pages, helping developers discover additional relevant information and best practices.

⚙️ Tools Provided
The server exposes the following tools through the MCP interface:​

read_documentation(url: str) -> str
Fetches and converts an Kubernetes documentation page to Markdown format.​

search_documentation(search_phrase: str, limit: int) -> list[dict]
Performs a search using the Kubernetes Documentation Search API and returns a list of relevant documentation entries.​

recommend(url: str) -> list[dict]
Provides a list of recommended Kubernetes documentation pages related to the specified URL.