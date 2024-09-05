import unittest
import sys
import os
import json
import numpy as np

# Add the parent directory of the current script to the Python path
cwd = os.getcwd()
dirname = os.path.dirname(cwd)
print(f'adding current directory to path: {cwd}')
sys.path.append(cwd)
print(f'adding parent to path: {dirname}')
sys.path.append(dirname)
print(f'Python path: {sys.path}')
print(sys.path)

from models.review import Review
from models.review_set import ReviewSet
from app.sqlite_database import SqliteDatabase
from app.config import load_database_config
from services.review_judgments import (
    create_judgment_vector_for_review,
    create_judgment_vector_for_review_list,
    create_reviewer_judgment_dict_for_review_set,
    create_reviewer_judgment_dict_for_review_set_list,
    get_review
)

class TestReviewJudgmentsIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db_type, uri, user, password = load_database_config(path='~/ae_config/test_config.ini')
        cls.db = SqliteDatabase(uri)

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def create_test_review(self, agent_id, ranking_data):
        return Review.create(
            self.db,
            data={},
            hypotheses_text="Test hypotheses",
            review_text="Test review",
            ranking_data=json.dumps(ranking_data),
            summary_review="Test summary",
            agent_id=agent_id,
            analysis_run_id="test_run",
            description="Test description",
            review_set_id="test_set",
            name="Test Review"
        )

    def create_test_review_set(self, review_ids):
        return ReviewSet.create(
            self.db,
            review_plan_id="test_plan",
            agent_ids=["reviewer1", "reviewer2"],
            analysis_run_id="test_run",
            description="Test ReviewSet",
            name="Test ReviewSet"
        )

    def test_review_judgments_integration(self):
        # Create test reviews
        ranking_data1 = {"ranking": {"1": {"order": 1, "stars": 3}, "2": {"order": 2, "stars": 2}, "3": {"order": 3, "stars": 1}}}
        ranking_data2 = {"ranking": {"1": {"order": 1, "stars": 2}, "2": {"order": 2, "stars": 3}, "3": {"order": 3, "stars": 1}}}
        
        review1 = self.create_test_review("reviewer1", ranking_data1)
        review2 = self.create_test_review("reviewer2", ranking_data2)
        review3 = self.create_test_review("reviewer1", ranking_data2)
        review4 = self.create_test_review("reviewer2", ranking_data1)

        # Test create_judgment_vector_for_review
        judgment_vector1 = create_judgment_vector_for_review(review1)
        self.assertEqual(judgment_vector1.tolist(), [1, 1, 1])

        # Test create_judgment_vector_for_review_list
        judgment_vector_list = create_judgment_vector_for_review_list([review1, review3])
        self.assertEqual(judgment_vector_list.tolist(), [1, 1, 1, -1, 1, 1])

        # Create actual ReviewSet objects
        review_set1 = self.create_test_review_set([review1.object_id, review2.object_id])
        review_set1.add_review(review1.object_id, "reviewer1")
        review_set1.add_review(review2.object_id, "reviewer2")

        review_set2 = self.create_test_review_set([review3.object_id, review4.object_id])
        review_set2.add_review(review3.object_id, "reviewer1")
        review_set2.add_review(review4.object_id, "reviewer2")

        # Test create_reviewer_judgment_dict_for_review_set
        reviewer_dict = create_reviewer_judgment_dict_for_review_set(self.db, review_set1)
        self.assertEqual(set(reviewer_dict.keys()), {"reviewer1", "reviewer2"})
        np.testing.assert_array_equal(reviewer_dict["reviewer1"], np.array([1, 1, 1]))
        np.testing.assert_array_equal(reviewer_dict["reviewer2"], np.array([-1, 1, 1]))

        # Test create_reviewer_judgment_dict_for_review_set_list
        reviewer_dict_list = create_reviewer_judgment_dict_for_review_set_list(self.db, [review_set1, review_set2])
        self.assertEqual(set(reviewer_dict_list.keys()), {"reviewer1", "reviewer2"})
        np.testing.assert_array_equal(reviewer_dict_list["reviewer1"], np.array([1, 1, 1, -1, 1, 1]))
        np.testing.assert_array_equal(reviewer_dict_list["reviewer2"], np.array([-1, 1, 1, 1, 1, 1]))

        # Test get_review
        retrieved_review = get_review(self.db, review_set1, "reviewer1")
        self.assertEqual(retrieved_review.object_id, review1.object_id)

        # Clean up
        review1.delete()
        review2.delete()
        review3.delete()
        review4.delete()
        review_set1.delete()
        review_set2.delete()

