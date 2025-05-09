# Zimbabwe News Article Clustering Application - User Guide

This guide will help you understand how to use the Zimbabwe News Article Clustering Application and explain how it works.

## Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Understanding the Web Scraper](#understanding-the-web-scraper)
4. [Understanding the Clustering Algorithm](#understanding-the-clustering-algorithm)
5. [Using the Web Interface](#using-the-web-interface)
6. [Troubleshooting](#troubleshooting)
7. [Extending the Application](#extending-the-application)

## Overview

The Zimbabwe News Article Clustering Application is a comprehensive system that:

1. Scrapes news articles from various online newspapers
2. Categorizes these articles into different topics (Business, Politics, Arts/Culture/Celebrities, Sports)
3. Clusters the articles based on their categories
4. Presents the clustered articles in a web interface for easy browsing

The application consists of three main components:

- **Web Scraper (`newspaper_scrapper.py`)**: Collects articles from configured news sources
- **Clustering Algorithm (`cluster_articles.py`)**: Organizes articles into meaningful groups
- **Web Interface (`fixed_webapp.py`)**: Displays the clusters and articles in a user-friendly way

## Getting Started

The easiest way to get started is to use the provided installation script:

```bash
python install_and_run.py
```

This script will:
1. Check your Python version
2. Install required packages
3. Set up HTML templates
4. Create sample data if needed
5. Start the web application

Alternatively, you can manually run each component:

1. Set up templates:
   ```bash
   python setup_templates.py
   ```

2. Create cluster data:
   ```bash
   python cluster_articles.py
   ```

3. Run the web application:
   ```bash
   python fixed_webapp.py
   ```

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

The clustering algorithm (`cluster_articles.py`) organizes the scraped articles into meaningful groups.

### How it Works

1. It loads article data from the CSV files
2. It categorizes articles based on their assigned categories
3. It creates clusters for each category
4. The clustered data is saved to `static/cluster_data.json` for the web interface

### Advanced Clustering Options

The current implementation uses a simple approach of clustering by category. However, the code includes commented sections for more advanced approaches:

- **TF-IDF Vectorization**: Converts article content into numerical features
- **K-means Clustering**: Groups articles based on content similarity

You can enable these advanced options by uncommenting the relevant sections in `cluster_articles.py`.

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

1. **Web application not starting**
   - Make sure you're running `fixed_webapp.py`, not `newspaper_scrapper.py`
   - Check that the required packages are installed
   - Look for error messages in the console or log files

2. **No clusters appearing**
   - Check if `static/cluster_data.json` exists and has valid content
   - Run `cluster_articles.py` to generate the cluster data

3. **Scraper not collecting articles**
   - The website structures may have changed; update the selectors
   - Check your internet connection
   - The website might be blocking automated scrapers

### Logging

The application creates several log files:
- `scraper.log`: Logs from the web scraper
- `clustering.log`: Logs from the clustering algorithm
- `webapp.log`: Logs from the web application

Check these files for detailed error information.

## Extending the Application

### Adding New Features

1. **Additional Categories**: Modify the `categories` dictionary in `newspaper_scrapper.py`

2. **New Clustering Methods**: Implement alternative clustering algorithms in `cluster_articles.py`

3. **Enhanced Web Interface**: Modify the HTML templates in the `templates/` directory

### Integration with Other Systems

The application's modular design allows for integration with other systems:

1. **Database Storage**: Replace CSV files with a database

2. **API Service**: Add API endpoints to the web application

3. **Automated Scraping**: Set up scheduled tasks to run the scraper regularly

---

## Technical Details

### File Structure

```
project_root/
├── newspaper_scrapper.py     # Web scraper
├── fixed_webapp.py           # Web application
├── cluster_articles.py       # Clustering algorithm
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
