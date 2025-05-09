#!/usr/bin/env python3
"""
Complete workflow script for Zimbabwe News Article Clustering
This script guides you through the entire process from scraping to viewing the data
"""
import os
import sys
import subprocess
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("workflow.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def print_header(message):
    """Print a formatted header message"""
    print("\n" + "=" * 80)
    print(f" {message}")
    print("=" * 80)


def print_step(step_number, message):
    """Print a step message"""
    print(f"\n[Step {step_number}] {message}")


def run_command(command, description, verbose=True):
    """Run a system command and display output"""
    print(f"\n> {description}...")
    if verbose:
        print(f"> Running: {command}")

    try:
        result = subprocess.run(command, shell=True, check=True, text=True,
                                capture_output=not verbose)
        if verbose and result.stdout:
            print(result.stdout)
        return True, result.stdout if result.stdout else ""
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        if verbose and e.stderr:
            print(e.stderr)
        return False, e.stderr if e.stderr else ""


def check_python_version():
    """Check if Python version is compatible"""
    print_step(1, "Checking Python version")

    if sys.version_info < (3, 7):
        print(f"Python version {sys.version} is too old. This application requires Python 3.7 or higher.")
        return False

    print(f"✓ Python version {sys.version.split(' ')[0]} is compatible.")
    return True


def install_dependencies():
    """Install required Python packages"""
    print_step(2, "Installing required Python packages")

    packages = [
        "flask",
        "requests",
        "beautifulsoup4",
        "pandas",
        "scikit-learn",
        "pillow",
        "numpy"
    ]

    for package in packages:
        run_command(f"{sys.executable} -m pip install {package}",
                    f"Installing {package}", verbose=False)

    print("\n✓ Package installation complete.")
    return True


def run_web_scraper():
    """Run the newspaper scraper to collect articles"""
    print_step(3, "Running web scraper to collect articles")

    if not os.path.exists("newspaper_scrapper.py"):
        print("✗ Error: newspaper_scrapper.py not found!")
        return False

    print("This step will scrape articles from various news sources.")
    print("Depending on your internet connection, this may take several minutes.")

    success, _ = run_command(f"{sys.executable} newspaper_scrapper.py",
                             "Running web scraper", verbose=True)

    if success:
        print("\n✓ Web scraping complete.")

        # Verify that data was collected
        if os.path.exists("news_data/all_articles.csv"):
            import pandas as pd
            try:
                df = pd.read_csv("news_data/all_articles.csv")
                print(f"✓ Successfully collected {len(df)} articles.")
            except Exception as e:
                print(f"✗ Error reading scraped data: {str(e)}")
                return False
        else:
            print("✗ No data was collected. Check the logs for errors.")
            return False

        return True
    else:
        print("✗ Web scraping failed. Check the logs for errors.")
        return False


def process_data():
    """Process the scraped data to create clusters"""
    print_step(4, "Processing scraped data to create clusters")

    if not os.path.exists("process_scraped_data.py"):
        print("✗ Error: process_scraped_data.py not found!")
        return False

    success, _ = run_command(f"{sys.executable} process_scraped_data.py",
                             "Processing scraped data", verbose=True)

    if success:
        print("\n✓ Data processing complete.")

        # Verify that clusters were created
        if os.path.exists("static/cluster_data.json"):
            import json
            try:
                with open("static/cluster_data.json", "r") as f:
                    clusters = json.load(f)
                print(f"✓ Successfully created {len(clusters)} clusters.")
            except Exception as e:
                print(f"✗ Error reading cluster data: {str(e)}")
                return False
        else:
            print("✗ No clusters were created. Check the logs for errors.")
            return False

        return True
    else:
        print("✗ Data processing failed. Check the logs for errors.")
        return False


def setup_templates():
    """Ensure HTML templates are set up correctly"""
    print_step(5, "Setting up HTML templates")

    # Make sure templates directory exists
    os.makedirs("templates", exist_ok=True)

    # Check if the template files already exist
    has_templates = (
            os.path.exists("templates/index.html") and
            os.path.exists("templates/cluster.html")
    )

    if has_templates:
        print("✓ Template files already exist.")
        return True

    # Create template files if they don't exist
    if not os.path.exists("templates/index.html"):
        print("Creating index.html template...")
        with open("templates/index.html", "w") as f:
            f.write("""<!DOCTYPE html>
<html>
<head>
    <title>Zimbabwe News Article Clusters</title>
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
        <h1 class="text-center mb-5">Zimbabwe News Article Clusters</h1>

        <div class="row">
            <div class="col-md-10 offset-md-1">
                <img src="/static/clusters.png" class="img-fluid mb-4" alt="Cluster Visualization" onerror="this.style.display='none'">
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
                        clusterCard.className = 'col-md-6 col-lg-3';
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
</html>""")

    if not os.path.exists("templates/cluster.html"):
        print("Creating cluster.html template...")
        with open("templates/cluster.html", "w") as f:
            f.write("""<!DOCTYPE html>
<html>
<head>
    <title>Cluster - Zimbabwe News Articles</title>
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
</html>""")

    # Create static directory if it doesn't exist
    os.makedirs("static", exist_ok=True)

    print("✓ Template setup complete.")
    return True


def run_web_application():
    """Run the web application"""
    print_step(6, "Running the web application")

    if not os.path.exists("fixed_webapp.py"):
        print("✗ Error: fixed_webapp.py not found!")
        return False

    print("The web application will now start.")
    print("You can access it at: http://localhost:5007")
    print("Press Ctrl+C to stop the application when you're done.")

    time.sleep(2)  # Give the user time to read the message

    # Try to open the browser
    import webbrowser
    webbrowser.open("http://localhost:5007")

    # Run the web application
    os.system(f"{sys.executable} fixed_webapp.py")

    return True


def main():
    """Main function to run the entire workflow"""
    print_header("Zimbabwe News Article Clustering - Complete Workflow")

    print("""This script will guide you through the entire process:
1. Check Python version
2. Install required packages
3. Run the web scraper to collect articles
4. Process the scraped data to create clusters
5. Set up HTML templates
6. Run the web application

You will be able to view the clustered articles in your web browser.
""")

    # Ask if the user wants to continue
    print("Do you want to continue? (y/n)")
    choice = input().lower()
    if not choice.startswith('y'):
        print("Workflow cancelled.")
        return

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Install dependencies
    install_dependencies()

    # Set up templates
    setup_templates()

    # Run web scraper
    if not run_web_scraper():
        print("\nWeb scraping failed. Do you want to continue with the workflow? (y/n)")
        choice = input().lower()
        if not choice.startswith('y'):
            print("Workflow cancelled.")
            return

    # Process data
    if not process_data():
        print("\nData processing failed. Do you want to continue with the workflow? (y/n)")
        choice = input().lower()
        if not choice.startswith('y'):
            print("Workflow cancelled.")
            return

    # Run web application
    print_header("Workflow complete! Running the web application...")
    run_web_application()


if __name__ == "__main__":
    main()