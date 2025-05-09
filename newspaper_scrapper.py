import os
import time
import random
import pandas as pd
import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
from urllib.parse import urlparse, urljoin
import logging
import re

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create directories
os.makedirs('news_data', exist_ok=True)

# User agent rotation to avoid being blocked
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
]

def get_random_user_agent():
    """Return a random user agent from the list"""
    return random.choice(USER_AGENTS)

class NewspaperScraper:
    def __init__(self):
        self.all_articles = []
        self.define_newspaper_structures()

    def define_newspaper_structures(self):
        """Define the structure and selectors for each newspaper"""
        self.newspapers = {
            # Independent - Updated selectors
            "independent": {
                "name": "Independent",
                "base_url": "https://www.independent.co.uk/",
                "categories": {
                    "Business": [
                        "https://www.independent.co.uk/news/business"
                    ],
                    "Politics": [
                        "https://www.independent.co.uk/news/uk/politics"
                    ],
                    "Arts/Culture/Celebrities": [
                        "https://www.independent.co.uk/arts-entertainment"
                    ],
                    "Sports": [
                        "https://www.independent.co.uk/sport"
                    ]
                },
                # Updated selectors based on current Independent website structure
                "article_selector": "div.article, div.content, article, div.jsx-bylines",
                "title_selector": "h2 a, h3 a, a.title, h1.headline",
                "content_selector": "div[id*='article-content'] p, div.content p, div.article-body p, div.body-content p"
            },
            # CNN - Updated selectors
            "cnn": {
                "name": "CNN",
                "base_url": "https://edition.cnn.com/",
                "categories": {
                    "Business": [
                        "https://edition.cnn.com/business"
                    ],
                    "Politics": [
                        "https://edition.cnn.com/politics"
                    ],
                    "Arts/Culture/Celebrities": [
                        "https://edition.cnn.com/entertainment"
                    ],
                    "Sports": [
                        "https://edition.cnn.com/sport"
                    ]
                },
                # Updated selectors based on current CNN website structure
                "article_selector": "div.card, article, div.container__item, div.container_lead-plus-headlines__item",
                "title_selector": "span.container__headline-text, h3.container__headline, a.container__link, h3 a, div.headline a, h2.headline a",
                "content_selector": "div.article__content p, section.body-text p, div.zn-body__paragraph"
            },
            # BBC - Updated selectors
            "bbc": {
                "name": "BBC",
                "base_url": "https://www.bbc.com/",
                "categories": {
                    "Business": [
                        "https://www.bbc.com/news/business"
                    ],
                    "Politics": [
                        "https://www.bbc.com/news/politics"
                    ],
                    "Arts/Culture/Celebrities": [
                        "https://www.bbc.com/news/entertainment_and_arts"
                    ],
                    "Sports": [
                        "https://www.bbc.com/sport"
                    ]
                },
                # Updated selectors based on current BBC website structure
                "article_selector": "div.gs-c-promo, article, div.media, div.media__panel, div.faux-block-link",
                "title_selector": "h3.gs-c-promo-heading__title, h3.media__title, a.media__link, span.faux-block-link__overlay-link",
                "content_selector": "div.story-body__inner p, article p, div[data-component='text-block']"
            },
            # iHarare - Zimbabwean news source
            "iharare": {
                "name": "iHarare",
                "base_url": "https://iharare.com",
                "categories": {
                    "Business": [
                        "https://iharare.com/category/business/"
                    ],
                    "Politics": [
                        "https://iharare.com/category/politics/"
                    ],
                    "Arts/Culture/Celebrities": [
                        "https://iharare.com/category/entertainment/"
                    ],
                    "Sports": [
                        "https://iharare.com/category/sports/"
                    ]
                },
                "article_selector": "article, div.jeg_posts, div.jeg_post, div.post-wrap",
                "title_selector": "h3.jeg_post_title a, h2.entry-title a, h3.entry-title a",
                "content_selector": "div.entry-content p, div.content-inner p, div.jeg_share_container"
            },
            # Added The Herald - Zimbabwe's national newspaper
            "herald": {
                "name": "The Herald",
                "base_url": "https://www.herald.co.zw/",
                "categories": {
                    "Business": [
                        "https://www.herald.co.zw/category/business/"
                    ],
                    "Politics": [
                        "https://www.herald.co.zw/category/politics/"
                    ],
                    "Arts/Culture/Celebrities": [
                        "https://www.herald.co.zw/category/entertainment/"
                    ],
                    "Sports": [
                        "https://www.herald.co.zw/category/sports/"
                    ]
                },
                "article_selector": "article, div.post, div.item, div.td_module_wrap",
                "title_selector": "h3 a, h2.entry-title a, div.entry-title a, h3.entry-title a",
                "content_selector": "div.entry-content p, div.td-post-content p, article p"
            }
        }

    def scrape_article_links(self, url, newspaper):
        """Scrape article links from a category page with more robust error handling and debugging"""
        headers = {'User-Agent': get_random_user_agent()}
        try:
            # Add headers and timeout for the request
            response = requests.get(url, headers=headers, timeout=15)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Log some of the HTML to help debug selector issues
                logger.debug(f"First 500 chars of HTML: {soup.prettify()[:500]}")

                # Try different article selectors
                selectors = newspaper['article_selector'].split(', ')
                article_links = []

                for selector in selectors:
                    elements = soup.select(selector)
                    if elements:
                        logger.info(f"Selector '{selector}' matched {len(elements)} elements")

                        # Try different title selectors for each article element
                        title_selectors = newspaper['title_selector'].split(', ')
                        for title_selector in title_selectors:
                            for element in elements:
                                title_elem = element.select_one(title_selector)
                                if title_elem and title_elem.get('href'):
                                    href = title_elem.get('href')
                                    title = title_elem.text.strip()
                                    # Handle relative URLs
                                    if not href.startswith('http'):
                                        href = urljoin(newspaper['base_url'], href)

                                    article_links.append({
                                        'url': href,
                                        'title': title
                                    })

                                # Also try to find links directly in the article container
                                links = element.find_all('a')
                                for link in links:
                                    href = link.get('href')
                                    if href and (
                                        '/news/' in href or
                                        '/article/' in href or
                                        '/story/' in href or
                                        '/business/' in href or
                                        '/politics/' in href or
                                        '/sport/' in href
                                    ):
                                        title = link.text.strip() or link.get('title', '')
                                        if not title and link.find('h2'):
                                            title = link.find('h2').text.strip()
                                        if not title and link.find('h3'):
                                            title = link.find('h3').text.strip()

                                        # Handle relative URLs
                                        if not href.startswith('http'):
                                            href = urljoin(newspaper['base_url'], href)

                                        article_links.append({
                                            'url': href,
                                            'title': title or "No title found"
                                        })

                # Remove duplicates
                unique_links = []
                seen_urls = set()
                for article in article_links:
                    if article['url'] not in seen_urls and article['title']:
                        unique_links.append(article)
                        seen_urls.add(article['url'])

                logger.info(f"Found {len(unique_links)} unique article links")
                return unique_links
            else:
                logger.warning(f"Failed to access {url}, status code: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Error scraping URL {url}: {str(e)}")
            return []

    def scrape_article_content(self, article_url, article_title, newspaper):
        """Scrape the content of an article with more robust error handling"""
        try:
            headers = {'User-Agent': get_random_user_agent()}
            response = requests.get(article_url, headers=headers, timeout=15)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Try different content selectors
                content_selectors = newspaper['content_selector'].split(', ')
                content = ""

                for selector in content_selectors:
                    paragraphs = soup.select(selector)
                    if paragraphs:
                        content = ' '.join(p.text.strip() for p in paragraphs)
                        if len(content) > 100:  # If we found substantial content, stop looking
                            break

                # If main selectors failed, try a more generic approach
                if not content or len(content) < 100:
                    # Look for article containers
                    article_containers = soup.select('article, div.article, div.story')
                    for container in article_containers:
                        paragraphs = container.find_all('p')
                        content = ' '.join(p.text.strip() for p in paragraphs)
                        if len(content) > 100:
                            break

                if not content or len(content) < 100:
                    # Last resort: get all paragraphs in the page
                    paragraphs = soup.find_all('p')
                    content = ' '.join(p.text.strip() for p in paragraphs[:15])  # Limit to first 15 paragraphs

                return content
            else:
                logger.warning(f"Failed to access article {article_url}, status code: {response.status_code}")
                return ""

        except Exception as e:
            logger.error(f"Error scraping article content {article_url}: {str(e)}")
            return ""

    def scrape_all_newspapers(self, max_articles_per_category=5):
        """Scrape articles from all defined newspapers with improved error handling"""
        logger.info("Starting web scraping process")

        for newspaper_id, newspaper in self.newspapers.items():
            logger.info(f"Scraping from {newspaper['name']}")

            # Create a CSV file for this newspaper
            csv_filename = f"news_data/{newspaper_id}.csv"
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(['newspaper', 'category', 'title', 'url', 'content', 'date_scraped'])

                # Scrape each category
                for category, urls in newspaper['categories'].items():
                    logger.info(f"  Scraping category: {category}")

                    articles_scraped = 0
                    for url in urls:
                        try:
                            if articles_scraped >= max_articles_per_category:
                                break

                            logger.info(f"    Accessing URL: {url}")

                            # Scrape article links
                            article_links = self.scrape_article_links(url, newspaper)

                            # Process each article link
                            for article in article_links[:max_articles_per_category - articles_scraped]:
                                try:
                                    article_url = article['url']
                                    article_title = article['title']

                                    logger.info(f"      Scraping article: {article_title}")

                                    # Add delay to avoid overloading the server
                                    time.sleep(random.uniform(1, 3))

                                    # Scrape article content
                                    content = self.scrape_article_content(article_url, article_title, newspaper)

                                    # Skip if content is too short
                                    if len(content) < 50:
                                        logger.warning(f"      Article content too short, skipping")
                                        continue

                                    # Save to CSV
                                    csv_writer.writerow([
                                        newspaper['name'],
                                        category,
                                        article_title,
                                        article_url,
                                        content,
                                        datetime.now().strftime('%Y-%m-%d')
                                    ])

                                    # Add to all articles list
                                    self.all_articles.append({
                                        'newspaper': newspaper['name'],
                                        'category': category,
                                        'title': article_title,
                                        'url': article_url,
                                        'content': content,
                                        'date_scraped': datetime.now().strftime('%Y-%m-%d')
                                    })

                                    articles_scraped += 1
                                    logger.info(f"      Successfully scraped article")

                                    if articles_scraped >= max_articles_per_category:
                                        break

                                except Exception as e:
                                    logger.error(f"      Error processing article: {str(e)}")

                        except Exception as e:
                            logger.error(f"    Error scraping URL {url}: {str(e)}")

        # Create a DataFrame from all the scraped articles
        if self.all_articles:
            return pd.DataFrame(self.all_articles)
        else:
            # Return an empty DataFrame if no articles could be scraped
            logger.warning("No articles were scraped successfully")
            return pd.DataFrame(columns=['newspaper', 'category', 'title', 'url', 'content', 'date_scraped'])

def main():
    """Main function to run the web scraper"""
    logger.info("Zimbabwe Newspaper Web Scraper")
    logger.info("=============================")

    # Run web scraping
    scraper = NewspaperScraper()
    df = scraper.scrape_all_newspapers(max_articles_per_category=5)

    # Save all articles to a single CSV file
    if not df.empty:
        df.to_csv('news_data/all_articles.csv', index=False)
        logger.info(f"Saved {len(df)} articles to news_data/all_articles.csv")
    else:
        logger.warning("No articles were scraped, so no CSV file was created")

    logger.info("Scraping completed")

if __name__ == "__main__":
    main()