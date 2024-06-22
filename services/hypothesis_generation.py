from models.dataset import Dataset
from models.analyst import Analyst
from models.llm import LLM
from models.hypothesis import Hypothesis
from models.analysis_run import AnalysisRun
from helpers.safe_dict import SafeDict

class HypothesisGenerator:
    def __init__(self, db):
        self.db = db

    def generate_hypothesis(self, analyst_id, analysis_run_id, n_hypotheses_per_analyst, description=""):
        # Load the dataset and analyst using the newly created classes
        analysis_run = AnalysisRun.load(self.db, analysis_run_id)
        if not analysis_run:
            raise ValueError("AnalysisRun to which to add the hypothesis was provided but not found in generate_hypothesis")
        
        dataset = Dataset.load(self.db, analysis_run.dataset_id)
        analyst = Analyst.load(self.db, analyst_id)
        if not dataset or not analyst:
            raise ValueError("Dataset or Analyst not found in generate_hypothesis")
       
        separation_symbol = "&&&&&"

        # Use properties directly from the loaded objects
        data = dataset.data
        safe_dict = SafeDict({
            'data': data,
            'experiment_description': dataset.experiment_description,
            'biological_context': analysis_run.biological_context
        })
        
        prompt = analyst.prompt_template.format_map(safe_dict)
        
        if (n_hypotheses_per_analyst > 1):
            prompt += f"\n\n Generate {n_hypotheses_per_analyst} hypotheses. Separate the text between each hypothesis with the following symbols: {separation_symbol}"

        # Load the LLM associated with the analyst
        llm = LLM.load(self.db, analyst.llm_id)
        if not llm:
            raise ValueError("LLM not found")

        # Generate hypothesis text using the LLM
        hypothesis_text = llm.query(analyst.context, prompt)
        
        if (n_hypotheses_per_analyst > 1):
            ids = []
            hypothesis_arr = hypothesis_text.split(separation_symbol)
            for hypothesis_text in hypothesis_arr:
                if len(hypothesis_text) > 5:
                    # Create and save the hypothesis
                    hypothesis = Hypothesis.create(
                        self.db,
                        data=data,
                        hypothesis_text=hypothesis_text.strip(),
                        analyst_id=analyst_id,
                        dataset_id=dataset.object_id,
                        description=description, 
                        analysis_run_id=analysis_run_id
                    )
                    ids.append(hypothesis.object_id)
            return ids
        
        else:

            # Create and save the hypothesis
            hypothesis = Hypothesis.create(
                self.db,
                data=data,
                hypothesis_text=hypothesis_text,
                analyst_id=analyst_id,
                dataset_id=dataset.object_id,
                description=description, 
                analysis_run_id=analysis_run_id
            )

            return [hypothesis.object_id]

# Example usage:
# generator = HypothesisGenerator(db)
# hypothesis_id = generator.generate_hypothesis(analyst_id, dataset_id)
