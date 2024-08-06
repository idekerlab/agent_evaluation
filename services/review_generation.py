from models.dataset import Dataset
from models.agent import Agent
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
        return ""
    
def extract_final_rankings(long_string):
    # Extract the Final Rankings section
    pattern = r'Final Rankings:(.*?)(?=\n\nSummary Review:)'
    match = re.search(pattern, long_string, re.DOTALL)
    
    if not match:
        return None
    
    rankings_text = match.group(1).strip()
    print("Extracted rankings text:", rankings_text)  # Debugging print
    
    # Parse the rankings into tuples
    ranking_pattern = r'Hypothesis#(\d+):\s*(\d+)'
    rankings = re.findall(ranking_pattern, rankings_text)
    print("Parsed rankings:", rankings)  # Debugging print
    
    # Convert strings to integers and sort by hypothesis number
    rankings = [(int(hyp), int(rank)) for hyp, rank in rankings]
    rankings.sort(key=lambda x: x[0])
    
    return rankings
        
class ReviewGenerator:
    def __init__(self, db):
        self.db = db

    def generate_review(self, agent_id, dataset_id, hypotheses_text, analysis_run_id, review_set_id):
        # Load the dataset and agent using the newly created classes
        dataset = Dataset.load(self.db, dataset_id)
        agent = Agent.load(self.db, agent_id)
        if not dataset or not agent:
            raise ValueError("Dataset or Agent not found in generate_hypothesis")
        
        if review_set_id:
            # Load the ReviewSet using the newly created class
            review_set = ReviewSet.load(self.db, review_set_id)
            if not review_set:
                raise ValueError("ReviewSet to which to add the hypothesis was provided but not found in generate_hypothesis")

        # Use properties directly from the loaded objects
        data = dataset.data

        # check the number of hypotheses loaded 
        analysis_run = AnalysisRun.load(self.db, analysis_run_id)
        n_hypotheses = len(analysis_run.hypothesis_ids)
        if n_hypotheses == 0:
            raise ValueError("No hypotheses found in AnalysisRun")

        safe_dict = SafeDict({
            'n': n_hypotheses, 
            'data': data,
            'experiment_description': dataset.experiment_description,
            'hypotheses_text': hypotheses_text
        })
        
        prompt = agent.prompt_template.format_map(safe_dict)

        # Load the LLM associated with the agent
        llm = LLM.load(self.db, agent.llm_id)
        if not llm:
            raise ValueError("LLM not found")

        # Generate hypothesis text using the LLM
        review_text = llm.query(agent.context, prompt)
        summary_review = extract_summary_review(review_text)
        ranking_tuples = extract_final_rankings(review_text)
        ranking_data = ""

        if ranking_tuples is not None:
            # Combine the tuples with the agent_id and the hypothesis_ids in the AnalysisRun 
            # to generate the rankings datastructure
            rankings = {"user_id": agent_id, "status": "done"}
            analysis_run = AnalysisRun.load(self.db, analysis_run_id)
            r = {}
            for order, rank in ranking_tuples:
                hypothesis_id = analysis_run.hypothesis_ids[order - 1]
                r[hypothesis_id] = {"stars": rank, "order": order, "comments": ""}

            rankings["rankings"]=r
            ranking_data = json.dumps(rankings)

        # Create and save the hypothesis
        review = Review.create(
            self.db,
            data=data,
            hypotheses_text=hypotheses_text,
            review_text=review_text,
            ranking_data=ranking_data,
            summary_review=summary_review,
            agent_id=agent_id,
            analysis_run_id=analysis_run_id,
            description=None, # Not sure why this is here
            review_set_id=review_set_id     
        )

        return review.object_id

# Example usage:
# generator = ReviewGenerator(db)
# hypothesis_id = generator.generate_hypothesis(agent_id, dataset_id)
