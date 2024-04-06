from agent_evaluation.hypothesis import Hypothesis
from agent_evaluation.ae_object import AE_Object

# class Analyst:
#     def __init__(self, llm, context, prompt_template, name, description):
#         """
#         Initializes a new Analyst instance.

#         :param llm: The language model used for generating hypotheses.
#         :param prompt_template: A template used to generate queries for the LLM.
#         :param name: Name of the Analyst.
#         :param description: Description of the Analyst's purpose.
#         """
#         self.llm = llm
#         self.context = context
#         self.prompt_template = prompt_template
#         self.name = name
#         self.description = description

#     def generate_hypothesis(self, dataset, log_file=None):
#         """
#         Generates a hypothesis based on the given dataset.

#         :param dataset: A Dataset instance.
#         :return: A Hypothesis instance.
#         """
#         prompt = self.prompt_template.format(data=dataset.data)
#         response = self.llm.query(self.context, prompt)
#         return Hypothesis(dataset=dataset, description=response, analyst=self)

class Analyst(AE_Object):
    def __init__(self, db, llm, context, prompt_template, name, description, persist=False, get=False):
        """
        Initializes a new Analyst instance with the option to persist or retrieve from the database.

        :param db: The database object for persistence operations.
        :type db: Database
        :param llm: The language model used for generating hypotheses.
        :type llm: LanguageModel
        :param context: The context used for the LLM to generate queries.
        :type context: str
        :param prompt_template: A template used to generate queries for the LLM.
        :type prompt_template: str
        :param name: Name of the Analyst, serves as a unique identifier.
        :type name: str
        :param description: Description of the Analyst's purpose.
        :type description: str
        :param persist: Whether to persist the Analyst instance upon initialization.
        :type persist: bool
        :param get: Whether to attempt to create the instance from the database.
        :type get: bool
        """
        super().__init__(db)
        self.llm = llm
        self.context = context
        self.prompt_template = prompt_template
        self.name = name
        self.description = description

        if get:
            self.load()
        elif persist:
            self.save()

    def to_dict(self):
        """
        Converts instance properties to a dictionary for persistence.
        
        :returns: A dictionary representation of the Analyst instance.
        :rtype: dict
        """
        return {
            'llm': self.llm,
            'context': self.context,
            'prompt_template': self.prompt_template,
            'description': self.description
        }

    def from_dict(self, properties):
        """
        Sets instance properties from a dictionary retrieved from the database.
        
        :param properties: A dictionary of properties to set on the instance.
        :type properties: dict
        """
        self.llm = properties.get('llm')
        self.context = properties.get('context')
        self.prompt_template = properties.get('prompt_template')
        self.description = properties.get('description')

    # The generate_hypothesis method remains unchanged from your definition
