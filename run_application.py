#!/usr/bin/env python3
"""
Main entry point for the News Article Clustering Application
This script will run both the scraper (if needed) and the web interface
"""
import os
import sys
import json


def ensure_directories():
    """Create necessary directories if they don't exist"""
    os.makedirs('news_data', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('templates', exist_ok=True)


def check_data_exists():
    """Check if necessary data files exist"""
    if not os.path.exists('static/cluster_data.json'):
        print("Warning: cluster_data.json doesn't exist. The webapp might not display correctly.")
        print("Would you like to create a sample cluster_data.json file? (y/n)")
        choice = input().lower()
        if choice.startswith('y'):
            create_sample_cluster_data()


def create_sample_cluster_data():
    """Create a sample cluster_data.json file if none exists"""
    print("Creating sample cluster data...")

    sample_data = {
        "0": [
            {
                "title": "Sample Business Article",
                "url": "https://example.com/business-article",
                "newspaper": "Example News",
                "category": "Business",
                "date_scraped": "2025-05-08"
            }
        ],
        "1": [
            {
                "title": "Sample Politics Article",
                "url": "https://example.com/politics-article",
                "newspaper": "Example News",
                "category": "Politics",
                "date_scraped": "2025-05-08"
            }
        ]
    }

    with open('static/cluster_data.json', 'w') as f:
        json.dump(sample_data, f, indent=2)

    print("Sample data created successfully.")


def run_scraper():
    """Run the newspaper scraper if needed"""
    print("Do you want to run the news scraper to collect fresh data? (y/n)")
    choice = input().lower()
    if choice.startswith('y'):
        print("Running newspaper scraper...")
        try:
            import newspaper_scrapper
            newspaper_scrapper.main()
            print("Scraper completed successfully.")
        except Exception as e:
            print(f"Error running scraper: {str(e)}")


def run_webapp():
    """Run the web application"""
    print("Starting web application...")
    try:
        import fixed_webapp
        webapp = fixed_webapp.WebApp()
        webapp.run()
    except Exception as e:
        print(f"Error starting web application: {str(e)}")


def main():
    """Main function to run the application"""
    print("=" * 80)
    print("Zimbabwe News Article Clustering Application")
    print("=" * 80)

    ensure_directories()
    check_data_exists()
    run_scraper()
    run_webapp()


if __name__ == "__main__":
    main()