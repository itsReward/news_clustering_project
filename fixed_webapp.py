import os
import time
import webbrowser
import threading
import json
import logging
from flask import Flask, render_template, jsonify, send_from_directory, redirect, url_for

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("webapp.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class WebApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.port = 1234
        self.setup_routes()

    def setup_routes(self):
        """Set up the Flask routes with error handling"""

        # Add a default route handler
        @self.app.route('/')
        def index():
            try:
                logger.info("Rendering index page")
                if os.path.exists('templates/index.html'):
                    return render_template('index.html')
                else:
                    logger.error("templates/index.html does not exist!")
                    return """
                    <html>
                    <head><title>Error</title></head>
                    <body>
                        <h1>Template Error</h1>
                        <p>The index.html template could not be found. Please make sure the templates directory exists and contains the required files.</p>
                    </body>
                    </html>
                    """
            except Exception as e:
                logger.exception(f"Error rendering index page: {str(e)}")
                return f"Error rendering index page: {str(e)}"

        # Add a fallback for favicon requests
        @self.app.route('/favicon.ico')
        def favicon():
            return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

        # Static file serving with error handling
        @self.app.route('/static/<path:path>')
        def serve_static(path):
            try:
                logger.info(f"Serving static file: {path}")
                if os.path.exists(os.path.join('static', path)):
                    return send_from_directory('static', path)
                else:
                    logger.error(f"Static file not found: {path}")
                    return f"Static file not found: {path}", 404
            except Exception as e:
                logger.exception(f"Error serving static file {path}: {str(e)}")
                return f"Error serving static file: {str(e)}", 500

        # API endpoint for cluster data
        @self.app.route('/api/clusters')
        def get_clusters():
            try:
                logger.info("Fetching cluster data")
                cluster_data_path = 'static/cluster_data.json'

                if os.path.exists(cluster_data_path):
                    with open(cluster_data_path, 'r') as f:
                        cluster_data = json.load(f)
                    return jsonify(cluster_data)
                else:
                    logger.error("Cluster data file not found")
                    return jsonify({"error": "Cluster data not found"}), 404
            except Exception as e:
                logger.exception(f"Error retrieving cluster data: {str(e)}")
                return jsonify({"error": str(e)}), 500

        # Individual cluster view
        @self.app.route('/cluster/<cluster_id>')
        def show_cluster(cluster_id):
            try:
                logger.info(f"Showing cluster {cluster_id}")
                cluster_data_path = 'static/cluster_data.json'

                if os.path.exists(cluster_data_path):
                    with open(cluster_data_path, 'r') as f:
                        cluster_data = json.load(f)

                    cluster_id_str = str(cluster_id)
                    if cluster_id_str in cluster_data:
                        if os.path.exists('templates/cluster.html'):
                            return render_template('cluster.html',
                                                   cluster_id=cluster_id,
                                                   articles=cluster_data[cluster_id_str])
                        else:
                            logger.error("templates/cluster.html does not exist!")
                            return "The cluster.html template is missing", 500
                    else:
                        logger.warning(f"Cluster {cluster_id} not found")
                        return f"Cluster {cluster_id} not found", 404
                else:
                    logger.error("Cluster data file not found")
                    return "Cluster data not found", 404
            except Exception as e:
                logger.exception(f"Error displaying cluster {cluster_id}: {str(e)}")
                return f"Error: {str(e)}", 500

        # Test route to verify basic functionality
        @self.app.route('/test')
        def test():
            return "Web server is running correctly!"

    def create_templates(self):
        """Create the HTML templates for the web application"""
        try:
            logger.info("Creating HTML templates")

            # Ensure directories exist
            os.makedirs('templates', exist_ok=True)
            os.makedirs('static', exist_ok=True)

            # Create a simple index.html if needed
            if not os.path.exists('templates/index.html'):
                with open('templates/index.html', 'w') as f:
                    f.write('''<!DOCTYPE html>
<html>
<head>
    <title>News Article Clusters</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
    </style>
</head>
<body>
    <h1>News Article Clusters</h1>
    <p>This is a simple version of the index page.</p>
    <p><a href="/test">Test if server is running</a></p>
</body>
</html>''')

            # Create a simple cluster.html if needed
            if not os.path.exists('templates/cluster.html'):
                with open('templates/cluster.html', 'w') as f:
                    f.write('''<!DOCTYPE html>
<html>
<head>
    <title>Cluster View</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
    </style>
</head>
<body>
    <h1>Cluster {{cluster_id}}</h1>
    <p><a href="/">Back to index</a></p>
    <ul>
    {% for article in articles %}
        <li>
            <strong>{{ article.title }}</strong><br>
            {{ article.newspaper }} - {{ article.category }}<br>
            <a href="{{ article.url }}" target="_blank">Read Article</a>
        </li>
    {% endfor %}
    </ul>
</body>
</html>''')

            logger.info("Templates created successfully")
            return True
        except Exception as e:
            logger.exception(f"Error creating templates: {str(e)}")
            return False

    def browser_opener(self):
        """Open browser with error handling"""
        try:
            time.sleep(2)  # Wait a bit longer for Flask to start
            url = f'http://localhost:{self.port}'
            logger.info(f"Opening browser at {url}")
            webbrowser.open(url)
        except Exception as e:
            logger.error(f"Failed to open browser: {str(e)}")

    def run(self):
        """Run the Flask web server with better error handling"""
        try:
            # Create templates if needed
            self.create_templates()

            # Create dummy cluster data if none exists
            if not os.path.exists('static/cluster_data.json'):
                logger.warning("No cluster data found, creating dummy data")
                with open('static/cluster_data.json', 'w') as f:
                    json.dump({
                        "0": [
                            {
                                "title": "Sample Article 1",
                                "url": "http://example.com",
                                "newspaper": "Sample News",
                                "category": "Sample Category",
                                "date_scraped": "2025-05-08"
                            }
                        ]
                    }, f)

            # Check for critical files before starting
            critical_files = {
                'templates/index.html': os.path.exists('templates/index.html'),
                'templates/cluster.html': os.path.exists('templates/cluster.html'),
                'static/cluster_data.json': os.path.exists('static/cluster_data.json')
            }

            logger.info("Critical file status:")
            for file, exists in critical_files.items():
                logger.info(f"  - {file}: {'✓' if exists else '✗'}")

            # Open browser in a separate thread
            logger.info(f"Starting browser thread for http://localhost:{self.port}")
            browser_thread = threading.Thread(target=self.browser_opener)
            browser_thread.daemon = True
            browser_thread.start()

            # Start the Flask app
            logger.info(f"Starting Flask server on port {self.port}")
            self.app.run(host='0.0.0.0', port=self.port, debug=False)

        except Exception as e:
            logger.exception(f"Failed to start web server: {str(e)}")


def test_webapp():
    """Function to test just the web app functionality"""
    logger.info("Testing web app functionality")

    # Create required directories
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)

    # Create a simple web app
    webapp = WebApp()
    webapp.create_templates()

    # Run the web app
    webapp.run()


if __name__ == "__main__":
    test_webapp()