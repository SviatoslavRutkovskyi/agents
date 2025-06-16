"""
Web Scraping Examples: How to Read Information from Web Pages

This file demonstrates the most common and effective methods for extracting
information from web pages using Python.
"""

import requests
from bs4 import BeautifulSoup
import json
import time

# ============================================================================
# METHOD 1: Simple HTTP Requests + BeautifulSoup (Most Common)
# ============================================================================

def scrape_webpage_simple(url):
    """
    Basic web scraping using requests and BeautifulSoup.
    Best for: Static HTML content, simple websites
    """
    try:
        # Set headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0'
        }
        
        # Make the request
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an error for bad status codes
        
        # Parse the HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract information
        title = soup.find('title')
        title_text = title.text if title else 'No title found'
        
        # Get all text content
        text_content = soup.get_text()
        
        # Find specific elements
        headings = soup.find_all(['h1', 'h2', 'h3'])
        heading_texts = [h.text.strip() for h in headings]
        
        # Find links
        links = soup.find_all('a', href=True)
        link_urls = [link['href'] for link in links]
        
        return {
            'title': title_text,
            'headings': heading_texts,
            'links': link_urls[:10],  # First 10 links
            'text_length': len(text_content),
            'status_code': response.status_code
        }
        
    except requests.RequestException as e:
        return {'error': f'Request failed: {e}'}
    except Exception as e:
        return {'error': f'Parsing failed: {e}'}

# ============================================================================
# METHOD 2: Extract Specific Data (Tables, Lists, etc.)
# ============================================================================

def extract_specific_data(url, selectors):
    """
    Extract specific data using CSS selectors.
    Best for: Getting structured data like tables, lists, specific content
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        extracted_data = {}
        
        for name, selector in selectors.items():
            elements = soup.select(selector)
            if elements:
                if len(elements) == 1:
                    extracted_data[name] = elements[0].text.strip()
                else:
                    extracted_data[name] = [elem.text.strip() for elem in elements]
            else:
                extracted_data[name] = None
        
        return extracted_data
        
    except Exception as e:
        return {'error': f'Extraction failed: {e}'}

# ============================================================================
# METHOD 3: API-like Data Extraction
# ============================================================================

def extract_json_data(url):
    """
    Extract data from JSON APIs or JSON-like responses.
    Best for: APIs, structured data endpoints
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Try to parse as JSON
        try:
            data = response.json()
            return {'data': data, 'type': 'json'}
        except json.JSONDecodeError:
            # If not JSON, return as text
            return {'data': response.text, 'type': 'text'}
            
    except requests.RequestException as e:
        return {'error': f'Request failed: {e}'}

# ============================================================================
# METHOD 4: RSS Feed Reading
# ============================================================================

def read_rss_feed(rss_url):
    """
    Read and parse RSS feeds.
    Best for: News sites, blogs, content feeds
    """
    try:
        response = requests.get(rss_url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'xml')
        
        # Extract feed information
        feed_title = soup.find('title')
        feed_title_text = feed_title.text if feed_title else 'Unknown Feed'
        
        # Extract articles
        articles = []
        for item in soup.find_all('item'):
            article = {
                'title': item.find('title').text if item.find('title') else '',
                'link': item.find('link').text if item.find('link') else '',
                'description': item.find('description').text if item.find('description') else '',
                'pubDate': item.find('pubDate').text if item.find('pubDate') else ''
            }
            articles.append(article)
        
        return {
            'feed_title': feed_title_text,
            'article_count': len(articles),
            'articles': articles[:5]  # First 5 articles
        }
        
    except Exception as e:
        return {'error': f'RSS reading failed: {e}'}

# ============================================================================
# METHOD 5: Rate-Limited Scraping (Best Practice)
# ============================================================================

