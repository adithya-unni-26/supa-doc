import requests
from bs4 import BeautifulSoup
from newspaper import Article, Config
import openai
from database import supabase
import logging
import os
from urllib.parse import urljoin, urlparse
import uuid  # Add this import
import json  # Add this import
import time
from collections import deque
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add this new function to scrape content from URLs
def scrape_content(urls):
    logger.info(f"Starting to scrape content from {len(urls)} URLs")
    content = []
    
    # Configure newspaper
    config = Config()
    config.browser_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    config.request_timeout = 10
    
    # Rate limiting parameters
    requests_per_minute = 60
    request_times = deque()
    delay = 1  # Initial delay between requests in seconds
    max_retries = 3
    failure_threshold = 0.2  # 20% failure rate

    successful_requests = 0
    failed_requests = 0
    
    for i, url in enumerate(urls, 1):
        logger.info(f"Scraping URL {i}/{len(urls)}: {url}")
        
        # Check if we've hit the rate limit
        now = datetime.now()
        while len(request_times) >= requests_per_minute:
            if now - request_times[0] < timedelta(minutes=1):
                time.sleep((request_times[0] + timedelta(minutes=1) - now).total_seconds())
                now = datetime.now()
            else:
                request_times.popleft()

        retries = 0
        while retries < max_retries:
            try:
                article = Article(url, config=config)
                article.download()
                article.parse()
                
                content.append({
                    'url': url,
                    'title': article.title,
                    'content': article.text,
                    'authors': article.authors,
                    'publish_date': str(article.publish_date) if article.publish_date else None,
                    'top_image': article.top_image,
                    'keywords': article.keywords if article.keywords else []
                })
                
                logger.info(f"Successfully scraped content from {url} ({len(article.text)} characters)")
                successful_requests += 1
                break
            except Exception as e:
                logger.error(f"Error scraping {url}: {str(e)}")
                retries += 1
                time.sleep(delay * retries)  # Exponential backoff
        
        if retries == max_retries:
            failed_requests += 1

        # Update rate limiting
        request_times.append(now)
        time.sleep(delay)

        # Adjust delay based on failure rate
        total_requests = successful_requests + failed_requests
        if total_requests > 0 and failed_requests / total_requests > failure_threshold:
            delay = min(delay * 2, 5)  # Increase delay, max 5 seconds
            logger.warning(f"Increased delay to {delay} seconds due to high failure rate")
    
    logger.info(f"Finished scraping content from {len(content)} URLs")
    logger.info(f"Successful requests: {successful_requests}, Failed requests: {failed_requests}")
    return content

def extract_sitemap(url):
    if not url.startswith('http'):
        url = 'https://' + url

    logger.info(f"Processing URL: {url}")
    
    # List of common sitemap locations
    sitemap_locations = [
        '/sitemap.xml',
        '/sitemap_index.xml',
        '/sitemap/',
        '/sitemap.php',
        '/sitemap.txt',
    ]

    for location in sitemap_locations:
        sitemap_url = urljoin(url, location)
        logger.info(f"Trying sitemap at: {sitemap_url}")
        try:
            response = requests.get(sitemap_url, timeout=10)
            response.raise_for_status()
            
            if 'xml' in response.headers.get('Content-Type', '').lower():
                soup = BeautifulSoup(response.content, 'xml')
                urls = [loc.text for loc in soup.find_all('loc')]
                if urls:
                    logger.info(f"Found sitemap at {sitemap_url}")
                    return urls
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch {sitemap_url}: {str(e)}")

    # If no sitemap found, fallback to scraping the homepage
    logger.info("No sitemap found. Falling back to scraping the homepage.")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        urls = [urljoin(url, a['href']) for a in soup.find_all('a', href=True)]
        return urls
    except requests.RequestException as e:
        logger.error(f"Error fetching homepage: {str(e)}")
        return []

def extract_subdomains(urls):
    logger.info("Extracting subdomains from URLs")
    subdomains = set()
    for url in urls:
        parsed_url = urlparse(url)
        subdomain = parsed_url.netloc
        subdomains.add(subdomain)
    logger.info(f"Extracted {len(subdomains)} unique subdomains")
    return list(subdomains)

def generate_embeddings(text: str) -> list:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.Embedding.create(input=text, model="text-embedding-ada-002")
    embeddings = response['data'][0]['embedding']
    return embeddings

def process_and_store_document(url: str, document_id: str, max_urls: int = 10):
    logger.info(f"Starting process_and_store_document for URL: {url} with document_id: {document_id}")
    try:
        urls = extract_sitemap(url)
        logger.info(f"Extracted {len(urls)} URLs from sitemap")
        urls = urls[:max_urls]  # Limit to max_urls
        content = scrape_content(urls)
        logger.info(f"Scraped content from {len(content)} URLs")
        for item in content:
            logger.info(f"Processing content from URL: {item['url']}")
            try:
                embeddings = generate_embeddings(item['content'])
                logger.info(f"Generated embeddings of length: {len(embeddings)}")
                result = supabase.table("embeddings").insert({
                    "id": str(uuid.uuid4()),
                    "document_id": document_id,
                    "embedding_jsonb": embeddings,  # Changed from 'embedding' to 'embedding_jsonb'
                    "content": item['content'],
                    "url": item['url']
                }).execute()
                logger.info(f"Successfully stored embedding for URL: {item['url']}")
                logger.info(f"Supabase insert result: {result}")
            except Exception as e:
                logger.error(f"Error processing or storing embedding for URL {item['url']}: {str(e)}")
    except Exception as e:
        logger.error(f"Error in process_and_store_document: {str(e)}")
    
    # Check the total number of embeddings stored
    total_embeddings = supabase.table("embeddings").select("id").eq("document_id", document_id).execute()
    logger.info(f"Total embeddings stored for document_id {document_id}: {len(total_embeddings.data)}")