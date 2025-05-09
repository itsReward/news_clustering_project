#!/usr/bin/env python3
"""
Debug script to check the project structure and diagnose issues
"""
import os
import sys
import json


def check_file_exists(filepath):
    """Check if a file exists and return True/False"""
    exists = os.path.exists(filepath)
    print(f"Checking if {filepath} exists: {exists}")
    return exists


def check_directory_contents(directory):
    """List contents of a directory"""
    if os.path.exists(directory):
        files = os.listdir(directory)
        print(f"Contents of {directory}/:")
        for file in files:
            print(f"  - {file}")
        return files
    else:
        print(f"Directory {directory}/ does not exist")
        return []


def check_imported_modules():
    """Check if required modules are installed"""
    required_modules = [
        'flask', 'requests', 'beautifulsoup4', 'pandas', 'sklearn'
    ]

    print("Checking for required modules:")
    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✓ {module} is installed")
        except ImportError:
            print(f"  ✗ {module} is NOT installed")


def ensure_directories():
    """Create necessary directories if they don't exist"""
    for directory in ['templates', 'static', 'news_data']:
        if not os.path.exists(directory):
            print(f"Creating missing directory: {directory}/")
            os.makedirs(directory)


def create_sample_cluster_data():
    """Create a sample cluster_data.json file if none exists"""
    filepath = 'static/cluster_data.json'

    if not os.path.exists(filepath):
        print(f"Creating sample {filepath}")

        sample_data = {
            "0": [
                {
                    "title": "Sample Sports Article",
                    "url": "https://example.com/sports-article",
                    "newspaper": "Example News",
                    "category": "Sports",
                    "date_scraped": "2025-05-08"
                }
            ],
            "1": [
                {
                    "title": "Sample Arts/Culture/Celebrities Article",
                    "url": "https://example.com/culture-article",
                    "newspaper": "Example News",
                    "category": "Arts/Culture/Celebrities",
                    "date_scraped": "2025-05-08"
                }
            ],
            "2": [
                {
                    "title": "Sample Business Article",
                    "url": "https://example.com/business-article",
                    "newspaper": "Example News",
                    "category": "Business",
                    "date_scraped": "2025-05-08"
                }
            ],
            "3": [
                {
                    "title": "Sample Politics Article",
                    "url": "https://example.com/politics-article",
                    "newspaper": "Example News",
                    "category": "Politics",
                    "date_scraped": "2025-05-08"
                }
            ]
        }

        with open(filepath, 'w') as f:
            json.dump(sample_data, f, indent=2)

        print(f"Created sample cluster data at {filepath}")
    else:
        print(f"{filepath} already exists")


def main():
    """Main function to check project structure"""
    print("=" * 80)
    print("Zimbabwe News Article Clustering Application - Debug")
    print("=" * 80)

    # Check for main script files
    check_file_exists('newspaper_scrapper.py')
    check_file_exists('fixed_webapp.py')

    # Check directories and their contents
    check_directory_contents('templates')
    check_directory_contents('static')
    check_directory_contents('news_data')

    # Check for required modules
    check_imported_modules()

    # Ensure required directories exist
    ensure_directories()

    # Create sample data if needed
    create_sample_cluster_data()

    print("\nDebugging complete. Run your application using:")
    print("python fixed_webapp.py")


if __name__ == "__main__":
    main()