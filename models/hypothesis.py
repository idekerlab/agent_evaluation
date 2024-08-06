 

class Hypothesis:
    def __init__(self, db, name=None, hypothesis_text=None, data=None, biological_context=None, agent_id=None, 
                 dataset_id=None, description=None, analysis_run_id=None, 
                 object_id=None, full_prompt = None, created=None):
        self.db = db
        self.hypothesis_text = hypothesis_text
        self.data = data
        self.biological_context=biological_context
        self.agent_id = agent_id
        self.dataset_id = dataset_id
        self.description = description
        self.analysis_run_id = analysis_run_id
        self.object_id = object_id
        self.created = created
        self.name = name
        self.full_prompt = full_prompt

    @classmethod
    def create(cls, db, hypothesis_text, data, biological_context, agent_id, dataset_id, description, analysis_run_id, name=None, full_prompt = None):
        properties = {
            "name": name,
            "hypothesis_text": hypothesis_text,
            "data": data,
            "biological_context": biological_context,
            "agent_id": agent_id,
            "dataset_id": dataset_id,
            "description": description,
            "analysis_run_id": analysis_run_id,
            "full_prompt": full_prompt
        }
        object_id, created, _ = db.add(object_id=None, properties=properties, object_type="hypothesis")
        hypothesis = cls(db, name, hypothesis_text, data, biological_context, agent_id, dataset_id, 
                   description, analysis_run_id, object_id=object_id, full_prompt = full_prompt, created=created)
        if not name:
            agent_properties, agent_type = db.load(agent_id)
            hypothesis.update(name=f"hypothesis - {agent_properties['name']} - {biological_context}")

        return hypothesis

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

    def delete(self):
        self.db.remove(self.object_id)
