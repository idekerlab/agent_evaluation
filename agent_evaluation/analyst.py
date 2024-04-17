from agent_evaluation.hypothesis import Hypothesis

class Analyst:
    def __init__(self, llm, context, prompt_template, name, label):
        """
        Initializes a new Analyst instance.

        :param llm: The language model used for generating hypotheses.
        :param prompt_template: A template used to generate queries for the LLM.
        :param name: Name of the Analyst.
        :param label: Description of the Analyst.
        """
        self.llm = llm
        self.context = context
        self.prompt_template = prompt_template
        self.name = name
        self.label = label

    def generate_hypothesis(self, dataset, log_file=None):
        """
        Generates a hypothesis based on the given dataset.

        :param dataset: A Dataset instance.
        :return: A Hypothesis instance.
        """
        prompt = self.prompt_template.format(data=dataset.data)
        response = self.llm.query(self.context, prompt)
        return Hypothesis(dataset=dataset, description=response, analyst=self)

