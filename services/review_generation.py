from models.dataset import Dataset
from models.analyst import Analyst
from models.analysis_run import AnalysisRun
from models.llm import LLM
from models.review import Review
from models.review_set import ReviewSet
from helpers.safe_dict import SafeDict
import re
import json

def extract_summary_review(long_string):
    pattern = r'\nSummary Review:(.*)'
    match = re.search(pattern, long_string, re.DOTALL)
    if match:
        return match.group(1).strip()
    else:
        return "Summary Review section not found."
    
def extract_final_rankings(long_string):
    # First, extract the Final Rankings section
    pattern = r'Final Rankings:(.*?)(?=\n\S|\Z)'
    match = re.search(pattern, long_string, re.DOTALL)
    
    if not match:
        return "Final Rankings section not found."
    
    rankings_text = match.group(1).strip()
    
    # Now, parse the rankings into tuples
    ranking_pattern = r'Hypothesis#(\d+):\s*(\d+)'
    rankings = re.findall(ranking_pattern, rankings_text)
    
    # Convert strings to integers and sort by hypothesis number
    rankings = [(int(hyp), int(rank)) for hyp, rank in rankings]
    rankings.sort(key=lambda x: x[0])
    
    return rankings
        
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
        summary_review = extract_summary_review(review_text)
        ranking_tuples = extract_final_rankings(review_text)

        # Combine the tuples with the analyst_id and the hypothesis_ids in the AnalysisRun 
        # to generate the rankings datastructure
        rankings = {"user_id": analyst_id, "status": "done"}
        analysis_run = AnalysisRun.load(self.db, analysis_run_id)
        r = {}
        for order, rank in ranking_tuples:
            hypothesis_id = analysis_run.hypothesis_ids[order-1]
            r[hypothesis_id] = {"stars": rank, "order": order, "comments": ""}

        rankings["rankings"]=r

        # Create and save the hypothesis
        review = Review.create(
            self.db,
            data=data,
            hypotheses_text=hypotheses_text,
            rankings=json.dumps(rankings),
            summary_review=summary_review,
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
