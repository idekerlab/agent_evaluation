
class HypothesisSet:
    def __init__(self, db, hypothesis_ids=None, user_ids=None, 
                 description=None, object_id=None, name=None, created=None):
        self.db = db
        self.hypothesis_ids = hypothesis_ids if hypothesis_ids else []
        self.user_ids = user_ids if user_ids else []
        self.description = description
        self.object_id = object_id
        self.name = name if name else "none"
        self.created = created

    @classmethod
    def create(cls, db, review_plan_id, agent_ids, analysis_run_id, description, name):
        properties = {
            "review_plan_id": review_plan_id,
            "agent_ids": agent_ids,
            "analysis_run_id": analysis_run_id,
            "review_ids": [],
            "description": description,
            "name": name,
            "attempts": {agent: [] for agent in agent_ids},
            "status": "pending"
        }
        object_id, created, _ = db.add(object_id=None, properties=properties, object_type="review_set")
        return cls(db, review_plan_id, agent_ids, analysis_run_id, [], 
                   description, "", properties['attempts'], 'pending', object_id, name, created)

    @classmethod
    def load(cls, db, object_id):
        properties, _ = db.load(object_id)
        if properties:
            return cls(db, **properties)
        return None

    def update(self):
        properties = {
            "review_ids": self.review_ids,
            "attempts": self.attempts,
            "status": self.status,
            "run_log": self.run_log
        }
        self.db.update(self.object_id, properties)

    def delete(self):
        self.db.remove(self.object_id)

    def add_review(self, review_id, agent_id):
        if self.status == 'done':
            return "ReviewSet is already completed."
        
        self.review_ids.append(review_id)
        self.attempts[agent_id].append('success')  # Assuming hypothesis generation was successful
        self.update_status()
        self.update()
        return "Review added successfully."

    def update_status(self):
        total_attempts = sum(len(attempts) for attempts in self.attempts.values())
        required_attempts = len(self.agent_ids)
        if total_attempts >= required_attempts:
            self.status = 'done'
        else:
            self.status = 'in_progress'
            
    def update_run_log(self, run_log):
        self.run_log = run_log
        self.update()
