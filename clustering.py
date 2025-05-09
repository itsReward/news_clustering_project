import pandas as pd
import glob
import os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from collections import defaultdict
import json


# Load all CSV files into a single DataFrame
def load_data():
    # Get list of CSV files
    all_files = glob.glob('news_data/*.csv')

    if not all_files:
        print("No CSV files found in news_data directory!")
        print("Current directory:", os.getcwd())
        print("Files in news_data:",
              os.listdir('news_data') if os.path.exists('news_data') else "Directory doesn't exist")

        # Create some dummy data for testing if no files exist
        print("Creating dummy data for testing...")
        if not os.path.exists('news_data'):
            os.makedirs('news_data')

        # Create a dummy CSV file
        with open('news_data/dummy_data.csv', 'w', newline='', encoding='utf-8') as f:
            f.write('newspaper,category,title,url,content,date_scraped\n')
            # Add some dummy rows
            for i in range(20):
                category = ['Business', 'Politics', 'Arts/Culture/Celebrities', 'Sports'][i % 4]
                f.write(
                    f'Dummy News,{category},Article {i},http://example.com/{i},This is content for article {i},{pd.Timestamp.now().strftime("%Y-%m-%d")}\n')

        all_files = glob.glob('news_data/*.csv')

    dfs = []
    for file in all_files:
        try:
            df = pd.read_csv(file)
            if not df.empty:
                dfs.append(df)
                print(f"Loaded {len(df)} rows from {file}")
            else:
                print(f"File is empty: {file}")
        except Exception as e:
            print(f"Error loading {file}: {str(e)}")

    if not dfs:
        raise ValueError("No valid data found in CSV files")

    return pd.concat(dfs, ignore_index=True)


# Preprocess text data
def preprocess_data(df):
    # Basic preprocessing to clean the text
    df['clean_content'] = df['content'].fillna('').astype(str).str.lower()

    # TF-IDF vectorization
    vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
    X = vectorizer.fit_transform(df['clean_content'])

    print(f"Vectorized {X.shape[0]} articles with {X.shape[1]} features")

    return X, vectorizer


# Cluster the articles
def cluster_articles(X, num_clusters=4):
    # Using KMeans for clustering
    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X)

    print(f"Created {num_clusters} clusters")

    return clusters


# Visualize clusters
def visualize_clusters(X, clusters, df):
    # Create static directory if it doesn't exist
    if not os.path.exists('static'):
        os.makedirs('static')

    # Reduce dimensions for visualization
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X.toarray())

    plt.figure(figsize=(10, 8))

    # Create a color map based on category
    category_to_color = {
        'Business': 'blue',
        'Politics': 'red',
        'Arts/Culture/Celebrities': 'green',
        'Sports': 'purple'
    }

    # Plot by category for comparison
    plt.subplot(1, 2, 1)
    for category, color in category_to_color.items():
        mask = df['category'] == category
        plt.scatter(X_pca[mask, 0], X_pca[mask, 1], c=color, label=category, alpha=0.7)

    plt.title('Articles by Category')
    plt.xlabel('PCA Component 1')
    plt.ylabel('PCA Component 2')
    plt.legend()

    # Plot by cluster
    plt.subplot(1, 2, 2)
    plt.scatter(X_pca[:, 0], X_pca[:, 1], c=clusters, cmap='viridis', alpha=0.7)
    plt.title('Articles by Cluster')
    plt.xlabel('PCA Component 1')
    plt.ylabel('PCA Component 2')

    plt.tight_layout()
    plt.savefig('static/clusters.png')
    print("Saved cluster visualization to static/clusters.png")
    plt.close()


# Save cluster data for web display
def save_cluster_data(df, clusters):
    df['cluster'] = clusters

    # Create a dictionary of clusters and their articles
    cluster_data = defaultdict(list)

    for i, row in df.iterrows():
        cluster_data[int(row['cluster'])].append({
            'title': row['title'],
            'url': row['url'],
            'newspaper': row['newspaper'],
            'category': row['category']
        })

    # Save as JSON for the web application
    with open('static/cluster_data.json', 'w') as f:
        json.dump(dict(cluster_data), f)

    print("Saved cluster data to static/cluster_data.json")

    return cluster_data


# Main clustering function
def run_clustering():
    print("Loading data from CSV files...")
    df = load_data()

    print("Preprocessing and vectorizing text data...")
    X, vectorizer = preprocess_data(df)

    print("Clustering articles...")
    clusters = cluster_articles(X)

    print("Visualizing clusters...")
    visualize_clusters(X, clusters, df)

    print("Saving cluster data...")
    cluster_data = save_cluster_data(df, clusters)

    # Print cluster statistics
    print("\nCluster Statistics:")
    for cluster in sorted(cluster_data.keys()):
        print(f"Cluster {cluster}: {len(cluster_data[cluster])} articles")

        # Count categories in this cluster
        category_count = defaultdict(int)
        for article in cluster_data[cluster]:
            category_count[article['category']] += 1

        for category, count in sorted(category_count.items()):
            print(f"  - {category}: {count} articles")
        print()

    return cluster_data


if __name__ == "__main__":
    run_clustering()