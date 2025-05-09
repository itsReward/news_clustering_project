#!/usr/bin/env python3
"""
Script to ensure all necessary HTML templates are available
"""
import os
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("setup.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def ensure_directory(directory):
    """Ensure a directory exists"""
    if not os.path.exists(directory):
        logger.info(f"Creating directory: {directory}")
        os.makedirs(directory)
    else:
        logger.info(f"Directory already exists: {directory}")


def create_or_update_template(filename, content):
    """Create or update a template file"""
    # Check if file exists
    if os.path.exists(filename):
        # Read existing content
        with open(filename, 'r') as f:
            existing_content = f.read()

        # Only update if content is different
        if existing_content != content:
            logger.info(f"Updating template: {filename}")
            with open(filename, 'w') as f:
                f.write(content)
        else:
            logger.info(f"Template already up to date: {filename}")
    else:
        # Create new file
        logger.info(f"Creating template: {filename}")
        with open(filename, 'w') as f:
            f.write(content)


def setup_templates():
    """Set up all necessary templates"""
    # Ensure templates directory exists
    ensure_directory('templates')

    # Create or update index.html
    index_html = """<!DOCTYPE html>
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
</html>"""

    # Create or update cluster.html
    cluster_html = """<!DOCTYPE html>
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
</html>"""

    # Create template files
    create_or_update_template('templates/index.html', index_html)
    create_or_update_template('templates/cluster.html', cluster_html)

    # Ensure static directory exists
    ensure_directory('static')

    # Create a placeholder clusters image
    create_placeholder_clusters_image()

    # Create news_data directory if it doesn't exist
    ensure_directory('news_data')

    logger.info("Template setup complete.")
    print("✓ Template setup complete. All necessary template files have been created or updated.")


def create_placeholder_clusters_image():
    """Create a simple placeholder image for clusters visualization"""
    try:
        import numpy as np
        from PIL import Image, ImageDraw

        # Create a sample cluster visualization
        width, height = 800, 400
        image = Image.new('RGB', (width, height), color=(240, 240, 240))
        draw = ImageDraw.Draw(image)

        # Draw some circles to represent clusters
        colors = [(66, 133, 244), (219, 68, 55), (244, 180, 0), (15, 157, 88)]
        np.random.seed(42)  # For reproducibility

        for i in range(4):
            # Draw cluster circles
            center_x = 150 + i * 170
            center_y = 200
            radius = 60 + np.random.randint(-10, 10)

            # Draw the main cluster circle
            draw.ellipse(
                [(center_x - radius, center_y - radius), (center_x + radius, center_y + radius)],
                fill=colors[i],
                outline=(255, 255, 255)
            )

            # Draw some small dots around to represent articles
            for _ in range(15):
                angle = np.random.uniform(0, 2 * np.pi)
                distance = np.random.uniform(0.4 * radius, 0.9 * radius)
                dot_x = center_x + distance * np.cos(angle)
                dot_y = center_y + distance * np.sin(angle)
                dot_size = np.random.randint(3, 8)

                # Draw a small white circle
                draw.ellipse(
                    [(dot_x - dot_size, dot_y - dot_size), (dot_x + dot_size, dot_y + dot_size)],
                    fill=(255, 255, 255)
                )

        # Add labels
        labels = ["Sports", "Arts/Culture", "Business", "Politics"]
        for i, label in enumerate(labels):
            center_x = 150 + i * 170
            center_y = 200 + 80
            draw.text((center_x - 30, center_y), label, fill=(0, 0, 0))

        # Save the image
        image.save('static/clusters.png')
        logger.info("Created placeholder clusters image")
    except ImportError:
        logger.info("Could not create placeholder image - PIL or numpy not installed")
        # Create an empty file as a placeholder
        with open('static/clusters.png', 'wb') as f:
            pass


if __name__ == "__main__":
    setup_templates()