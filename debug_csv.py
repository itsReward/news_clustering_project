#!/usr/bin/env python3
"""
Debugging script for CSV data in the Zimbabwe News Article Clustering application
This script helps diagnose issues with reading and processing the CSV data
"""
import os
import sys
import pandas as pd
import json


def print_header(message):
    """Print a formatted header message"""
    print("\n" + "=" * 80)
    print(f" {message}")
    print("=" * 80)


def check_csv_file():
    """Check if the CSV file exists and is readable"""
    print_header("Checking CSV File")

    csv_path = "news_data/all_articles.csv"

    if not os.path.exists(csv_path):
        print(f"❌ Error: CSV file not found at {csv_path}")
        print("Possible solutions:")
        print("1. Make sure you have run the scraper (newspaper_scrapper.py)")
        print("2. Check if the file is in a different location")
        return False

    print(f"✅ CSV file found at {csv_path}")

    # Check file size
    file_size = os.path.getsize(csv_path) / 1024  # Size in KB
    print(f"File size: {file_size:.2f} KB")

    if file_size < 1:
        print("❌ Warning: File size is very small, it might be empty")

    return True


def read_csv_file():
    """Attempt to read the CSV file and display its contents"""
    print_header("Reading CSV File")

    csv_path = "news_data/all_articles.csv"

    try:
        df = pd.read_csv(csv_path)
        print(f"✅ Successfully read CSV file with {len(df)} rows and {len(df.columns)} columns")

        # Display column names
        print("\nColumns:")
        for i, col in enumerate(df.columns):
            print(f"  {i + 1}. {col}")

        # Check if required columns exist
        required_columns = ['newspaper', 'category', 'title', 'url', 'content', 'date_scraped']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            print(f"\n❌ Warning: Missing required columns: {', '.join(missing_columns)}")
            print("These columns are needed for the clustering to work correctly.")
        else:
            print("\n✅ All required columns are present")

        # Display a sample of the data
        print("\nSample data (first 3 rows):")
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        print(df.head(3))

        # Check for empty values
        empty_counts = df.isna().sum()
        if empty_counts.sum() > 0:
            print("\n❌ Warning: Found empty values in the following columns:")
            for col, count in empty_counts.items():
                if count > 0:
                    print(f"  {col}: {count} empty values")
        else:
            print("\n✅ No empty values found in the data")

        return df

    except Exception as e:
        print(f"❌ Error reading CSV file: {str(e)}")
        print("Possible solutions:")
        print("1. Check if the file is corrupt or in an unexpected format")
        print("2. Try opening the file in Excel or a text editor to verify its contents")
        return None


def check_clustering():
    """Check if the clustering process works correctly"""
    print_header("Testing Clustering Process")

    csv_path = "news_data/all_articles.csv"

    try:
        # Read CSV
        df = pd.read_csv(csv_path)

        # Get unique categories
        if 'category' in df.columns:
            categories = df['category'].unique()
            print(f"Found {len(categories)} unique categories: {', '.join(categories)}")

            # Create clusters based on categories
            clusters = {}
            for i, category in enumerate(categories):
                # Filter articles for this category
                category_articles = df[df['category'] == category]

                # Convert to list of dictionaries for JSON serialization
                articles_list = category_articles.to_dict('records')

                # Add to clusters
                clusters[str(i)] = articles_list

                print(f"Created cluster {i} for category '{category}' with {len(articles_list)} articles")

            # Save to a test file
            test_output = "static/test_cluster_data.json"
            with open(test_output, 'w') as f:
                json.dump(clusters, f, indent=2)

            print(f"\n✅ Successfully created test clusters and saved to {test_output}")
            print(f"To use this test data, rename the file to cluster_data.json")

            return True
        else:
            print("❌ Error: 'category' column not found in the CSV file")
            print("This column is required for clustering to work")
            return False

    except Exception as e:
        print(f"❌ Error during clustering test: {str(e)}")
        return False


def fix_csv_issues(df):
    """Attempt to fix common issues with the CSV data"""
    print_header("Fixing CSV Issues")

    if df is None:
        print("❌ Cannot fix issues as the CSV file could not be read")
        return False

    modified = False

    # Fix missing columns
    required_columns = ['newspaper', 'category', 'title', 'url', 'content', 'date_scraped']
    for col in required_columns:
        if col not in df.columns:
            print(f"Adding missing column: {col}")
            if col == 'date_scraped':
                df[col] = pd.Timestamp.now().strftime('%Y-%m-%d')
            else:
                df[col] = f"Missing {col}"
            modified = True

    # Fix empty values
    empty_counts = df.isna().sum()
    for col, count in empty_counts.items():
        if count > 0:
            print(f"Fixing {count} empty values in column: {col}")
            if col == 'date_scraped':
                df[col].fillna(pd.Timestamp.now().strftime('%Y-%m-%d'), inplace=True)
            elif col == 'category':
                # Try to infer categories from the title or content
                df[col].fillna('Uncategorized', inplace=True)
            else:
                df[col].fillna(f"Missing {col}", inplace=True)
            modified = True

    if modified:
        # Save the fixed CSV
        fixed_csv_path = "news_data/fixed_all_articles.csv"
        df.to_csv(fixed_csv_path, index=False)
        print(f"\n✅ Fixed issues and saved to {fixed_csv_path}")
        print(f"To use this fixed file, rename it to all_articles.csv")
        return True
    else:
        print("\n✅ No issues to fix in the CSV file")
        return True


def main():
    """Main function to run the debugging process"""
    print_header("Zimbabwe News Article Clustering - CSV Debugging")

    print("""This script will help diagnose and fix issues with the CSV data:
1. Check if the CSV file exists
2. Try to read the CSV file and display its contents
3. Test the clustering process
4. Attempt to fix common issues
""")

    # Check if the CSV file exists
    if not check_csv_file():
        print("\nCannot continue debugging as the CSV file was not found.")
        return

    # Try to read the CSV file
    df = read_csv_file()

    # Test the clustering process
    check_clustering()

    # Try to fix any issues
    fix_csv_issues(df)

    print_header("Debugging Complete")
    print("""
Next steps:
1. If issues were found and fixed, use the fixed CSV file
2. Run the clustering process again using process_scraped_data.py
3. Start the web application using fixed_webapp.py
""")


if __name__ == "__main__":
    main()