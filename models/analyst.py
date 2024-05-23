import datetime

class Analyst:
    def __init__(self, db, llm_id=None, context=None, prompt_template=None, name=None, description=None, id=None, created=None):
        self.db = db
        self.llm_id = llm_id
        self.context = context
        self.prompt_template = prompt_template
        self.name = name
        self.description = description
        self.id = id
        self.created = created

    @classmethod
    def create(cls, db, llm_id, context, prompt_template, name=None, description=""):
        properties = {
            "llm_id": llm_id,
            "context": context,
            "prompt_template": prompt_template,
            "name": name,
            "description": description,
            #"created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        id, created = db.add(properties, object_type="Analyst")
        return cls(db, llm_id, context, prompt_template, name, description, id=id, created=created)

    @classmethod
    def load(cls, db, id):
        data = db.load(id)
        if data:
            return cls(db, **data)
        return None

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.db.update(self.id, kwargs)
