from agent_evaluation.hypothesis import Hypothesis
from agent_evaluation.review import Review
from agent_evaluation.comparison import Comparison



class Reviewer:
    def __init__(self, llm, context, prompt_template, name, label):
        """
        Initializes a new Reviewer instance.

        :param llm: The language model used for generating comparisons.
        :param context: The context used for generating queries for the LLM.
        :param prompt_template: A template used to generate queries for the LLM.
        :param name: Name of the Reviewer.
        :param label: Description of the Reviewer.
        """
        self.llm = llm
        self.context = context
        self.prompt_template = prompt_template
        self.name = name
        self.label = label

    def generate_comparison(self, hypothesis_a, hypothesis_b, dataset, log_file=None):
        """
        Generates a comparison between two hypotheses.

        :param hypothesis_a: A Hypothesis instance.
        :param hypothesis_b: A Hypothesis instance.
        :return: A Comparison instance.
        """
        
        prompt = self.prompt_template.format(experiment_description=dataset.experiment_description, 
                                             data=dataset.data,
                                             hypothesis_a=hypothesis_a.description,
                                             hypothesis_b=hypothesis_b.description,
                                             analyst_a = hypothesis_a.analyst.name,
                                             analyst_b = hypothesis_b.analyst.name)
                                        
        
        response = self.llm.query(self.context, prompt)
        
        
        # Parse the response to extract the comparison values
        
        comparison= Comparison(hypothesis_a, hypothesis_b, self,
                                factuality=None, 
                                novelty=None, 
                                significance=None, 
                                plausibility=None, 
                                logic=None, 
                                combined=None,
                                comment=response)

        return comparison
        
    