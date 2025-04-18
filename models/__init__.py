class LLM:
    def __init__(self, db, type=None, model_name=None, max_tokens=None, seed=None, temperature=None, llm_id=None):
        self.db = db
        self.type = type
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.seed = seed
        self.temperature = temperature
        self.llm_id = llm_id

    @classmethod
    def create(cls, db, type, model_name, max_tokens, seed, temperature):
        # Create the LLM instance in the database
        llm_data = {
            "type": type,
            "model_name": model_name,
            "max_tokens": max_tokens,
            "seed": seed,
            "temperature": temperature
        }
        llm_id = db.add(llm_data, label="LLM")
        return cls(db, type, model_name, max_tokens, seed, temperature, llm_id)

    @classmethod
    def load(cls, db, llm_id):
        # Load the LLM instance from the database
        data = db.load(llm_id)
        if data:
            return cls(db, **data)
        else:
            return None

    def update(self, **kwargs):
        # Update attributes of the LLM instance
        for key, value in kwargs.items():
            setattr(self, key, value)
        # Assume db.update is a method to update the record in the database
        self.db.update(self.llm_id, **kwargs)

    def __repr__(self):
        return f"<LLM {self.type} {self.model_name} (ID: {self.llm_id})>"