if __name__ == '__main__':
    unittest.main()
    
    #-----
# 
# import unittest
# import sys
# import os
# import json
# import numpy as np

# # Add the parent directory of the current script to the Python path
# cwd = os.getcwd()
# dirname = os.path.dirname(cwd)
# print(f'adding current directory to path: {cwd}')
# sys.path.append(cwd)
# print(f'adding parent to path: {dirname}')
# sys.path.append(dirname)
# print(f'Python path: {sys.path}')
# print(sys.path)

# from models.review import Review
# from models.review_set import ReviewSet 
# from app.sqlite_database import SqliteDatabase
# from app.config import load_database_config
# from services.review_judgments import (
#     create_judgment_vector_for_review,
#     create_judgment_vector_for_review_list,
#     create_reviewer_judgment_dict_for_review_set,
#     create_reviewer_judgment_dict_for_review_set_list,
#     get_review
# )

# class TestReviewJudgmentsIntegration(unittest.TestCase):
#     @classmethod
#     def setUpClass(cls):
#         # Establish a connection to the database
#         db_type, uri, user, password = load_database_config(path='~/ae_config/test_config.ini')
#         cls.db = SqliteDatabase(uri)

#     @classmethod
#     def tearDownClass(cls):
#         # Close the database connection
#         cls.db.close()

#     def create_test_review(self, agent_id, ranking_data):
#         return Review.create(
#             self.db,
#             data={},
#             hypotheses_text="Test hypotheses",
#             review_text="Test review",
#             ranking_data=json.dumps(ranking_data),
#             summary_review="Test summary",
#             agent_id=agent_id,
#             analysis_run_id="test_run",
#             description="Test description",
#             review_set_id="test_set",
#             name="Test Review"
#         )

#     def create_test_review_set(self, review_ids):
#         return ReviewSet.create(
#             self.db,
#             review_plan_id="test_plan",
#             agent_ids=["reviewer1", "reviewer2"],
#             analysis_run_id="test_run",
#             description="Test ReviewSet",
#             name="Test ReviewSet"
#         )

#     def test_review_judgments_integration(self):
#         # Create test reviews
#         ranking_data1 = {"ranking": {"1": {"order": 1, "stars": 3}, "2": {"order": 2, "stars": 2}, "3": {"order": 3, "stars": 1}}}
#         ranking_data2 = {"ranking": {"1": {"order": 1, "stars": 2}, "2": {"order": 2, "stars": 3}, "3": {"order": 3, "stars": 1}}}
        
#         review1 = self.create_test_review("reviewer1", ranking_data1)
#         review2 = self.create_test_review("reviewer1", ranking_data2)
#         review3 = self.create_test_review("reviewer2", ranking_data1)

#         # Test create_judgment_vector_for_review
#         judgment_vector1 = create_judgment_vector_for_review(review1)
#         self.assertEqual(judgment_vector1.tolist(), [1, 1, 1])

#         # Test create_judgment_vector_for_review_list
#         judgment_vector_list = create_judgment_vector_for_review_list([review1, review2])
#         self.assertEqual(judgment_vector_list.tolist(), [1, 1, 1, -1, 1, 1])

#         # Create actual ReviewSet objects
#         review_set1 = self.create_test_review_set([review1.object_id, review3.object_id])
#         review_set1.add_review(review1.object_id, "reviewer1")
#         review_set1.add_review(review3.object_id, "reviewer2")

#         review_set2 = self.create_test_review_set([review2.object_id])
#         review_set2.add_review(review2.object_id, "reviewer1")

#         # Test create_reviewer_judgment_dict_for_review_set
#         reviewer_dict = create_reviewer_judgment_dict_for_review_set(self.db, review_set1)
#         self.assertEqual(set(reviewer_dict.keys()), {"reviewer1", "reviewer2"})
#         np.testing.assert_array_equal(reviewer_dict["reviewer1"], np.array([1, 1, 1]))
#         np.testing.assert_array_equal(reviewer_dict["reviewer2"], np.array([1, 1, 1]))

