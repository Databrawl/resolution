from pprint import pprint

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

from research.hdbscan_gpt import cluster

# Load the dataset
file_path = 'customer_support_tickets.csv'
tickets_df = pd.read_csv(file_path)


def print_values(tickets_df):
    # Display unique values in the 'Ticket Type' column
    ticket_types = tickets_df['Ticket Type'].unique()
    print('Ticket Types:')
    print(ticket_types)

    print('Ticket subjects:')
    for ts in tickets_df['Ticket Subject'].unique():
        print(ts)

    # Filter rows with 'Product Recommendation' as 'Ticket Subject'
    product_recommendation_tickets = tickets_df[
        tickets_df['Ticket Subject'] == 'Product recommendation']

    # Vectorizing the descriptions in all tickets for analysis
    all_descriptions = tickets_df['Ticket Description']

    # Applying TF-IDF vectorization
    vectorizer = TfidfVectorizer(stop_words='english')
    X_all = vectorizer.fit_transform(all_descriptions)

    # Using KMeans to cluster all ticket descriptions into 10 clusters
    n_clusters_all = 10
    model_all = KMeans(n_clusters=n_clusters_all, random_state=42)
    model_all.fit(X_all)

    # Getting cluster assignments for each description
    all_clusters = model_all.predict(X_all)

    # Summarizing the different types of issues in each cluster
    all_tickets_issues_summary = {}
    for i in range(n_clusters_all):
        cluster_indices = np.where(all_clusters == i)[0]
        cluster_descriptions = all_descriptions.iloc[cluster_indices]
        all_tickets_issues_summary[f"Cluster {i + 1}"] = cluster_descriptions.sample(
            min(5, len(cluster_descriptions))).tolist()

    pprint(all_tickets_issues_summary)


def cluster_hdb(tickets_df):
    descriptions = tickets_df['Ticket Description']
    topics = cluster(descriptions)
    pprint(topics)


if __name__ == '__main__':
    cluster_hdb(tickets_df)
