import os
import time
import sys
import subprocess


def run_scrapy_spider():
    print("Starting web scraping...")
    try:
        # Run the spider directly using scrapy runspider command
        result = subprocess.run(
            ["scrapy", "runspider", "spider.py", "-s", "ROBOTSTXT_OBEY=False", "-s",
             "USER_AGENT='News Scraper for Academic Project'"],
            capture_output=True,
            text=True
        )

        # Print the output and error messages
        if result.stdout:
            print("Spider output:")
            print(result.stdout)

        if result.stderr:
            print("Spider errors:")
            print(result.stderr)

        if result.returncode == 0:
            print("Web scraping completed successfully.")
        else:
            print(f"Web scraping failed with return code {result.returncode}.")
    except Exception as e:
        print(f"Error running spider: {str(e)}")

    # Check if any data was collected
    csv_files = [f for f in os.listdir('news_data') if f.endswith('.csv')]
    print(f"Found {len(csv_files)} CSV files in news_data directory")


def run_clustering_analysis():
    print("Starting clustering analysis...")
    try:
        # Import and run the clustering module
        from clustering import run_clustering
        cluster_data = run_clustering()
        print("Clustering analysis completed.")
        return cluster_data
    except Exception as e:
        print(f"Error in clustering analysis: {str(e)}")
        raise


def start_web_server():
    print("Starting web server...")
    try:
        # Start the Flask web server
        from web_app import app
        app.run(host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"Error starting web server: {str(e)}")


if __name__ == "__main__":
    # Create necessary directories
    if not os.path.exists('static'):
        os.makedirs('static')

    if not os.path.exists('news_data'):
        os.makedirs('news_data')

    if not os.path.exists('templates'):
        os.makedirs('templates')

    # Create template files if they don't exist
    if not os.path.exists('templates/index.html'):
        with open('templates/index.html', 'w') as f:
            f.write('''<!DOCTYPE html>
<html>
<head>
    <title>News Article Clusters</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css">
    <style>
        .cluster-card {
            margin-bottom: 20px;
            transition: transform 0.3s;
        }
        .cluster-card:hover {
            transform: scale(1.03);
        }
    </style>
</head>
<body>
    <div class="container mt-5">
        <h1 class="text-center mb-5">News Article Clusters</h1>

        <div class="row">
            <div class="col-md-8 offset-md-2">
                <img src="/static/clusters.png" class="img-fluid mb-4" alt="Cluster Visualization">
            </div>
        </div>

        <div class="row" id="clusters-container">
            <!-- Clusters will be loaded here via JavaScript -->
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            fetch('/api/clusters')
                .then(response => response.json())
                .then(data => {
                    const container = document.getElementById('clusters-container');

                    Object.keys(data).forEach(clusterId => {
                        const articles = data[clusterId];
                        const categoryCount = {};

                        // Count categories in this cluster
                        articles.forEach(article => {
                            if (!categoryCount[article.category]) {
                                categoryCount[article.category] = 0;
                            }
                            categoryCount[article.category]++;
                        });

                        // Create category distribution text
                        let categoryText = '';
                        Object.keys(categoryCount).forEach(category => {
                            categoryText += `${category}: ${categoryCount[category]} articles<br>`;
                        });

                        const clusterCard = document.createElement('div');
                        clusterCard.className = 'col-md-6 col-lg-4';
                        clusterCard.innerHTML = `
                            <div class="card cluster-card">
                                <div class="card-body">
                                    <h5 class="card-title">Cluster ${clusterId}</h5>
                                    <p class="card-text">
                                        <strong>Articles:</strong> ${articles.length}<br>
                                        <strong>Categories:</strong><br>${categoryText}
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
                        '<div class="alert alert-danger">Error loading cluster data. Please check the console for details.</div>';
                });
        });
    </script>
</body>
</html>''')

    if not os.path.exists('templates/cluster.html'):
        with open('templates/cluster.html', 'w') as f:
            f.write('''<!DOCTYPE html>
<html>
<head>
    <title>Cluster - News Articles</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css">
</head>
<body>
    <div class="container mt-5">
        <h1 class="mb-4">Cluster {{cluster_id}}</h1>
        <a href="/" class="btn btn-secondary mb-4">Back to Clusters</a>

        <div class="table-responsive">
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>Title</th>
                        <th>Newspaper</th>
                        <th>Category</th>
                        <th>URL</th>
                    </tr>
                </thead>
                <tbody>
                    {% for article in articles %}
                    <tr>
                        <td>{{ article.title }}</td>
                        <td>{{ article.newspaper }}</td>
                        <td>{{ article.category }}</td>
                        <td><a href="{{ article.url }}" target="_blank">Read Article</a></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>''')

    # Run the spider to collect data
    run_scrapy_spider()

    # Run the clustering analysis
    cluster_data = run_clustering_analysis()

    # Start the web server
    start_web_server()