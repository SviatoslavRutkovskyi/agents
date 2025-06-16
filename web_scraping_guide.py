"""
Web Scraping Guide: How to Read Information from Web Pages

This guide covers different methods to extract information from web pages,
from simple HTTP requests to advanced browser automation.
"""

import requests
from bs4 import BeautifulSoup
import json
from playwright.async_api import async_playwright
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ============================================================================
# METHOD 1: Simple HTTP Requests with BeautifulSoup
# ============================================================================
# Best for: Static content, simple websites, API-like data

def scrape_with_requests_beautifulsoup(url):
    """
    Basic web scraping using requests and BeautifulSoup.
    Good for static HTML content.
    """
    try:
        # Send HTTP request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract information (examples)
        title = soup.find('title').text if soup.find('title') else 'No title'
        
        # Find all paragraphs
        paragraphs = soup.find_all('p')
        text_content = '\n'.join([p.text for p in paragraphs])
        
        # Find specific elements by class or ID
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
        
        return {
            'title': title,
            'text_content': text_content,
            'main_content': main_content.text if main_content else None,
            'status_code': response.status_code
        }
        
    except requests.RequestException as e:
        return {'error': f'Request failed: {e}'}
    except Exception as e:
        return {'error': f'Parsing failed: {e}'}

# Example usage:
# result = scrape_with_requests_beautifulsoup('https://example.com')

# ============================================================================
# METHOD 2: Playwright (Browser Automation)
# ============================================================================
# Best for: Dynamic content, JavaScript-heavy sites, user interactions

async def scrape_with_playwright(url):
    """
    Advanced web scraping using Playwright.
    Good for JavaScript-heavy sites and dynamic content.
    """
    async with async_playwright() as p:
        # Launch browser (headless=True for production)
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            # Navigate to page
            await page.goto(url, wait_until='networkidle')
            
            # Wait for specific content to load (optional)
            # await page.wait_for_selector('h1', timeout=10000)
            
            # Extract information
            title = await page.title()
            
            # Get page content
            content = await page.content()
            
            # Extract specific elements
            headings = await page.query_selector_all('h1, h2, h3')
            heading_texts = []
            for heading in headings:
                text = await heading.text_content()
                heading_texts.append(text)
            
            # Extract text from specific selectors
            main_content = await page.query_selector('main, article, .content')
            main_text = await main_content.text_content() if main_content else None
            
            # Handle cookies/popups if needed
            # await page.click('button[aria-label="Accept cookies"]')
            
            return {
                'title': title,
                'headings': heading_texts,
                'main_content': main_text,
                'full_content': content
            }
            
        except Exception as e:
            return {'error': f'Playwright scraping failed: {e}'}
        finally:
            await browser.close()

# Example usage:
# import asyncio
# result = asyncio.run(scrape_with_playwright('https://example.com'))

# ============================================================================
# METHOD 3: Selenium WebDriver
# ============================================================================
# Best for: Complex interactions, form filling, legacy browser automation

def scrape_with_selenium(url):
    """
    Web scraping using Selenium WebDriver.
    Good for complex interactions and legacy browser automation.
    """
    driver = None
    try:
        # Setup Chrome options
        from selenium.webdriver.chrome.options import Options
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in background
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        # Initialize driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Extract information
        title = driver.title
        
        # Find elements
        headings = driver.find_elements(By.CSS_SELECTOR, 'h1, h2, h3')
        heading_texts = [h.text for h in headings]
        
        # Get main content
        main_content = driver.find_element(By.TAG_NAME, 'body').text
        
        return {
            'title': title,
            'headings': heading_texts,
            'main_content': main_content
        }
        
    except Exception as e:
        return {'error': f'Selenium scraping failed: {e}'}
    finally:
        if driver:
            driver.quit()

# ============================================================================
# METHOD 4: API-like Data Extraction
# ============================================================================
# Best for: JSON APIs, structured data, RSS feeds

def extract_api_data(url):
    """
    Extract data from API endpoints or JSON-like responses.
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
        return {'error': f'API request failed: {e}'}

# ============================================================================
# METHOD 5: RSS Feed Reading
# ============================================================================
# Best for: News sites, blogs, content feeds

def read_rss_feed(rss_url):
    """
    Read and parse RSS feeds.
    """
    try:
        response = requests.get(rss_url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'xml')
        
        # Extract feed information
        feed_title = soup.find('title').text if soup.find('title') else 'Unknown'
        
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
            'feed_title': feed_title,
            'articles': articles
        }
        
    except Exception as e:
        return {'error': f'RSS reading failed: {e}'}

# ============================================================================
# PRACTICAL EXAMPLES FROM YOUR CODEBASE
# ============================================================================

def example_from_codebase():
    """
    Examples based on patterns found in your codebase.
    """
    
    # Example 1: Rate limiting with requests (from deep_research_with_emailjs)
    def rate_limited_request(url, rate_limit_api, request_token):
        """Make a rate-limited request to a web service."""
        try:
            # Check rate limit first
            response = requests.post(
                rate_limit_api,
                headers={"custom-header": request_token}
            )
            
            if response.status_code == 429:
                raise Exception("Too many requests! Please try again later.")
            elif response.status_code != 201:
                raise Exception(f"Rate limiter error: {response.status_code}")
            
            # Now make the actual request
            web_response = requests.get(url, timeout=10)
            return web_response.text
            
        except Exception as e:
            return f"Request failed: {e}"
    
    # Example 2: Browser automation with Playwright (from sidekick_tools.py)
    async def browser_automation_example():
        """Example of browser automation for complex web interactions."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            
            try:
                # Navigate and interact
                await page.goto("https://example.com")
                
                # Accept cookies if present
                try:
                    await page.click('button[aria-label="Accept cookies"]', timeout=5000)
                except:
                    pass  # No cookie banner
                
                # Extract information
                content = await page.content()
                title = await page.title()
                
                return {'title': title, 'content': content}
                
            finally:
                await browser.close()
    
    return "Examples ready for use"

# ============================================================================
# BEST PRACTICES AND TIPS
# ============================================================================

def web_scraping_best_practices():
    """
    Best practices for web scraping.
    """
    tips = {
        "1. Respect robots.txt": "Always check robots.txt before scraping",
        "2. Use appropriate delays": "Add time.sleep() between requests",
        "3. Set user agents": "Use realistic user agent strings",
        "4. Handle errors gracefully": "Always use try-catch blocks",
        "5. Check rate limits": "Implement rate limiting for large-scale scraping",
        "6. Use session objects": "Reuse connections for better performance",
        "7. Parse efficiently": "Use specific selectors instead of regex when possible",
        "8. Store data properly": "Save data in structured formats (JSON, CSV)",
        "9. Monitor changes": "Websites change, so monitor your scrapers",
        "10. Legal compliance": "Ensure you have permission to scrape the data"
    }
    return tips

# ============================================================================
# USAGE EXAMPLES
# ============================================================================

if __name__ == "__main__":
    # Example 1: Simple scraping
    print("=== Simple Web Scraping ===")
    result = scrape_with_requests_beautifulsoup('https://httpbin.org/html')
    print(f"Title: {result.get('title', 'N/A')}")
    
    # Example 2: Best practices
    print("\n=== Best Practices ===")
    practices = web_scraping_best_practices()
    for key, value in practices.items():
        print(f"{key}: {value}")
    
    # Example 3: Rate-limited request
    print("\n=== Rate Limited Request Example ===")
    # This would need actual API endpoints
    # result = rate_limited_request('https://api.example.com', rate_limit_api, token)
    
    print("\nWeb scraping guide ready! Use the functions above based on your needs.") 