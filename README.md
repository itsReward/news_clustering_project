# News Article Clustering Application - User Guide

This guide will help understand how to use the News Article Clustering Application and explain how it works.

## Table of Contents

1. [Overview](#overview)
2. [Complete Workflow](#complete-workflow)
3. [Step-by-Step Guide](#step-by-step-guide)
4. [Understanding the Web Scraper](#understanding-the-web-scraper)
5. [Understanding the Clustering Algorithm](#understanding-the-clustering-algorithm)
6. [Using the Web Interface](#using-the-web-interface)
7. [Troubleshooting](#troubleshooting)
8. [Debugging Tools](#debugging-tools)
9. [Extending the Application](#extending-the-application)

## Overview

The News Article Clustering Application is a comprehensive system that:

1. Scrapes news articles from various online newspapers
2. Categorizes these articles into different topics (Business, Politics, Arts/Culture/Celebrities, Sports)
3. Clusters the articles based on their categories
4. Presents the clustered articles in a web interface for easy browsing

The application consists of three main components:

- **Web Scraper (`newspaper_scrapper.py`)**: Collects articles from configured news sources
- **Data Processor (`process_scraped_data.py`)**: Organizes articles into meaningful clusters
- **Web Interface (`webapp.py`)**: Displays the clusters and articles in a user-friendly way

## Complete Workflow

The easiest way to run the entire application is to use the complete workflow script:

```bash
python workflow.py
```

This script guides you through the entire process:
1. Checks your Python version and installs required packages
2. Runs the web scraper to collect articles
3. Processes the scraped data to create clusters
4. Sets up the necessary HTML templates
5. Starts the web application

This is the recommended approach, especially if you're encountering issues with displaying your scraped data.

## Step-by-Step Guide

If you prefer to run each component manually, follow these steps:

### 1. Install Dependencies

```bash
pip install flask requests beautifulsoup4 pandas scikit-learn pillow numpy
```

### 2. Run the Web Scraper

```bash
python newspaper_scrapper.py
```

This will collect articles from the configured news sources and save them to CSV files in the `news_data/` directory.

### 3. Process the Scraped Data

```bash
python process_scraped_data.py
```

This critical step reads your scraped data from `news_data/all_articles.csv` and creates clusters for the web application.

### 4. Run the Web Application

```bash
python fixed_webapp.py
```

This starts the web interface where you can browse the clustered articles.

## Understanding the Web Scraper

The web scraper (`newspaper_scrapper.py`) is designed to collect articles from various online newspapers.

### How it Works

1. It connects to the configured newspaper websites
2. For each newspaper, it navigates to different category pages (Business, Politics, etc.)
3. It extracts article links, titles, and content
4. The collected data is saved to CSV files in the `news_data/` directory

### Configured Newspapers

The scraper is currently configured to collect articles from:
- Independent
- CNN
- BBC
- iHarare
- The Herald (Zimbabwe's national newspaper)

### Customizing the Scraper

To add or modify news sources, you can edit the `define_newspaper_structures` method in `newspaper_scrapper.py`. Each news source requires:

- `name`: The display name of the newspaper
- `base_url`: The main URL of the newspaper
- `categories`: URLs for each category page
- Selectors for articles, titles, and content

## Understanding the Clustering Algorithm

The data processing scripts (`process_scraped_data.py` and `cluster_articles.py`) organize the scraped articles into meaningful groups.

### How it Works

1. It loads article data from `news_data/all_articles.csv`
2. It categorizes articles based on their assigned categories
3. It creates clusters for each category
4. The clustered data is saved to `static/cluster_data.json` for the web interface

### Advanced Clustering Options

The current implementation uses a simple approach of clustering by category. However, the code includes options for more advanced approaches:

- **TF-IDF Vectorization**: Converts article content into numerical features
- **K-means Clustering**: Groups articles based on content similarity

These advanced options can be enabled by modifying the relevant sections in `process_scraped_data.py`.

## Using the Web Interface

The web interface (`fixed_webapp.py`) provides a user-friendly way to browse the clustered articles.

### How to Access

After starting the application, open your web browser and navigate to:
```
http://localhost:5007
```

### Main Page

The main page shows:
- A visualization of the clusters
- Cards for each cluster, showing:
  - Cluster ID
  - Number of articles
  - Distribution of categories

### Cluster View

Clicking on a cluster card takes you to the cluster view, which shows:
- All articles in the selected cluster
- Article details (title, newspaper, category)
- Links to read the original articles

## Troubleshooting

### Common Issues

1. **Web application showing dummy data instead of scraped data**
   - Make sure you've run `process_scraped_data.py` after scraping
   - Check that `news_data/all_articles.csv` exists and contains your data
   - Use `debug_csv.py` to diagnose issues with your CSV file

2. **Web application not starting**
   - Make sure you're running `fixed_webapp.py`, not `newspaper_scrapper.py`
   - Check that the required packages are installed
   - Look for error messages in the console or log files

3. **No clusters appearing**
   - Check if `static/cluster_data.json` exists and has valid content
   - Run `process_scraped_data.py` to generate the cluster data from your CSV

4. **Scraper not collecting articles**
   - The website structures may have changed; update the selectors
   - Check your internet connection
   - The website might be blocking automated scrapers

### Data Flow Issues

If you're having issues with the data flow between components, run the complete workflow script with the `--verbose` flag:

```bash
python workflow.py --verbose
```

This will show detailed logs of each step, helping you identify where the process is breaking down.

### Logging

The application creates several log files:
- `scraper.log`: Logs from the web scraper
- `process_data.log`: Logs from the data processing
- `webapp.log`: Logs from the web application

Check these files for detailed error information.

## Debugging Tools

The application includes several debugging tools to help you diagnose and fix issues:

### CSV Debugger

If you suspect issues with your CSV data, run:

```bash
python debug_csv.py
```

This tool:
- Checks if your CSV file exists and can be read
- Displays the content and structure of the file
- Tests the clustering process with your real data
- Attempts to fix common issues with the CSV file

### Install and Run Script

For a guided installation and setup experience:

```bash
python install_and_run.py
```

This script helps you correctly set up all dependencies and components.


---

## Technical Details

### File Structure

```
project_root/
├── newspaper_scrapper.py     # Web scraper
├── process_scraped_data.py   # Processes CSV data into clusters
├── webapp.py                 # Web application
├── debug_csv.py              # Tool for diagnosing CSV issues
├── workflow.py               # Complete workflow script
├── setup_templates.py        # Template setup
├── install_and_run.py        # Installation script
├── README.md                 # Project overview
├── USER_GUIDE.md             # This user guide
├── news_data/                # Directory for scraped data
│   └── all_articles.csv      # CSV file with scraped articles
├── static/                   # Static files for web app
│   ├── cluster_data.json     # Clustered article data
│   └── clusters.png          # Cluster visualization
└── templates/                # HTML templates
    ├── index.html            # Main page template
    └── cluster.html          # Cluster view template
```

### Dependencies

- **Flask**: Web framework
- **Requests**: HTTP library
- **BeautifulSoup4**: HTML parsing
- **Pandas**: Data handling
- **scikit-learn**: Machine learning and clustering
- **PIL**: Image processing
- **NumPy**: Numerical computing
