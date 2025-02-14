import json
from helpers.safe_dict import SafeDict
from models.llm import LLM

class Agent:
    def __init__(self, llm_id=None, context=None, 
                 prompt_template=None, name="unnamed", description=None, 
                 object_id=None, created=None):
        self.llm_id = llm_id
        self.context = context
        self.prompt_template = prompt_template
        self.name = name
        self.description = description
        self.object_id = object_id
        self.created = created

    @classmethod
    def create(cls, db, llm_id, context, prompt_template, name="unnamed", description=""):
        """Create a new agent in the database.
        
        Note: db parameter is used only for creation and not stored in the instance.
        """
        properties = {
            "llm_id": llm_id,
            "context": context,
            "prompt_template": prompt_template,
            "name": name,
            "description": description,
        }
        object_id, created, _ = db.add(object_id=None, properties=properties, object_type="agent")
        return cls(llm_id, context, prompt_template, name, description, object_id=object_id, created=created)

    @classmethod
    def load(cls, db, object_id):
        """Load an agent from the database.
        
        Note: db parameter is used only for loading and not stored in the instance.
        """
        properties, _ = db.load(object_id)
        if properties:
            return cls(**properties)
        return None

    def update(self, db, **kwargs):
        """Update agent properties in the database.
        
        Note: db parameter must be provided for the update operation.
        """
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.update(self.object_id, kwargs)
        
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
    
    def run(self, properties=None, dataset_id=None, json_object_id=None):
        """Run the agent with optional property sources.
        
        Args:
            properties: Dictionary of properties (highest priority)
            dataset_id: ID of dataset to extract experiment description and data from (medium priority)
            json_object_id: ID of JSON object to extract properties from (lowest priority)
            
        Properties are merged with the following priority:
        1. Explicitly passed properties argument
        2. Dataset properties (experiment_description, data)
        3. JSON object properties
        
        Returns:
            Parsed JSON object. If output is not valid JSON, returns {"data": output_text}
        """
        # Create a new database connection for this thread
        from app.sqlite_database import SqliteDatabase
        from app.config import load_database_uri
        db = SqliteDatabase(load_database_uri())
        
        try:
            # Initialize merged properties
            merged_props = {}
            
            # Load JSON object properties (lowest priority)
            if json_object_id:
                json_props, _ = db.load(json_object_id)
                if json_props and 'json' in json_props:
                    json_data = json_props['json']
                    if isinstance(json_data, dict):
                        # If json is a dict, merge all its top-level properties
                        merged_props.update(json_data)
                    else:
                        # If json is not a dict, store it under 'json' key
                        merged_props['json'] = json_data
            
            # Load dataset properties (medium priority)
            if dataset_id:
                dataset_props, _ = db.load(dataset_id)
                if dataset_props:
                    if 'experiment_description' in dataset_props:
                        merged_props['experiment_description'] = dataset_props['experiment_description']
                    if 'data' in dataset_props:
                        merged_props['data'] = dataset_props['data']
            
            # Merge explicit properties (highest priority)
            if properties:
                merged_props.update(properties)
            
            # Create SafeDict and run prompt
            safe_dict = SafeDict(merged_props)
            prompt = self.prompt_template.format_map(safe_dict)
            
            # Load the LLM associated with the agent
            llm = LLM.load(db, self.llm_id)
            if not llm:
                raise ValueError("LLM not found")

            # Generate output using the LLM
            output_text = llm.query(self.context, prompt)
            
            # Try to parse output as JSON
            try:
                return json.loads(output_text)
            except json.JSONDecodeError:
                # If not valid JSON, wrap in data property
                return {"data": output_text}
        finally:
            # Always close the database connection
            db.close()
