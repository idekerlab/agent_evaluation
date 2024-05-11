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
        # Assume db.update is a method to update the record in the database
        self.db.update(self.id, kwargs)

    def query(self, context, prompt):
        if self.type == 'OpenAI':
            return self.query_openai(context, prompt)
        elif self.type == 'Groq':
            return self.query_groq(context, prompt)
        else:
            raise ValueError(f"Unsupported llm type: {self.type}")

    def query_openai(self, context, prompt):
        key = os.getenv('OPENAI_API_KEY')
        if not key:
            raise EnvironmentError("OPENAI_API_KEY environment variable not set.")
        import openai  # Assuming the OpenAI library is used
        try:
            response = openai.Completion.create(
                engine=self.model_name,
                prompt=f"{context}\n{prompt}",
                max_tokens=self.max_tokens,
                n=1,
                stop=None,
                temperature=self.temperature,
                presence_penalty=0.5  # Example additional parameter
            )
            return response.choices[0].text.strip(), response.usage.total_tokens
        except openai.error.OpenAIError as e:
            raise Exception(f"API error occurred: {e}")

    def query_groq(self, context, prompt):
        key = os.getenv('GROQ_API_KEY')
        if not key:
            raise EnvironmentError("GROQ_API_KEY environment variable not set.")
        # Assuming the use of a hypothetical 'GroqClient' library
        import groqclient  # This is hypothetical and needs to be replaced with actual library usage
        client = groqclient.Client(api_key=key)
        try:
            response = client.create_completion(
                model_name=self.model_name,
                prompt=f"{context}\n{prompt}",
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            return response.text.strip(), response.tokens_used  # Assuming these attributes exist
        except Exception as e:
            raise Exception(f"Groq transaction error occurred: {e}")
        
    def __repr__(self):
        return f"<LLM {self.type} {self.model_name} (ID: {self.id})>"