#         # Test create_reviewer_judgment_dict_for_review_set_list
#         reviewer_dict_list = create_reviewer_judgment_dict_for_review_set_list(self.db, [review_set1, review_set2])
#         self.assertEqual(set(reviewer_dict_list.keys()), {"reviewer1", "reviewer2"})
#         np.testing.assert_array_equal(reviewer_dict_list["reviewer1"], np.array([1, 1, 1, -1, 1, 1]))
#         np.testing.assert_array_equal(reviewer_dict_list["reviewer2"], np.array([1, 1, 1]))

#         # Test get_review
#         retrieved_review = get_review(self.db, review_set1, "reviewer1")
#         self.assertEqual(retrieved_review.object_id, review1.object_id)

#         # Clean up
#         review1.delete()
#         review2.delete()
#         review3.delete()
#         review_set1.delete()
#         review_set2.delete()

# class TestReviewJudgmentsIntegration(unittest.TestCase):
#     @classmethod
#     def setUpClass(cls):
#         # Establish a connection to the database
#         db_type, uri, user, password = load_database_config(path='~/ae_config/test_config.ini')
#         cls.db = SqliteDatabase(uri)

#     @classmethod
#     def tearDownClass(cls):
#         # Close the database connection
#         cls.db.close()

#     def create_test_review(self, agent_id, ranking_data):
#         return Review.create(
#             self.db,
#             data={},
#             hypotheses_text="Test hypotheses",
#             review_text="Test review",
#             ranking_data=json.dumps(ranking_data),
#             summary_review="Test summary",
#             agent_id=agent_id,
#             analysis_run_id="test_run",
#             description="Test description",
#             review_set_id="test_set",
#             name="Test Review"
#         )

#     def test_review_judgments_integration(self):
#         # Create test reviews
#         ranking_data1 = {"ranking": {"1": {"order": 1, "stars": 3}, "2": {"order": 2, "stars": 2}, "3": {"order": 3, "stars": 1}}}
#         ranking_data2 = {"ranking": {"1": {"order": 1, "stars": 2}, "2": {"order": 2, "stars": 3}, "3": {"order": 3, "stars": 1}}}
        
#         review1 = self.create_test_review("reviewer1", ranking_data1)
#         review2 = self.create_test_review("reviewer1", ranking_data2)
#         review3 = self.create_test_review("reviewer2", ranking_data1)

#         # Test create_judgment_vector_for_review
#         judgment_vector1 = create_judgment_vector_for_review(review1)
#         self.assertEqual(judgment_vector1.tolist(), [1, 1, 1])

#         # Test create_judgment_vector_for_review_list
#         judgment_vector_list = create_judgment_vector_for_review_list([review1, review2])
#         self.assertEqual(judgment_vector_list.tolist(), [1, 1, 1, -1, 1, 1])

#         # Create a mock ReviewSet
#         class MockReviewSet:
#             def __init__(self, review_ids):
#                 self.review_ids = review_ids

#         review_set = MockReviewSet([review1.object_id, review3.object_id])

#         # Test create_reviewer_judgment_dict_for_review_set
#         reviewer_dict = create_reviewer_judgment_dict_for_review_set(self.db, review_set)
#         self.assertEqual(set(reviewer_dict.keys()), {"reviewer1", "reviewer2"})
#         np.testing.assert_array_equal(reviewer_dict["reviewer1"], np.array([1, 1, 1]))
#         np.testing.assert_array_equal(reviewer_dict["reviewer2"], np.array([1, 1, 1]))

#         # Test create_reviewer_judgment_dict_for_review_set_list
#         review_set2 = MockReviewSet([review2.object_id])
#         reviewer_dict_list = create_reviewer_judgment_dict_for_review_set_list(self.db, [review_set, review_set2])
#         self.assertEqual(set(reviewer_dict_list.keys()), {"reviewer1", "reviewer2"})
#         np.testing.assert_array_equal(reviewer_dict_list["reviewer1"], np.array([1, 1, 1, -1, 1, 1]))
#         np.testing.assert_array_equal(reviewer_dict_list["reviewer2"], np.array([1, 1, 1]))

#         # Test get_review
#         retrieved_review = get_review(self.db, review_set, "reviewer1")
#         self.assertEqual(retrieved_review.object_id, review1.object_id)

#         # Clean up
#         review1.delete()
#         review2.delete()
#         review3.delete()

if __name__ == '__main__':
    unittest.main()