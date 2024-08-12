import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.cluster import hierarchy
from scipy.spatial.distance import pdist, squareform
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import umap
from typing import Dict, Tuple
from itertools import combinations
from models.review import Review
import json

# {
#   "user_id": "user_15579855-9160-4aac-97d4-361ecdfdd4a8",
#   "status": "pending",
#   "rankings": {
#     "hypothesis_id7r3297": {
#       "stars": 3,
#       "comments": "",
#       "order": 1
#     },
#     "hypothesis_id7r3297": {
#       "stars": 3,
#       "comments": "",
#       "order": 3
#     },
#     "hypothesis_id7r3297": {
#       "stars": 5,
#       "comments": "",
#       "order": 4
#     },
#     "hypothesis_id7r3297": {
#       "stars": 1,
#       "comments": "",
#       "order": 2
#     }
#   }
# }

def get_review(db, review_set, reviewer_id):
    for review_id in review_set.review_ids:
        review = Review.load(db, review_id)
        if review.agent_id == reviewer_id:
            return review
    raise ValueError("Reviewer not in ReviewSet")

def create_review_judgment_vector(db, review_set=None, reviewer_id=None):
    """
    Create a judgment vector for the Review 
    belonging to the Reviewer in the ReviewSet

    Each ReviewSet is the result of one or more Reviewers judging
    (assigning a partial ranking) the Hypothesis objects in an AnalysisRun, 
    as specified in the corresponding ReviewPlan

    Each Review in the ReviewSet contains a partial ranking for each Hypothesis
    in the Review. TODO: format example. There is one Review per Reviewer.
    
    The Hypotheses in the Review are identified according to their order in the 
    AnalysisRun, which is in turn specified by their order in the AnalysisPlan

    The vector is in N dimensions in the judgment space where
    N is the number of unique hypothesis vs. hypothesis comparisons.

    Each comparison is represented as 1 | 0 | -1 based on: 
        A > B -> 1  (prefer A)
        A = B -> 0  (no preference)
        A < B -> -1 (prefer B)
    
    :param review_set: ReviewSet object
    :return: NumPy array representing the judgment vector
    """
    review = get_review(db, review_set, reviewer_id)

    ranking_data = json.loads(review.ranking_data)

    N = len(ranking_data["rankings"])  # Number of Hypothesis objects in the ReviewSet

    rankings = np.zeros(N, dtype=int) 
    for hypothesis_id, ranking in ranking_data["rankings"].items():
        order = int(ranking["order"])
        stars = int(ranking["stars"])
        rankings[order - 1] = stars
    
    # Create a vector long enough to hold the unique A-B comparisons,
    # not including self comparisons
    review_judgment_vector_length = (N * (N - 1) // 2)
    review_judgment_vector = np.zeros(review_judgment_vector_length, dtype=np.int8)
    
    idx = 0
    for i, j in combinations(range(N), 2):
        if rankings[i] < rankings[j]:
            review_judgment_vector[idx] = -1
        elif rankings[i] > rankings[j]:
            review_judgment_vector[idx] = 1
        # If the hypotheses are tied, the value remains 0
        idx += 1
    
    return review_judgment_vector

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

def create_judgment_vector(db, review_sets=None, reviewer_id=None):
    # For a each ReviewSet, create a judgment
    # vector for the specified Reviewer
    #
    # Each judgement_vector represents coordinates
    # in a separate set of dimensions in the
    # judgment space. 
    #
    # We can therefore create a merged vector
    # by simple concatenation.
    #
    # NOTE
    # The judgment vectors for the reviewers are
    # comparable ONLY if the ReviewSets 
    # have exactly the same Reviewers. Otherwise,
    # the vectors will be of different lengths
    # for different reviewers and the A-B
    # comparisons will not align.
    judgment_vector_list = []
    review_jvecs = {}
    for review_set in review_sets:
        review_jvec = create_review_judgment_vector(db, review_set=review_set, reviewer_id=reviewer_id)
        judgment_vector_list.append(review_jvec)
        review_jvecs[reviewer_id] = review_jvec
    return np.concatenate(judgment_vector_list), review_jvecs

def visualize_judgment_vectors(reviewer_data: Dict[str, Dict], 
                               plot_type: str = 'PCA', 
                               n_components: int = 2,
                               random_state: int = 42,
                               figsize: Tuple[int, int] = (10, 8)):
    """
    Visualize multiple reviewers in judgment space.
    
    :param reviewer_data: Dictionary of reviewer data
    :param plot_type: Type of plot ('PCA', 'UMAP', or 'TSNE')
    :param n_components: Number of components for dimensionality reduction
    :param random_state: Random state for reproducibility
    :param figsize: Figure size
    """
    # Extract judgment vectors and labels
    judgment_vectors = []
    labels = []
    n = 1
    for reviewer_id, data in reviewer_data.items():
        judgment_vectors.append(data['judgment_vector'])
        if "label" in data and data['label'] is not None:
            labels.append(data['label'])
        else:
            labels.append(f'label#{str(n)}')
            n += 1

    # Convert to numpy array
    all_reviewers = np.vstack(judgment_vectors)

    # Determine the number of components
    n_samples, n_features = all_reviewers.shape
    n_components = min(n_components, n_samples, n_features)
    
    # Perform dimensionality reduction
    if plot_type == 'PCA':
        reducer = PCA(n_components=n_components, random_state=random_state)
    elif plot_type == 'UMAP':
        reducer = umap.UMAP(n_components=n_components, random_state=random_state)
    elif plot_type == 'TSNE':
        reducer = TSNE(n_components=n_components, random_state=random_state)
    else:
        raise ValueError("Invalid plot_type. Choose 'PCA', 'UMAP', or 'TSNE'.")
    
    try:
        reduced_data = reducer.fit_transform(all_reviewers)
    except ValueError as e:
        print(f"Error in dimensionality reduction: {e}")
        print(f"Number of reviewers: {n_samples}, Number of features: {n_features}")
        return
    
    # Plotting
    plt.figure(figsize=figsize)
    colors = plt.cm.rainbow(np.linspace(0, 1, len(set(labels))))
    color_dict = {label: color for label, color in zip(set(labels), colors)}
    markers = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', 'h', 'H', '+', 'x', 'd', '|', '_']
    marker_dict = {label: marker for label, marker in zip(set(labels), markers)}
    
    for i, (x, y) in enumerate(reduced_data):
        label = labels[i]
        plt.scatter(x, y, 
                    c=[color_dict[label]], 
                    marker=marker_dict[label], 
                    label=label if label not in plt.gca().get_legend_handles_labels()[1] else "",
                    alpha=0.7)
    
    plt.title(f"Reviewers in {plot_type} Space")
    plt.xlabel(f"{plot_type}1")
    plt.ylabel(f"{plot_type}2")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()



def reviewer_similarity_heatmap(reviewer_judgment_vectors, metric='cosine', method='average', figsize=(12, 10)):
    """
    Create a similarity heatmap for judgment vectors with clustering.
    
    :param reviewer_judgment_vectors: dict where the keys are reviewer ids and the values are numpy vectors
    :param judge_labels: List of labels for each reviewer
    :param metric: Distance metric for similarity (default: 'cosine')
    :param method: Linkage method for hierarchical clustering (default: 'average')
    :param figsize: Figure size (width, height) in inches
    """

    # 2D array where each row is a reviewer's vector
    judgment_vectors = []
    # List of reviewer labels
    reviewer_labels = []

    for reviewer, judgement_vector in reviewer_judgment_vectors:
        judgment_vectors.append(judgement_vector)
        reviewer_labels.append(reviewer.name)

    # Compute pairwise distances
    distances = pdist(judgment_vectors, metric=metric)
    similarity_matrix = 1 - squareform(distances)  # Convert distances to similarities
    
    # Perform hierarchical clustering
    linkage = hierarchy.linkage(distances, method=method)
    
    # Create a clustered heatmap
    plt.figure(figsize=figsize)
    sns.set_theme(font_scale=0.8)
    
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
                       xticklabels=reviewer_labels,
                       yticklabels=reviewer_labels,
                       figsize=figsize)
    
    # Rotate x-axis labels
    plt.setp(g.ax_heatmap.get_xticklabels(), rotation=45, ha='right')
    
    plt.title("Reviewer Similarity Heatmap", pad=50)
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