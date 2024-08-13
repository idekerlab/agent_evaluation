import json

class Agent:
    def __init__(self, db, llm_id=None, context=None, 
                 prompt_template=None, name=None, description=None, 
                 object_id=None, created=None):
        self.db = db
        self.llm_id = llm_id
        self.context = context
        self.prompt_template = prompt_template
        self.name = name
        self.description = description
        self.object_id = object_id
        self.created = created

    @classmethod
    def create(cls, db, llm_id, context, prompt_template, name=None, description=""):
        properties = {
            "llm_id": llm_id,
            "context": context,
            "prompt_template": prompt_template,
            "name": name,
            "description": description,
        }
        object_id, created, _ = db.add(object_id=None, properties=properties, object_type="agent")
        return cls(db, llm_id, context, prompt_template, name, description, object_id=object_id, created=created)

    @classmethod
    def load(cls, db, object_id):
        properties, _ = db.load(object_id)
        if properties:
            return cls(db, **properties)
        return None

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.db.update(self.object_id, kwargs)
        
    def to_json(self):
        return json.dumps({
            "llm_id": self.llm_id,
            "context": self.context,
            "prompt_template": self.prompt_template,
            "name": self.name,
            "description": self.description,
            "object_id": self.object_id,
            "created": self.created
        })
