from llm import llm_query
from hypothesis import Hypothesis
from review import Review
from comparison import Comparison



class Reviewer:
    def __init__(self, llm, context, prompt_template, name):
        """
        Initializes a new Reviewer instance.

        :param llm: The language model used for generating comparisons.
        :param context: The context used for generating queries for the LLM.
        :param prompt_template: A template used to generate queries for the LLM.
        :param name: Name of the Reviewer.
        """
        self.llm = llm
        self.context = context
        self.prompt_template = prompt_template
        self.name = name

    def generate_comparison(self, hypothesis_a, hypothesis_b, dataset, log_file=None):
        """
        Generates a comparison between two hypotheses.

        :param hypothesis_a: A Hypothesis instance.
        :param hypothesis_b: A Hypothesis instance.
        :return: A Comparison instance.
        """
        comparison = Comparison()
        prompt = self.prompt_template.format(experiment_description=dataset.experiment_description, 
                                             data=dataset.data,
                                             hypothesis_a=hypothesis_a.text,
                                             hypothesis_b=hypothesis_b.text)
        
        response = llm_query(self.context,
                             prompt, 
                             self.llm, 
                             self.temperature, 
                             self.max_tokens,
                             log_file)
