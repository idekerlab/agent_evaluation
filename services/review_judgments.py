from models.review import Review
from models.review_set import ReviewSet
from itertools import combinations
import json
import numpy as np

def create_judgment_vector_for_review(review):
    """
    Create a judgment vector for a single Review.

    :param review: Review object
    :return: NumPy array representing the judgment vector
    :raises ValueError: If the ranking data is invalid
    """
    if not isinstance(review, Review):
        raise TypeError("Input must be a Review object")

    if not review.ranking_data:
        raise ValueError("Review does not contain ranking data")

    try:
        ranking_data = json.loads(review.ranking_data)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON in ranking_data")

    if not ranking_data.get("ranking"):
        raise ValueError("Ranking data is empty or invalid")

    N = len(ranking_data["ranking"])

    hypothesis_rankings = np.zeros(N, dtype=int)
    for hypothesis_id, ranking in ranking_data["ranking"].items():
        order = int(ranking["order"])
        stars = int(ranking["stars"])
        if order < 1 or order > N:
            raise ValueError(f"Invalid order {order} for hypothesis {hypothesis_id}")
        hypothesis_rankings[order - 1] = stars

    review_judgment_vector_length = (N * (N - 1) // 2)
    review_judgment_vector = np.zeros(review_judgment_vector_length, dtype=np.int8)

    idx = 0
    for i, j in combinations(range(N), 2):
        if hypothesis_rankings[i] < hypothesis_rankings[j]:
            review_judgment_vector[idx] = -1
        elif hypothesis_rankings[i] > hypothesis_rankings[j]:
            review_judgment_vector[idx] = 1
        idx += 1

    return review_judgment_vector

def create_judgment_vector_for_review_list(reviews):
    """
    Create a judgment vector based on an ordered list of Reviews.

    :param reviews: List of Review objects
    :return: NumPy array representing the combined judgment vector
    :raises ValueError: If the reviews are not from the same reviewer
    :raises TypeError: If any item in the list is not a Review object
    """
    if not reviews:
        raise ValueError("Empty list of reviews")

    if not all(isinstance(review, Review) for review in reviews):
        raise TypeError("All items in the list must be Review objects")

    # Check if all reviews are from the same reviewer
    reviewer_id = reviews[0].agent_id
    if not all(review.agent_id == reviewer_id for review in reviews):
        raise ValueError("All reviews must be from the same reviewer")

    # Create judgment vectors for each review
    judgment_vectors = [create_judgment_vector_for_review(review) for review in reviews]

    # Concatenate all judgment vectors
    return np.concatenate(judgment_vectors)

def create_reviewer_judgment_dict_for_review_set(db, review_set_id):
    """
    Create a dictionary of Reviewer IDs to judgment vectors for a ReviewSet.

    :param db: Database connection
    :param review_set: ReviewSet object
    :return: Dict of Reviewer IDs to judgment vectors
    :raises ValueError: If any review in the set is invalid
    """
    review_set = ReviewSet.load(db, review_set_id)
    if not review_set:
            raise ValueError(f"Failed to load review_set with ID {review_set_id}")
    if not hasattr(review_set, 'review_ids'):
        raise AttributeError("ReviewSet object must have a 'review_ids' attribute")

    reviewer_judgment_dict = {}
    for review_id in review_set.review_ids:
        review = Review.load(db, review_id)
        if not review:
            raise ValueError(f"Failed to load review with ID {review_id}")
        reviewer_judgment_dict[review.agent_id] = create_judgment_vector_for_review(review)
    return reviewer_judgment_dict

def create_reviewer_judgment_dict_for_review_set_list(db, review_sets):
    """
    Create a dictionary of Reviewer IDs to judgment vectors for a list of ReviewSets.

    :param db: Database connection
    :param review_sets: List of ReviewSet objects
    :return: Dict of Reviewer IDs to combined judgment vectors
    :raises ValueError: If any review set is invalid or if the review sets have different reviewers
    """
    if not review_sets:
        raise ValueError("Empty list of review sets")

    reviewer_judgment_dict = {}
    first_set_reviewers = set()

    for i, review_set in enumerate(review_sets):
        review_set_dict = create_reviewer_judgment_dict_for_review_set(db, review_set)
        
        if i == 0:
            first_set_reviewers = set(review_set_dict.keys())
        elif set(review_set_dict.keys()) != first_set_reviewers:
            raise ValueError(f"Review set {i} has different reviewers than the first set")

        for reviewer_id, judgment_vector in review_set_dict.items():
            if reviewer_id not in reviewer_judgment_dict:
                reviewer_judgment_dict[reviewer_id] = []
            reviewer_judgment_dict[reviewer_id].append(judgment_vector)
    
    # Combine judgment vectors for each reviewer
    for reviewer_id in reviewer_judgment_dict:
        reviewer_judgment_dict[reviewer_id] = np.concatenate(reviewer_judgment_dict[reviewer_id])
    
    return reviewer_judgment_dict

# Helper function
def get_review(db, review_set, reviewer_id):
    """
    Get a specific Review from a ReviewSet based on the reviewer_id.

    :param db: Database connection
    :param review_set: ReviewSet object
    :param reviewer_id: ID of the reviewer
    :return: Review object
    :raises ValueError: If the reviewer is not found in the ReviewSet
    """
    if not hasattr(review_set, 'review_ids'):
        raise AttributeError("ReviewSet object must have a 'review_ids' attribute")

    reviewer_ids = []
    for review_id in review_set.review_ids:
        review = Review.load(db, review_id)
        if not review:
            raise ValueError(f"Failed to load review with ID {review_id}")
        reviewer_ids.append(review.agent_id)
        if review.agent_id == reviewer_id:
            return review
    raise ValueError(f"Reviewer {reviewer_id} not in ReviewSet reviewer_ids \n{json.dumps(reviewer_ids)}")