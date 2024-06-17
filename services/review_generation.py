from models.dataset import Dataset
from models.analyst import Analyst
from models.llm import LLM
from models.review import Review
from models.review_set import ReviewSet
from helpers.safe_dict import SafeDict

class ReviewGenerator:
    def __init__(self, db):
        self.db = db

    def generate_review(self, analyst_id, dataset_id, hypotheses_text, analysis_run_id, review_set_id):
        # Load the dataset and analyst using the newly created classes
        dataset = Dataset.load(self.db, dataset_id)
        analyst = Analyst.load(self.db, analyst_id)
        if not dataset or not analyst:
            raise ValueError("Dataset or Analyst not found in generate_hypothesis")
        
        if review_set_id:
            # Load the ReviewSet using the newly created class
            review_set = ReviewSet.load(self.db, review_set_id)
            if not review_set:
                raise ValueError("ReviewSet to which to add the hypothesis was provided but not found in generate_hypothesis")

        # Use properties directly from the loaded objects
        data = dataset.data
        safe_dict = SafeDict({
            'data': data,
            'experiment_description': dataset.experiment_description,
            'hypotheses_text': hypotheses_text
        })
        
        prompt = analyst.prompt_template.format_map(safe_dict)

        # Load the LLM associated with the analyst
        llm = LLM.load(self.db, analyst.llm_id)
        if not llm:
            raise ValueError("LLM not found")

        # Generate hypothesis text using the LLM
        review_text = llm.query(analyst.context, prompt)

        # Create and save the hypothesis
        review = Review.create(
            self.db,
            data=data,
            hypotheses_text=hypotheses_text,
            review_text=review_text,
            analyst_id=analyst_id,
            analysis_run_id=analysis_run_id,
            description=None, # Not sure why this is here
            review_set_id=review_set_id     
        )

        return review.object_id

# Example usage:
# generator = ReviewGenerator(db)
# hypothesis_id = generator.generate_hypothesis(analyst_id, dataset_id)
