from mcp.server.fastmcp import FastMCP
import os
import requests
from bs4 import BeautifulSoup
import re
import markdown
from urllib.parse import urlparse, urljoin

# Create an MCP server
mcp = FastMCP("k8s-doc-mcp")

# Constants based on the provided image
# The official base URL for the Kubernetes documentation
K8S_DOCS_BASE_URL = "https://kubernetes.io/docs/"
# Kubernetes does not provide a public search API endpoint.
# This is the URL of the page where client-side search can be performed,
# but it's not used by our server-side tool.
# K8S_SEARCH_API_URL = "https://kubernetes.io/search/" # Removed as the search tool is removed
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"


def clean_html(html_content):
    """
    Clean HTML content by removing unnecessary elements and formatting the content.
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove elements that are typically not part of the main content body
    for element in soup.select('nav, header, footer, .js-toc, #TableOfContents, .td-sidebar-nav, .td-page-meta, .td-navbar'):
        if element:
            element.decompose()

    # Target main content areas - adjust selectors based on typical k8s doc structure
    # This might need refinement depending on the exact page structure, but main, article, td-content are common.
    main_content_elements = soup.select('main, article, .td-content')

    if not main_content_elements:
        # If specific content areas not found, clean the whole body but be more cautious
        body = soup.find('body')
        if body:
             main_content = body
        else:
             main_content = soup # Fallback to the whole soup
    else:
        # Concatenate content from found main areas into a single BeautifulSoup object
        # This helps in processing the content as a unified block
        combined_content_soup = BeautifulSoup('', 'html.parser')
        for element in main_content_elements:
             combined_content_soup.append(element)
        main_content = combined_content_soup


    # Fix links - make relative links absolute using the defined base URL
    for a_tag in main_content.find_all('a', href=True):
        href = a_tag['href']
        parsed_href = urlparse(href)
        # If it's a relative URL or an absolute URL within the k8s domain, make it absolute using the base
        if not parsed_href.netloc or parsed_href.netloc.endswith('kubernetes.io'):
             a_tag['href'] = urljoin(K8S_DOCS_BASE_URL, href)
             # Ensure it still points to a kubernetes.io domain after joining
             if not urlparse(a_tag['href']).netloc.endswith('kubernetes.io'):
                  # If urljoin resulted in an external link unexpectedly, revert or handle
                  a_tag['href'] = href # Revert to original if joining failed to keep it internal

    # Fix images - make relative image sources absolute using the defined base URL
    for img_tag in main_content.find_all('img', src=True):
        src = img_tag['src']
        parsed_src = urlparse(src)
        if not parsed_src.netloc: # Relative URL
             img_tag['src'] = urljoin(K8S_DOCS_BASE_URL, src)
             # Ensure it still points to a kubernetes.io domain after joining
             if not urlparse(img_tag['src']).netloc.endswith('kubernetes.io'):
                  img_tag['src'] = src # Revert if joining failed to keep it internal


    # Return the cleaned HTML string representation of the content
    return str(main_content)


def html_to_markdown(html_content):
    """
    Convert HTML content to Markdown format.
    Uses the markdown library which expects HTML input.
    """
    # Use the markdown library to convert cleaned HTML to markdown
    md = markdown.markdown(html_content)

    # Additional cleaning and formatting of markdown output
    md = re.sub(r'\n{3,}', '\n\n', md)  # Replace 3 or more newlines with 2
    md = re.sub(r'^\s*$', '', md, flags=re.M) # Remove empty lines

    return md


@mcp.tool()
def read_documentation(url: str) -> str:
    """
    Fetches and converts a Kubernetes documentation page to Markdown format.

    Args:
        url (str): URL of the Kubernetes documentation page to read.
               Must be from kubernetes.io domain.

    Returns:
        str: Markdown content of the Kubernetes documentation.
    """
    # Validate URL
    parsed_url = urlparse(url)
    # Check if netloc exists and ends with kubernetes.io
    if not (parsed_url.netloc and parsed_url.netloc.endswith('kubernetes.io')):
        return "Error: URL must be from kubernetes.io domain."

    # Fetch content
    try:
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
    except requests.RequestException as e:
        return f"Error fetching documentation: {str(e)}"

    # Convert to markdown
    try:
        html_content = response.text
        # Clean the HTML using BeautifulSoup
        cleaned_html = clean_html(html_content)
        # Convert the cleaned HTML string to markdown
        markdown_content = html_to_markdown(cleaned_html)

        # Add original URL as a reference at the beginning of the markdown
        markdown_content = f"Source: {url}\n\n" + markdown_content

        return markdown_content
    except Exception as e:
        return f"Error converting to markdown: {str(e)}"


@mcp.tool()
def recommend(url: str) -> list:
    """
    Provides a list of recommended Kubernetes documentation pages related to the specified URL.

    This simulates a recommendation system by analyzing the page content
    and finding related pages based on links and context.

    Args:
        url (str): URL of the Kubernetes documentation page to get recommendations for.

    Returns:
        list[dict]: List of recommended pages with URLs, titles, and context.
                    Returns a list containing an error dict if fetching or processing fails.
    """
    # Validate URL
    parsed_url = urlparse(url)
    if not (parsed_url.netloc and parsed_url.netloc.endswith('kubernetes.io')):
        return [{"error": "URL must be from kubernetes.io domain."}]

    # Ensure the URL path starts with /docs/
    if not parsed_url.path.startswith('/docs/'):
         return [{"error": "Recommendations are currently limited to URLs within the /docs/ path."}]

    try:
        # Fetch the page
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find related links
        related_links = []

        # Look for "See Also", "Related", "Next Steps", "What's Next" or similar sections
        # Adding more variations or patterns might improve detection
        see_also_headings = soup.find_all(['h2', 'h3', 'h4'],
                                        string=re.compile(r'see also|related|next steps|what\'s next|further reading', re.I))

        for heading in see_also_headings:
            next_element = heading.find_next_sibling()
            # Look within the elements following the heading until another heading or a horizontal rule is found
            while next_element and next_element.name not in ['h2', 'h3', 'h4', 'hr']:
                links = next_element.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    # Process only links within the kubernetes.io domain, specifically /docs/ path
                    # Avoid anchors within the same page (#...) and links to specific files (.pdf, .zip)
                    parsed_href = urlparse(href)
                    # Check if the link is relative or points to kubernetes.io AND is within /docs/ path
                    if (not parsed_href.netloc or parsed_href.netloc.endswith('kubernetes.io')) \
                       and parsed_href.path.startswith('/docs/') \
                       and not parsed_href.fragment \
                       and not re.search(r'\.(pdf|zip)$', href, re.I):
                         full_url = urljoin(K8S_DOCS_BASE_URL, href)
                         link_text = link.get_text(strip=True)
                         # Use link text if it's substantial, otherwise derive from URL path
                         title = link_text if link_text and len(link_text) > 3 and not re.match(r'^\s*<img.*?$', link_text, re.I) else parsed_href.path.split('/')[-1].replace('-', ' ').title()

                         related_links.append({
                            'url': full_url,
                            'title': title,
                            'context': f'Link near "{heading.get_text(strip=True)}"'
                        })
                next_element = next_element.find_next_sibling()

        # If not enough related links found in specific sections, look in main content (fallback)
        if len(related_links) < 3:
            main_content = soup.select_one('main') or soup.select_one('.td-content') or soup
            if main_content:
                content_links = main_content.find_all('a', href=True)

                for link in content_links:
                    href = link['href']
                    # Apply similar filtering as above
                    parsed_href = urlparse(href)
                    if (not parsed_href.netloc or parsed_href.netloc.endswith('kubernetes.io')) \
                       and parsed_href.path.startswith('/docs/') \
                       and not parsed_href.fragment \
                       and not re.search(r'\.(pdf|zip)$', href, re.I):
                        full_url = urljoin(K8S_DOCS_BASE_URL, href)
                        link_text = link.get_text(strip=True)
                        # Avoid using very short, generic, or image-alt link text in fallback
                        if link_text and len(link_text) > 5 and not re.match(r'^(home|docs|guide|learn|reference)$', link_text, re.I) and not re.match(r'^\s*<img.*?$', link_text, re.I):
                             title = link_text
                             related_links.append({
                                'url': full_url,
                                'title': title,
                                'context': 'Link in content (fallback)'
                            })
            else:
                 # Handle case where no main content area was found
                 pass # No links from main content if main_content is None


        # Remove duplicates and the original URL, limit results
        unique_urls = set()
        unique_links = []
        # Normalize original URL path for comparison, remove trailing slash if it exists
        original_url_normalized = urljoin(K8S_DOCS_BASE_URL, urlparse(url).path).rstrip('/')

        for link in related_links:
            # Normalize candidate URL path for comparison, remove trailing slash
            candidate_url_normalized = urljoin(K8S_DOCS_BASE_URL, urlparse(link['url']).path).rstrip('/')

            # Skip the original URL and duplicates based on normalized path
            if candidate_url_normalized != original_url_normalized and candidate_url_normalized not in unique_urls:
                unique_urls.add(candidate_url_normalized)
                unique_links.append(link)
                if len(unique_links) >= 10:  # Limit to 10 recommendations
                    break

        # If no specific recommendations were found, maybe suggest the main docs page?
        # Only suggest if the original URL wasn't already the main docs page
        if not unique_links and urlparse(url).path != '/docs/' and urlparse(url).path != '/docs' and urlparse(url).path != '/':
             unique_links.append({
                 'url': K8S_DOCS_BASE_URL,
                 'title': 'Kubernetes Documentation Home',
                 'context': 'General starting point'
             })


        return unique_links

    except requests.RequestException as e:
        return [{"error": f"Error fetching documentation for recommendations: {str(e)}"}]
    except Exception as e:
        # Log the error for debugging, but return a user-friendly message
        print(f"Recommendation error: {e}")
        return [{"error": f"An unexpected error occurred while generating recommendations: {str(e)}"}]


if __name__ == "__main__":
    mcp.run()