def scrape_with_rate_limiting(urls, delay=1):
    """
    Scrape multiple URLs with rate limiting.
    Best practice for scraping multiple pages.
    """
    results = []
    
    for i, url in enumerate(urls):
        print(f"Scraping {i+1}/{len(urls)}: {url}")
        
        try:
            result = scrape_webpage_simple(url)
            results.append({'url': url, 'result': result})
            
            # Rate limiting - wait between requests
            if i < len(urls) - 1:  # Don't wait after the last request
                time.sleep(delay)
                
        except Exception as e:
            results.append({'url': url, 'error': str(e)})
    
    return results

# ============================================================================
# PRACTICAL EXAMPLES
# ============================================================================

def example_usage():
    """
    Examples of how to use the scraping functions.
    """
    
    print("=== Web Scraping Examples ===\n")
    
    # Example 1: Simple webpage scraping
    print("1. Simple webpage scraping:")
    result = scrape_webpage_simple('https://httpbin.org/html')
    print(f"   Title: {result.get('title', 'N/A')}")
    print(f"   Headings found: {len(result.get('headings', []))}")
    print(f"   Links found: {len(result.get('links', []))}")
    print()
    
    # Example 2: Extract specific data
    print("2. Extract specific data:")
    selectors = {
        'title': 'title',
        'main_heading': 'h1',
        'paragraphs': 'p',
        'navigation': 'nav'
    }
    specific_data = extract_specific_data('https://httpbin.org/html', selectors)
    print(f"   Main heading: {specific_data.get('main_heading', 'Not found')}")
    print()
    
    # Example 3: JSON data extraction
    print("3. JSON data extraction:")
    json_data = extract_json_data('https://httpbin.org/json')
    print(f"   Data type: {json_data.get('type', 'N/A')}")
    if json_data.get('type') == 'json':
        print(f"   Keys in data: {list(json_data.get('data', {}).keys())}")
    print()
    
    # Example 4: RSS feed reading
    print("4. RSS feed reading:")
    # Using a public RSS feed
    rss_data = read_rss_feed('https://feeds.bbci.co.uk/news/rss.xml')
    print(f"   Feed: {rss_data.get('feed_title', 'N/A')}")
    print(f"   Articles: {rss_data.get('article_count', 0)}")
    print()
    
    # Example 5: Rate-limited scraping
    print("5. Rate-limited scraping:")
    test_urls = [
        'https://httpbin.org/html',
        'https://httpbin.org/json',
        'https://httpbin.org/xml'
    ]
    rate_limited_results = scrape_with_rate_limiting(test_urls, delay=0.5)
    print(f"   Scraped {len(rate_limited_results)} URLs successfully")
    print()

# ============================================================================
# BEST PRACTICES
# ============================================================================

def best_practices():
    """
    Best practices for web scraping.
    """
    practices = [
        "1. Always check robots.txt before scraping",
        "2. Use realistic user agent strings",
        "3. Implement rate limiting (delay between requests)",
        "4. Handle errors gracefully with try-catch blocks",
        "5. Respect the website's terms of service",
        "6. Use session objects for multiple requests to the same site",
        "7. Parse HTML efficiently with specific selectors",
        "8. Store data in structured formats (JSON, CSV)",
        "9. Monitor for website changes that might break your scraper",
        "10. Consider using APIs when available instead of scraping"
    ]
    
    print("=== Best Practices ===")
    for practice in practices:
        print(practice)
    print()

# ============================================================================
# RUN EXAMPLES
# ============================================================================

if __name__ == "__main__":
    best_practices()
    example_usage()
    
    print("=== Quick Test ===")
    # Test with a simple, reliable endpoint
    test_result = scrape_webpage_simple('https://httpbin.org/html')
    if 'error' not in test_result:
        print("✅ Basic scraping works!")
        print(f"   Page title: {test_result.get('title', 'N/A')}")
    else:
        print(f"❌ Scraping failed: {test_result['error']}")
    
    print("\nWeb scraping examples ready! Use these functions based on your needs.") 