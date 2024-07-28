import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.cluster import hierarchy
from scipy.spatial.distance import pdist, squareform
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import umap
from typing import List, Tuple
from itertools import combinations

def create_ranking_vector(rankings):
    """
    Create a ranking vector from a list of rankings.
    
    :param rankings: List of lists, where each inner list represents a trial's rankings
    :return: NumPy array representing the ranking vector
    """
    M = len(rankings)  # Number of trials
    N = len(rankings[0])  # Number of hypotheses per trial
    
    vector_length = M * (N * (N - 1) // 2)
    ranking_vector = np.zeros(vector_length, dtype=np.int8)
    
    idx = 0
    for trial_ranking in rankings:
        for i, j in combinations(range(N), 2):
            if trial_ranking[i] < trial_ranking[j]:
                ranking_vector[idx] = -1
            elif trial_ranking[i] > trial_ranking[j]:
                ranking_vector[idx] = 1
            # If equal, it remains 0
            idx += 1
    
    return ranking_vector

# Example usage
# M = 3  # Number of trials
# N = 4  # Number of hypotheses per trial

# # Simulating rankings for a judge
# # Each inner list represents a trial's rankings
# judge_rankings = [
#     [1, 2, 3, 4],  # Trial 1
#     [2, 1, 3, 4],  # Trial 2
#     [1, 3, 2, 4]   # Trial 3
# ]

# judge_vector = create_ranking_vector(judge_rankings)
# print(f"Judge's ranking vector: {judge_vector}")
# print(f"Vector length: {len(judge_vector)}")

def visualize_judges(judge_sets: List[Tuple[np.ndarray, str]], 
                     plot_type: str = 'PCA', 
                     n_components: int = 2,
                     random_state: int = 42,
                     figsize: Tuple[int, int] = (10, 8)):
    """
    Visualize multiple judges in judgment space.
    
    :param judge_sets: List of tuples, each containing (judge_vectors, set_label)
    :param plot_type: Type of plot ('PCA', 'UMAP', or 'TSNE')
    :param n_components: Number of components for dimensionality reduction
    :param random_state: Random state for reproducibility
    :param figsize: Figure size
    """
    # Combine all judge vectors
    all_judges = np.vstack([judges for judges, _ in judge_sets])
    
    # Perform dimensionality reduction
    if plot_type == 'PCA':
        reducer = PCA(n_components=n_components, random_state=random_state)
    elif plot_type == 'UMAP':
        reducer = umap.UMAP(n_components=n_components, random_state=random_state)
    elif plot_type == 'TSNE':
        reducer = TSNE(n_components=n_components, random_state=random_state)
    else:
        raise ValueError("Invalid plot_type. Choose 'PCA', 'UMAP', or 'TSNE'.")
    
    reduced_data = reducer.fit_transform(all_judges)
    
    # Plotting
    plt.figure(figsize=figsize)
    colors = plt.cm.rainbow(np.linspace(0, 1, len(judge_sets)))
    markers = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', 'h', 'H', '+', 'x', 'd', '|', '_']
    
    start_idx = 0
    for (judges, label), color, marker in zip(judge_sets, colors, markers):
        end_idx = start_idx + len(judges)
        plt.scatter(reduced_data[start_idx:end_idx, 0], 
                    reduced_data[start_idx:end_idx, 1], 
                    c=[color], 
                    marker=marker, 
                    label=label,
                    alpha=0.7)
        start_idx = end_idx
    
    plt.title(f"Judges in {plot_type} Space")
    plt.xlabel(f"{plot_type}1")
    plt.ylabel(f"{plot_type}2")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()

# Example usage
# M, N = 3, 4  # 3 trials, 4 hypotheses per trial

# # Generate random ranking vectors for demonstration
# np.random.seed(42)
# human_judges = np.random.randint(-1, 2, size=(10, M * (N * (N - 1) // 2)))
# ai_judges = np.random.randint(-1, 2, size=(5, M * (N * (N - 1) // 2)))

# # Visualize
# judge_sets = [
#     (human_judges, "Human Judges"),
#     (ai_judges, "AI Judges")
# ]

# visualize_judges(judge_sets, plot_type='PCA')
# visualize_judges(judge_sets, plot_type='UMAP')
# visualize_judges(judge_sets, plot_type='TSNE')

def similarity_heatmap(judge_vectors, judge_labels, metric='cosine', method='average', figsize=(12, 10)):
    """
    Create a similarity heatmap for judgment vectors with clustering.
    
    :param judge_vectors: 2D array where each row is a judge's vector
    :param judge_labels: List of labels for each judge
    :param metric: Distance metric for similarity (default: 'cosine')
    :param method: Linkage method for hierarchical clustering (default: 'average')
    :param figsize: Figure size (width, height) in inches
    """
    # Compute pairwise distances
    distances = pdist(judge_vectors, metric=metric)
    similarity_matrix = 1 - squareform(distances)  # Convert distances to similarities
    
    # Perform hierarchical clustering
    linkage = hierarchy.linkage(distances, method=method)
    
    # Create a clustered heatmap
    plt.figure(figsize=figsize)
    sns.set(font_scale=0.8)
    
    # Generate a custom diverging colormap
    cmap = sns.diverging_palette(h_neg=220, h_pos=10, as_cmap=True)
    
    # Create the heatmap
    g = sns.clustermap(similarity_matrix,
                       row_linkage=linkage,
                       col_linkage=linkage,
                       cmap=cmap,
                       center=0,
                       annot=True,
                       fmt='.2f',
                       xticklabels=judge_labels,
                       yticklabels=judge_labels,
                       figsize=figsize)
    
    # Rotate x-axis labels
    plt.setp(g.ax_heatmap.get_xticklabels(), rotation=45, ha='right')
    
    plt.title("Judge Similarity Heatmap", pad=50)
    plt.tight_layout()
    plt.show()

# # Example usage
# M, N = 3, 4  # 3 trials, 4 hypotheses per trial
# np.random.seed(42)

# # Generate random ranking vectors for demonstration
# num_judges = 15
# judge_vectors = np.random.randint(-1, 2, size=(num_judges, M * (N * (N - 1) // 2)))

# # Create labels for judges
# judge_labels = [f'Human_{i+1}' if i < 10 else f'AI_{i-9}' for i in range(num_judges)]

# # Generate the heatmap
# similarity_heatmap(judge_vectors, judge_labels)