from hre.llm.llm_query import llm_query
from hre.analysis.hypothesis import Hypothesis

class Analyst:
    def __init__(self, llm, context, prompt_template, name, description, 
                 temperature=0.0, 
                 max_tokens=1000):
        """
        Initializes a new Analyst instance.

        :param llm: The language model used for generating hypotheses.
        :param prompt_template: A template used to generate queries for the LLM.
        :param name: Name of the Analyst.
        :param description: Description of the Analyst's purpose.
        """
        self.llm = llm
        self.context = context
        self.prompt_template = prompt_template
        self.name = name
        self.description = description
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate_hypothesis(self, dataset, log_file=None):
        """
        Generates a hypothesis based on the given dataset.

        :param dataset: A Dataset instance.
        :return: A Hypothesis instance.
        """
        prompt = self.prompt_template.format(data=dataset.data)
        response = llm_query(self.context,
                             prompt, 
                             self.llm, 
                             self.temperature, 
                             self.max_tokens,
                             log_file)
        return Hypothesis(dataset=dataset, description=response, analyst=self)

