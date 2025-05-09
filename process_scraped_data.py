#!/usr/bin/env python3
"""
Script to process scraped news article data and create clusters for the web application.
This script specifically ensures that data from all_articles.csv is properly processed.
"""
import os
import json
import pandas as pd
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("process_data.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def check_file_exists(file_path):
    """Check if a file exists and log its details"""
    if os.path.exists(file_path):
        file_size = os.path.getsize(file_path) / 1024  # Size in KB
        logger.info(f"✓ Found {file_path} (Size: {file_size:.2f} KB)")
        return True
    else:
        logger.error(f"✗ File not found: {file_path}")
        return False


def load_scraped_data():
    """Load the scraped article data from CSV"""
    csv_path = "news_data/all_articles.csv"

    if not check_file_exists(csv_path):
        raise FileNotFoundError(f"Could not find scraped data at {csv_path}")

    try:
        df = pd.read_csv(csv_path)
        logger.info(f"Successfully loaded {len(df)} articles from {csv_path}")

        # Check if dataframe has expected columns
        expected_columns = ['newspaper', 'category', 'title', 'url', 'content', 'date_scraped']
        missing_columns = [col for col in expected_columns if col not in df.columns]

        if missing_columns:
            logger.warning(f"Missing expected columns: {', '.join(missing_columns)}")

            # Try to infer missing columns or create them with placeholders
            for col in missing_columns:
                if col == 'date_scraped':
                    df[col] = datetime.now().strftime('%Y-%m-%d')
                else:
                    df[col] = f"Missing {col}"

        # Display a sample of the data for verification
        logger.info("Sample of loaded data:")
        for idx, sample in df.head(3).iterrows():
            logger.info(f"Article {idx + 1}: {sample['title']} from {sample['newspaper']}")

        return df

    except Exception as e:
        logger.error(f"Error loading scraped data: {str(e)}")
        raise


def create_clusters(df):
    """Create clusters based on article categories"""
    logger.info("Creating clusters from scraped data...")

    # Ensure the category field exists
    if 'category' not in df.columns:
        logger.error("Category column not found in the data!")
        # Try to use another column or infer categories
        if 'topic' in df.columns:
            logger.info("Using 'topic' column instead of 'category'")
            df['category'] = df['topic']
        else:
            logger.warning("Unable to find category information, using placeholder categories")
            df['category'] = "Uncategorized"

    # Get unique categories
    categories = df['category'].unique()
    logger.info(f"Found {len(categories)} unique categories: {', '.join(categories)}")

    # Create clusters based on categories
    clusters = {}
    for i, category in enumerate(categories):
        # Filter articles for this category
        category_articles = df[df['category'] == category]

        # Convert to list of dictionaries for JSON serialization
        articles_list = category_articles.to_dict('records')

        # Add to clusters
        clusters[str(i)] = articles_list

        logger.info(f"Created cluster {i} for category '{category}' with {len(articles_list)} articles")

    return clusters


def save_clusters(clusters, output_path):
    """Save clusters to a JSON file for the web application"""
    logger.info(f"Saving clusters to {output_path}")

    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save to JSON
    with open(output_path, 'w') as f:
        json.dump(clusters, f, indent=2)

    logger.info(f"Successfully saved {len(clusters)} clusters to {output_path}")


def main():
    """Main function to process scraped data and create clusters"""
    print("=" * 80)
    print("Processing Scraped News Article Data")
    print("=" * 80)

    try:
        # Load the scraped data
        df = load_scraped_data()

        # Create clusters
        clusters = create_clusters(df)

        # Save clusters for the web application
        output_path = "static/cluster_data.json"
        save_clusters(clusters, output_path)

        print("\n✓ Processing complete!")
        print(f"✓ Created {len(clusters)} clusters from {len(df)} articles")
        print(f"✓ Saved to {output_path}")
        print(f"\nYou can now run the web application using:")
        print(f"  python fixed_webapp.py")

    except Exception as e:
        logger.error(f"Error processing data: {str(e)}")
        print(f"\n✗ Error: {str(e)}")
        print("Please check the log file for details: process_data.log")


if __name__ == "__main__":
    main()