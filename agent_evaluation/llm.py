from abc import ABC, abstractmethod

class LLM(DB_Object, ABC):
    def __init__(self, db, db_unique_id, model_name, temperature=0.5, max_tokens=1000, seed=None, persist=False):
        """
        Initializes a new LLM instance, setting up the model parameters and database interaction.

        :param db: Database instance for persistence.
        :param db_unique_id: Unique identifier for the LLM.
        :param model_name: The name of the model to query.
        :param temperature: The temperature to use when querying the model, affecting randomness.
        :param max_tokens: The maximum number of tokens to generate.
        :param seed: The seed for random number generation to ensure reproducibility.
        :param persist: Whether to persist the model instance upon initialization.
        """
        super().__init__(db, db_unique_id, persist)
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.seed = seed

    @abstractmethod
    def query(self, context, prompt):
        """
        Queries the model with the given prompt.

        :param context: The context to use when querying the model.
        :param prompt: The prompt to use when querying the model.
        :return: The model's response to the prompt.
        """
        pass

    def to_dict(self):
        """
        Converts instance properties to a dictionary for persistence.
        """
        return {
            'model_name': self.model_name,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'seed': self.seed
        }

    def from_dict(self, properties):
        """
        Populates instance properties from a dictionary retrieved from the database.
        """
        self.model_name = properties.get('model_name', '')
        self.temperature = properties.get('temperature', 0.5)
        self.max_tokens = properties.get('max_tokens', 1000)
        self.seed = properties.get('seed', None)


import openai
import os
import time
import requests

class OpenAI_LLM(LLM):
    def __init__(self, db, db_unique_id, model_name="text-davinci-002", temperature=0.5, max_tokens=2048, seed=None, persist=False):
        """
        Initializes a new instance of OpenAI_LLM with specific configurations for the OpenAI model.

        :param db: Database instance for persistence.
        :param db_unique_id: Unique identifier for the LLM.
        :param model_name: The name of the OpenAI model to query, default is the latest available model.
        :param temperature: The temperature to use when querying the model, affecting randomness.
        :param max_tokens: The maximum number of tokens to generate.
        :param seed: The seed for random number generation to ensure reproducibility.
        :param persist: Whether to persist the model instance upon initialization.
        """
        super().__init__(db, db_unique_id, model_name, temperature, max_tokens, seed, persist)

    def query(self, context, prompt):
        """
        Queries the OpenAI model with the given context and prompt.

        :param context: The context to use when querying the model.
        :param prompt: The prompt to use when querying the model.
        :return: A tuple containing the model's response, system fingerprint, and tokens used.
        """
        key = os.environ.get('OPENAI_API_KEY')
        if not key:
            raise EnvironmentError("OPENAI_API_KEY environment variable not set.")
        
        openai.api_key = key
        try:
            response = openai.Completion.create(
                engine=self.model_name,
                prompt=f"{context}\n\n{prompt}",
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                n=1,
                stop=None,
                seed=self.seed
            )
            response_content = response.choices[0].text.strip()
            tokens_used = response.usage.total_tokens
            return response_content, tokens_used
        except openai.APIError as e:
            raise Exception(f"API error occurred: {e}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed with an exception: {e}")

