#!/usr/bin/env python3
"""
Script to cluster news articles based on their categories
Takes CSV file input and outputs JSON clusters for the web application
"""
import os
import json
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("clustering.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def load_data(input_csv):
    """
    Load article data from CSV file
    """
    logger.info(f"Loading data from {input_csv}")

    # Check if file exists
    if not os.path.exists(input_csv):
        logger.error(f"File {input_csv} does not exist!")

        # If the real data doesn't exist, create a sample dataset for testing
        logger.info("Creating sample dataset for testing")
        data = create_sample_data()
        return data

    # Load the CSV file
    try:
        df = pd.read_csv(input_csv)
        logger.info(f"Loaded {len(df)} articles from {input_csv}")
        return df
    except Exception as e:
        logger.error(f"Error loading CSV: {str(e)}")
        logger.info("Creating sample dataset for testing")
        return create_sample_data()


def create_sample_data():
    """
    Create a sample dataset for testing the clustering
    """
    newspapers = ["Independent", "CNN", "BBC", "iHarare"]
    categories = ["Business", "Politics", "Arts/Culture/Celebrities", "Sports"]

    data = []
    counter = 0

    # Create 5 sample articles for each newspaper in each category
    for newspaper in newspapers:
        for category in categories:
            for i in range(5):
                counter += 1
                data.append({
                    "newspaper": newspaper,
                    "category": category,
                    "title": f"Sample {category} Article {i + 1} from {newspaper}",
                    "url": f"https://{newspaper.lower()}.com/sample-article-{i}",
                    "content": f"This is sample content for a {category} article from {newspaper}.",
                    "date_scraped": "2025-05-08"
                })

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Save sample data for inspection
    df.to_csv("news_data/sample_articles.csv", index=False)
    logger.info(f"Created sample dataset with {len(df)} articles")

    return df


def cluster_articles(df):
    """
    Cluster articles based on their categories
    In this implementation, we're simply using the category as the cluster
    but you could modify this to use more sophisticated clustering
    """
    logger.info("Clustering articles...")

    # Method 1: Simple clustering by category
    # Create a dictionary where each category is a cluster
    clusters = {}

    # For each unique category, create a cluster
    for i, category in enumerate(df['category'].unique()):
        # Get all articles in this category
        articles = df[df['category'] == category].to_dict('records')
        # Add them to the cluster
        clusters[str(i)] = articles

    logger.info(f"Created {len(clusters)} clusters based on categories")

    # Method 2: Advanced clustering using TF-IDF and K-means (uncomment to use)
    # This would cluster based on content similarity rather than just category
    """
    # Create a TF-IDF vectorizer
    vectorizer = TfidfVectorizer(stop_words='english')

    # Fit and transform the article content
    tfidf_matrix = vectorizer.fit_transform(df['content'])

    # Use K-means to cluster the articles
    # You can adjust the number of clusters (n_clusters) as needed
    kmeans = KMeans(n_clusters=4, random_state=42)
    df['cluster'] = kmeans.fit_predict(tfidf_matrix)

    # Create a dictionary where each cluster is a list of articles
    clusters = {}
    for cluster_id in df['cluster'].unique():
        articles = df[df['cluster'] == cluster_id].to_dict('records')
        clusters[str(cluster_id)] = articles

    logger.info(f"Created {len(clusters)} clusters using TF-IDF and K-means")
    """

    return clusters


def save_clusters(clusters, output_json):
    """
    Save the clusters to a JSON file
    """
    logger.info(f"Saving clusters to {output_json}")

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_json), exist_ok=True)

    # Save to JSON
    with open(output_json, 'w') as f:
        json.dump(clusters, f, indent=2)

    logger.info(f"Saved {len(clusters)} clusters to {output_json}")


def main():
    """
    Main function to run the clustering process
    """
    logger.info("Starting article clustering")

    # Define input and output files
    input_csv = "news_data/all_articles.csv"
    output_json = "static/cluster_data.json"

    # Load data
    df = load_data(input_csv)

    # Cluster articles
    clusters = cluster_articles(df)

    # Save clusters
    save_clusters(clusters, output_json)

    logger.info("Clustering complete. Output saved to: " + output_json)

    # Print a message indicating which file was updated
    print(f"\n✓ Successfully created {len(clusters)} clusters!")
    print(f"✓ Saved to {output_json}")
    print(f"✓ You can now run the web application using:\n  python fixed_webapp.py")


if __name__ == "__main__":
    main()