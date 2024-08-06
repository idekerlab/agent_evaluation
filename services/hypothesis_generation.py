from models.dataset import Dataset
from models.agent import Agent
from models.llm import LLM
from models.hypothesis import Hypothesis
from models.analysis_run import AnalysisRun
from helpers.safe_dict import SafeDict

class HypothesisGenerator:
    def __init__(self, db):
        self.db = db

    def generate_hypothesis(self, agent_id, analysis_run_id, n_hypotheses_per_agent, description=""):
        # Load the dataset and agent using the newly created classes
        analysis_run = AnalysisRun.load(self.db, analysis_run_id)
        if not analysis_run:
            raise ValueError("AnalysisRun to which to add the hypothesis was provided but not found in generate_hypothesis")
        
        dataset = Dataset.load(self.db, analysis_run.dataset_id)
        agent = Agent.load(self.db, agent_id)
        if not dataset or not agent:
            raise ValueError("Dataset or Agent not found in generate_hypothesis")
       
        separation_symbol = "&&&&&"

        # Use properties directly from the loaded objects
        data = dataset.data
        safe_dict = SafeDict({
            'data': data,
            'experiment_description': dataset.experiment_description,
            'biological_context': analysis_run.biological_context
        })
        
        prompt = agent.prompt_template.format_map(safe_dict)
        
        if (n_hypotheses_per_agent > 1):
            prompt += f"\n\nGenerate {n_hypotheses_per_agent} hypotheses without explicitly mention the number of hypotheses in the response text. Separate the text between each hypothesis with the following symbols: {separation_symbol}."

        # Load the LLM associated with the agent
        llm = LLM.load(self.db, agent.llm_id)
        if not llm:
            raise ValueError("LLM not found")

        # Generate hypothesis text using the LLM
        hypothesis_text = llm.query(agent.context, prompt)
        
        if (n_hypotheses_per_agent > 1):
            ids = []
            hypothesis_arr = hypothesis_text.split(separation_symbol)
            for hypothesis_text in hypothesis_arr:
                # Strip leading and trailing whitespace
                cleaned_text = hypothesis_text.strip()
        
                # Remove "Hypothesis #" prefix if it exists
                if cleaned_text.lower().startswith('hypothesis '):
                    colon_index = cleaned_text.find(':')
                    if colon_index != -1:
                        cleaned_text = cleaned_text[colon_index + 1:].strip()
                
                if len(cleaned_text) > 5:
                    # Create and save the hypothesis
                    hypothesis = Hypothesis.create(
                        self.db,
                        hypothesis_text=cleaned_text.strip(),
                        data=data,
                        biological_context=analysis_run.biological_context,
                        agent_id=agent_id,
                        dataset_id=dataset.object_id,
                        description=description, 
                        analysis_run_id=analysis_run_id, 
                        full_prompt = prompt
                    )
                    ids.append(hypothesis.object_id)
            return ids
        
        else:

            # Create and save the hypothesis
            hypothesis = Hypothesis.create(
                self.db,
                hypothesis_text=hypothesis_text,
                data=data,
                biological_context=analysis_run.biological_context,
                agent_id=agent_id,
                dataset_id=dataset.object_id,
                description=description, 
                analysis_run_id=analysis_run_id, 
                full_prompt = prompt
            )

            return [hypothesis.object_id]

# Example usage:
# generator = HypothesisGenerator(db)
# hypothesis_id = generator.generate_hypothesis(agent_id, dataset_id)
