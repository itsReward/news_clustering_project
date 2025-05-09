import os
import time
import random
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
from urllib.parse import urlparse, urljoin
import logging
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from collections import defaultdict
import json
from flask import Flask, render_template, jsonify, send_from_directory
import threading
import webbrowser

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
os.makedirs('static', exist_ok=True)
os.makedirs('templates', exist_ok=True)

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
            df = pd.DataFrame(self.all_articles)
            # Save all articles to a single CSV file
            df.to_csv('news_data/all_articles.csv', index=False)
            logger.info(f"Saved {len(df)} articles to news_data/all_articles.csv")
            return df
        else:
            # Return an empty DataFrame if no articles could be scraped
            logger.warning("No articles were scraped successfully")
            return pd.DataFrame(columns=['newspaper', 'category', 'title', 'url', 'content', 'date_scraped'])


class ArticleClusterer:
    def __init__(self, df):
        self.df = df

    def preprocess_data(self):
        """Preprocess the article content for clustering"""
        logger.info("Preprocessing article content for clustering")

        # Basic text cleaning
        self.df['clean_content'] = self.df['content'].fillna('').astype(str).str.lower()

        # Remove URLs, special characters, etc.
        self.df['clean_content'] = self.df['clean_content'].apply(self.clean_text)

        # Create a combined text field (title + content) for better clustering
        self.df['combined_text'] = self.df['title'].fillna('').astype(str) + ' ' + self.df['clean_content']

        # TF-IDF vectorization
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),  # Include bigrams
            min_df=2  # Ignore terms that appear in less than 2 documents
        )

        # If we have enough data, apply TF-IDF vectorization
        if len(self.df) > 1:
            self.X = self.vectorizer.fit_transform(self.df['combined_text'])
            logger.info(f"Vectorized {self.X.shape[0]} articles with {self.X.shape[1]} features")
            return self.X
        else:
            logger.warning("Not enough data for clustering")
            self.X = None
            return None

    def clean_text(self, text):
        """Clean the text by removing URLs, special characters, etc."""
        # Remove URLs
        text = re.sub(r'http\S+', '', text)
        # Remove special characters
        text = re.sub(r'[^\w\s]', '', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def determine_optimal_clusters(self, max_clusters=10):
        """Determine the optimal number of clusters using the elbow method"""
        if self.X is None or len(self.df) < 3:
            logger.warning("Not enough data to determine optimal clusters")
            return 2  # Default to 2 clusters

        logger.info("Determining optimal number of clusters using elbow method")

        wcss = []  # Within-cluster sum of squares
        K = range(2, min(max_clusters + 1, len(self.df)))

        for k in K:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(self.X)
            wcss.append(kmeans.inertia_)

        # Calculate the differences
        diffs = np.diff(wcss)
        # Calculate the rates of change
        roc = diffs[:-1] / diffs[1:]

        # Find the elbow point (where the rate of change is highest)
        optimal_clusters = np.argmax(roc) + 2

        # Plot the elbow graph
        plt.figure(figsize=(10, 6))
        plt.plot(K, wcss, 'bx-')
        plt.xlabel('Number of Clusters')
        plt.ylabel('Within-Cluster Sum of Squares')
        plt.title('Elbow Method For Optimal k')
        plt.axvline(x=optimal_clusters, color='r', linestyle='--')
        plt.savefig('static/elbow_method.png')

        logger.info(f"Optimal number of clusters determined to be {optimal_clusters}")
        return optimal_clusters

    def cluster_articles(self, num_clusters=None):
        """Cluster the articles using KMeans"""
        if self.X is None:
            logger.warning("No data available for clustering")
            self.df['cluster'] = 0  # Assign all to cluster 0
            return [0] * len(self.df)

        # If num_clusters is not provided, determine it automatically
        if num_clusters is None:
            num_clusters = self.determine_optimal_clusters()

        logger.info(f"Clustering articles into {num_clusters} clusters")

        # Apply KMeans clustering
        self.kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
        self.clusters = self.kmeans.fit_predict(self.X)

        # Add cluster labels to the dataframe
        self.df['cluster'] = self.clusters

        # Get the most common words in each cluster
        self.get_cluster_keywords()

        logger.info("Clustering completed")

        return self.clusters

    def get_cluster_keywords(self, top_n=10):
        """Get the top keywords that define each cluster"""
        if not hasattr(self, 'kmeans') or not hasattr(self, 'vectorizer'):
            logger.warning("Clustering has not been performed yet")
            return {}

        logger.info("Extracting top keywords for each cluster")

        # Get the cluster centers
        centers = self.kmeans.cluster_centers_

        # Get feature names from the vectorizer
        feature_names = self.vectorizer.get_feature_names_out()

        # Store keywords for each cluster
        self.cluster_keywords = {}

        for i in range(centers.shape[0]):
            # Sort the features by their score
            indices = centers[i].argsort()[::-1]
            # Get the top N keywords
            top_indices = indices[:top_n]
            keywords = [feature_names[idx] for idx in top_indices]
            self.cluster_keywords[i] = keywords

            logger.info(f"Cluster {i} keywords: {', '.join(keywords)}")

        return self.cluster_keywords

    def visualize_clusters(self):
        """Create visualizations of the clusters"""
        if self.X is None or 'cluster' not in self.df.columns:
            logger.warning("Clustering has not been performed yet")
            return

        logger.info("Creating cluster visualizations")

        # Reduce dimensions for visualization using PCA
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(self.X.toarray())

        plt.figure(figsize=(15, 10))

        # Create a color map for categories
        category_to_color = {
            'Business': 'blue',
            'Politics': 'red',
            'Arts/Culture/Celebrities': 'green',
            'Sports': 'purple'
        }

        # Plot by category
        plt.subplot(2, 2, 1)
        for category, color in category_to_color.items():
            mask = self.df['category'] == category
            if any(mask):  # Only plot if there are articles in this category
                plt.scatter(X_pca[mask, 0], X_pca[mask, 1], c=color, label=category, alpha=0.7)
        plt.title('Articles by Category')
        plt.xlabel('PCA Component 1')
        plt.ylabel('PCA Component 2')
        plt.legend()

        # Plot by cluster
        plt.subplot(2, 2, 2)
        scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], c=self.clusters, cmap='viridis', alpha=0.7)
        plt.title('Articles by Cluster')
        plt.xlabel('PCA Component 1')
        plt.ylabel('PCA Component 2')
        plt.colorbar(scatter, label='Cluster')

        # Plot category distribution within each cluster
        plt.subplot(2, 2, 3)
        categories = self.df['category'].unique()
        cluster_ids = sorted(self.df['cluster'].unique())

        category_counts = {}
        for cluster in cluster_ids:
            category_counts[cluster] = self.df[self.df['cluster'] == cluster]['category'].value_counts()

        # Create a stacked bar chart
        data = pd.DataFrame(index=cluster_ids, columns=categories).fillna(0)
        for cluster in cluster_ids:
            for category in categories:
                if category in category_counts[cluster]:
                    data.loc[cluster, category] = category_counts[cluster][category]

        data.plot(kind='bar', stacked=True, ax=plt.gca(), colormap='viridis')
        plt.title('Category Distribution in Each Cluster')
        plt.xlabel('Cluster')
        plt.ylabel('Number of Articles')
        plt.legend(title='Category')

        # Plot newspaper distribution within each cluster
        plt.subplot(2, 2, 4)
        newspapers = self.df['newspaper'].unique()

        newspaper_counts = {}
        for cluster in cluster_ids:
            newspaper_counts[cluster] = self.df[self.df['cluster'] == cluster]['newspaper'].value_counts()

        data = pd.DataFrame(index=cluster_ids, columns=newspapers).fillna(0)
        for cluster in cluster_ids:
            for newspaper in newspapers:
                if newspaper in newspaper_counts[cluster]:
                    data.loc[cluster, newspaper] = newspaper_counts[cluster][newspaper]

        data.plot(kind='bar', stacked=True, ax=plt.gca(), colormap='tab20')
        plt.title('Newspaper Distribution in Each Cluster')
        plt.xlabel('Cluster')
        plt.ylabel('Number of Articles')
        plt.legend(title='Newspaper')

        plt.tight_layout()
        plt.savefig('static/clusters.png', dpi=300)
        logger.info("Saved cluster visualization to static/clusters.png")

    def save_cluster_data(self):
        """Save cluster data to JSON for web display"""
        if 'cluster' not in self.df.columns:
            logger.warning("Clustering has not been performed yet")
            return {}

        logger.info("Saving cluster data for web display")

        # Create a dictionary of clusters and their articles
        cluster_data = defaultdict(list)

        for i, row in self.df.iterrows():
            cluster_data[int(row['cluster'])].append({
                'title': row['title'],
                'url': row['url'],
                'newspaper': row['newspaper'],
                'category': row['category'],
                'date_scraped': row['date_scraped']
            })

        # Add cluster keywords if available
        if hasattr(self, 'cluster_keywords'):
            for cluster_id, keywords in self.cluster_keywords.items():
                # Add cluster keywords to each article in the cluster
                for article in cluster_data[cluster_id]:
                    article['cluster_keywords'] = keywords

        # Save as JSON
        with open('static/cluster_data.json', 'w') as f:
            json.dump(dict(cluster_data), f)

        logger.info("Saved cluster data to static/cluster_data.json")

        # Print cluster statistics
        logger.info("\nCluster Statistics:")
        for cluster in sorted(cluster_data.keys()):
            logger.info(f"Cluster {cluster}: {len(cluster_data[cluster])} articles")

            # Count categories in this cluster
            category_count = defaultdict(int)
            for article in cluster_data[cluster]:
                category_count[article['category']] += 1

            for category, count in sorted(category_count.items()):
                logger.info(f"  - {category}: {count} articles")

            # If we have keywords, print them
            if hasattr(self, 'cluster_keywords') and cluster in self.cluster_keywords:
                logger.info(f"  - Keywords: {', '.join(self.cluster_keywords[cluster])}")

            logger.info("")

        return cluster_data


class WebApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.setup_routes()

    def setup_routes(self):
        """Set up the Flask routes"""

        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.app.route('/static/<path:path>')
        def serve_static(path):
            return send_from_directory('static', path)

        @self.app.route('/api/clusters')
        def get_clusters():
            try:
                with open('static/cluster_data.json', 'r') as f:
                    cluster_data = json.load(f)
                return jsonify(cluster_data)
            except Exception as e:
                logger.error(f"Error retrieving cluster data: {str(e)}")
                return jsonify({"error": str(e)}), 500

        @self.app.route('/cluster/<cluster_id>')
        def show_cluster(cluster_id):
            try:
                with open('static/cluster_data.json', 'r') as f:
                    cluster_data = json.load(f)

                # Convert string keys to integers for comparison
                cluster_id_str = str(cluster_id)
                if cluster_id_str not in cluster_data:
                    logger.warning(f"Cluster {cluster_id} not found")
                    return "Cluster not found", 404

                return render_template('cluster.html',
                                       cluster_id=cluster_id,
                                       articles=cluster_data[cluster_id_str])
            except Exception as e:
                logger.error(f"Error displaying cluster {cluster_id}: {str(e)}")
                return f"Error: {str(e)}", 500

    def create_templates(self):
        """Create the HTML templates for the web application"""
        logger.info("Creating HTML templates for web display")

        # Create index.html
        with open('templates/index.html', 'w') as f:
            f.write('''<!DOCTYPE html>
<html>
<head>
    <title>Zimbabwe News Article Clusters</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f8f9fa;
        }
        .header {
            background-color: #343a40;
            color: white;
            padding: 2rem 0;
            margin-bottom: 2rem;
        }
        .cluster-card {
            margin-bottom: 20px;
            transition: transform 0.3s;
            border: none;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .cluster-card:hover {
            transform: scale(1.03);
            box-shadow: 0 10px 20px rgba(0,0,0,0.15);
        }
        .cluster-card .card-body {
            padding: 1.5rem;
        }
        .cluster-card .card-title {
            color: #343a40;
            font-weight: 600;
        }
        .btn-primary {
            background-color: #0d6efd;
            border-color: #0d6efd;
        }
        .btn-primary:hover {
            background-color: #0b5ed7;
            border-color: #0a58ca;
        }
        .visualization-container {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }
        .keyword-badge {
            display: inline-block;
            background-color: #e9ecef;
            color: #495057;
            padding: 0.35em 0.65em;
            font-size: 0.75em;
            font-weight: 700;
            line-height: 1;
            text-align: center;
            white-space: nowrap;
            vertical-align: baseline;
            border-radius: 0.25rem;
            margin-right: 5px;
            margin-bottom: 5px;
        }
    </style>
</head>
<body>
    <div class="header text-center">
        <div class="container">
            <h1 class="display-4">Zimbabwe News Article Clusters</h1>
            <p class="lead">Discover patterns and relationships between news articles from various sources</p>
        </div>
    </div>

    <div class="container">
        <div class="row mb-4">
            <div class="col-md-12">
                <div class="visualization-container">
                    <h2 class="mb-3">Cluster Visualization</h2>
                    <img src="/static/clusters.png" class="img-fluid" alt="Cluster Visualization">
                </div>
            </div>
        </div>

        <h2 class="mb-4">News Clusters</h2>
        <div class="row" id="clusters-container">
            <!-- Clusters will be loaded here via JavaScript -->
            <div class="col-12 text-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p>Loading clusters...</p>
            </div>
        </div>
    </div>

    <footer class="bg-dark text-white text-center py-4 mt-5">
        <div class="container">
            <p class="mb-0">Zimbabwe News Clustering System &copy; 2025</p>
        </div>
    </footer>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            fetch('/api/clusters')
                .then(response => response.json())
                .then(data => {
                    const container = document.getElementById('clusters-container');
                    container.innerHTML = ''; // Clear loading spinner

                    if (Object.keys(data).length === 0) {
                        container.innerHTML = '<div class="col-12"><div class="alert alert-warning">No clusters available. Please run the scraper first.</div></div>';
                        return;
                    }

                    Object.keys(data).forEach(clusterId => {
                        const articles = data[clusterId];
                        const categoryCount = {};
                        const newspaperCount = {};

                        // Count categories and newspapers in this cluster
                        articles.forEach(article => {
                            // Count categories
                            if (!categoryCount[article.category]) {
                                categoryCount[article.category] = 0;
                            }
                            categoryCount[article.category]++;

                            // Count newspapers
                            if (!newspaperCount[article.newspaper]) {
                                newspaperCount[article.newspaper] = 0;
                            }
                            newspaperCount[article.newspaper]++;
                        });

                        // Create category distribution text
                        let categoryText = '';
                        Object.keys(categoryCount).sort().forEach(category => {
                            categoryText += `${category}: ${categoryCount[category]} articles<br>`;
                        });

                        // Create newspaper distribution text
                        let newspaperText = '';
                        Object.keys(newspaperCount).sort().forEach(newspaper => {
                            newspaperText += `${newspaper}: ${newspaperCount[newspaper]} articles<br>`;
                        });

                        // Get keywords if available
                        let keywordsHtml = '';
                        if (articles.length > 0 && articles[0].cluster_keywords) {
                            keywordsHtml = '<div class="mt-2"><strong>Keywords:</strong><br>';
                            articles[0].cluster_keywords.forEach(keyword => {
                                keywordsHtml += `<span class="keyword-badge">${keyword}</span>`;
                            });
                            keywordsHtml += '</div>';
                        }

                        const clusterCard = document.createElement('div');
                        clusterCard.className = 'col-md-6 col-lg-4 mb-4';
                        clusterCard.innerHTML = `
                            <div class="card cluster-card h-100">
                                <div class="card-body">
                                    <h5 class="card-title">Cluster ${clusterId}</h5>
                                    <p class="card-text">
                                        <strong>Articles:</strong> ${articles.length}<br>
                                        <strong>Categories:</strong><br>${categoryText}
                                        <strong>Sources:</strong><br>${newspaperText}
                                        ${keywordsHtml}
                                    </p>
                                    <a href="/cluster/${clusterId}" class="btn btn-primary">View Articles</a>
                                </div>
                            </div>
                        `;
                        container.appendChild(clusterCard);
                    });
                })
                .catch(error => {
                    console.error('Error loading clusters:', error);
                    document.getElementById('clusters-container').innerHTML = 
                        '<div class="col-12"><div class="alert alert-danger">Error loading cluster data. Please check the console for details.</div></div>';
                });
        });
    </script>
</body>
</html>''')

        # Create cluster.html
        with open('templates/cluster.html', 'w') as f:
            f.write('''<!DOCTYPE html>
<html>
<head>
    <title>Cluster Details - Zimbabwe News Articles</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f8f9fa;
        }
        .header {
            background-color: #343a40;
            color: white;
            padding: 1.5rem 0;
            margin-bottom: 2rem;
        }
        .article-card {
            margin-bottom: 20px;
            transition: transform 0.2s;
            border: none;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .article-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.15);
        }
        .badge {
            font-size: 0.8em;
        }
        .keyword-badge {
            display: inline-block;
            background-color: #e9ecef;
            color: #495057;
            padding: 0.35em 0.65em;
            font-size: 0.75em;
            font-weight: 700;
            line-height: 1;
            text-align: center;
            white-space: nowrap;
            vertical-align: baseline;
            border-radius: 0.25rem;
            margin-right: 5px;
            margin-bottom: 5px;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <div class="d-flex justify-content-between align-items-center">
                <h1>Cluster {{cluster_id}} Details</h1>
                <a href="/" class="btn btn-outline-light">Back to Clusters</a>
            </div>
        </div>
    </div>

    <div class="container mb-5">
        <!-- Keywords section -->
        {% if articles[0].cluster_keywords %}
        <div class="mb-4">
            <h3>Cluster Keywords</h3>
            <div class="p-3 bg-white rounded shadow-sm">
                {% for keyword in articles[0].cluster_keywords %}
                <span class="keyword-badge">{{ keyword }}</span>
                {% endfor %}
            </div>
        </div>
        {% endif %}

        <h3 class="mb-3">Articles in this Cluster</h3>

        <div class="row">
            {% for article in articles %}
            <div class="col-md-6 mb-4">
                <div class="card article-card h-100">
                    <div class="card-body">
                        <h5 class="card-title">{{ article.title }}</h5>
                        <div class="mb-3">
                            <span class="badge bg-primary">{{ article.newspaper }}</span>
                            <span class="badge bg-secondary">{{ article.category }}</span>
                            <span class="badge bg-info text-dark">{{ article.date_scraped }}</span>
                        </div>
                        <a href="{{ article.url }}" target="_blank" class="btn btn-primary btn-sm">Read Full Article</a>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>

    <footer class="bg-dark text-white text-center py-3">
        <div class="container">
            <p class="mb-0">Zimbabwe News Clustering System &copy; 2025</p>
        </div>
    </footer>
</body>
</html>''')

        logger.info("HTML templates created successfully")