import os
from openai import OpenAI, APIError
from groq import Groq
import requests
from app.config import load_api_key


class LLM:
    def __init__(self, db, type=None, model_name=None,
                 max_tokens=None, seed=None, temperature=None,
                 id=None, created=None):
        self.db = db
        self.type = type
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.seed = seed
        self.temperature = temperature
        self.id = id
        self.created = created

    @classmethod
    def create(cls, db, type, model_name, max_tokens, seed, temperature):
        # Create the LLM instance in the database
        properties = {
            "type": type,
            "model_name": model_name,
            "max_tokens": max_tokens,
            "seed": seed,
            "temperature": temperature
        }
        id, created = db.add(properties, label="LLM")
        return cls(db, type, model_name, max_tokens, seed, temperature, id, created)

    @classmethod
    def load(cls, db, id):
        # Load the LLM instance from the database
        data = db.load(id)
        if data:
            return cls(db, **data)
        else:
            return None

    def update(self, **kwargs):
        # Update attributes of the LLM instance
        for key, value in kwargs.items():
            setattr(self, key, value)
        # update the record in the database
        self.db.update(self.id, kwargs)

    def query(self, context, prompt):
        if self.type == 'OpenAI':
            return self.query_openai(context, prompt)
        elif self.type == 'Groq':
            return self.query_groq(context, prompt)
        else:
            raise ValueError(f"Unsupported llm type: {self.type}")

    def query_openai(self, context, prompt):
        """
        Queries the OpenAI model with the given context and prompt.

        :param context: The context to use when querying the model.
        :param prompt: The prompt to use when querying the model.
        :return: The model's response
        (maybe later: also return tokens used.)
        """
        # Load the API keys
        key = load_api_key("OPENAI_API_KEY")
        if not key:
            raise EnvironmentError("OPENAI_API_KEY environment variable not set.")
        client = OpenAI()
        client.api_key = key

        try:
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": context},
                    {"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                n=1,
                stop=None,
                seed=self.seed,
                temperature=self.temperature,
            )
            response_content = response.choices[0].message.content.strip()
            # tokens_used = response.usage.total_tokens
            return response_content
        except APIError as e:
            raise Exception(f"API error occurred: {e}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed with an exception: {e}")

    def query_groq(self, context, prompt):
        """
        Queries a model hosted on groq with the given context and prompt.

        :param context: The context to use when querying the model.
        :param prompt: The prompt to use when querying the model.
        :return: the model's response.
        (maybe later: also return tokens used.)
        """
        key = load_api_key("GROQ_API_KEY")
        if not key:
            raise EnvironmentError("GROQ_API_KEY environment variable not set.")
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

        try:
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": context},
                    {"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                stop=None,
                temperature=self.temperature,
            )
            response_content = response.choices[0].message.content.strip()
            # tokens_used = response.usage.total_tokens
            return response_content
        except Exception as e:
            raise Exception(f"groq transaction error occurred: {e}")
    
    def __repr__(self):
        return f"<LLM {self.type} {self.model_name} (ID: {self.id})>"
