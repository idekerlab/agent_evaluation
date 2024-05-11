from jsonschema import validate, ValidationError

object_specifications = {
    # MARK:llm
    "llm": {
        "properties": {
            "type": {
                "type": "str",
                "input_type": "dropdown",
                "options": ["OpenAI", "Groq"],
                "view": "text",
                "editable": True,
                "default": "Groq"
            },
            "model_name": {
                "type": "str",
                "input_type": "dropdown",
                "conditional_on": "type",
                "options": {"OpenAI": ["gpt-3.5-turbo-1106", "gpt-4.0-turbo-1106"],
                            "Groq": ["llama3-8b-8192", "llama4-8b-8192"]},
                "view": "text",
                "default": "llama3-8b-8192",
                "editable": True
            },
            "max_tokens": {
                "type": "int",
                "input_type": "number",
                "view": "text",
                "default": 2048,
                "editable": True
            },
            "seed": {
                "type": "int",
                "input_type": "number",
                "view": "text",
                "default": 42,
                "editable": True
            },
            "temperature": {
                "type": "float",
                "input_type": "number",
                "view": "text",
                "default": 0.5,
                "editable": True
            },
            "description": {
                "type": "str",
                "editable": True,
                "input_type": "textarea",
                "view": "text"
            }
        },
    },
    # MARK:analyst
    "analyst": {
        "properties": {
            "llm_id": {
                "type": "object_id",
                "input_type": "select_single_object",
                "object_type": "llm",
                "view": "object_link",
                "editable": True
            },
            "context": {
                "type": "str",
                "editable": True,
                "input_type": "textarea",
                "view": "text"
            },
            "prompt_template": {
                "type": "str",
                "editable": True,
                "input_type": "textarea",
                "view": "text"
            },
            "name": {
                "type": "str",
                "editable": True,
                "input_type": "text",
                "view": "text"
            },
            "description": {
                "type": "str",
                "editable": True,
                "input_type": "textarea",
                "view": "text"
            }
        }
    },
    # MARK:dataset
    "dataset": {
        "properties": {
            "name": {
                "type": "str",
                "input_type": "text",
                "view": "text",
                "editable": True
            },
            "data": {
                "type": "csv",
                "input_type": "upload_table",
                "view": "scrolling_table",
                "editable": True
            },
            "experiment_description": {
                "type": "str",
                "editable": True,
                "input_type": "textarea",
                "view": "text"
            },
            "description": {
                "type": "str",
                "editable": True,
                "input_type": "textarea",
                "view": "text"
            }
        }
    },
    # MARK:testplan
    "testplan": {
        "actions": ["create_test"],
        "properties": {
            "analyst_ids": {
                "type": "list_of_object_ids",
                "input_type": "select_multiple_objects",
                "object_type": "analyst",
                "view": "list_of_object_links",
                "editable": True
            },
            "dataset_id": {
                "type": "object_id",
                "input_type": "select_single_object",
                "object_type": "dataset",
                "view": "object_link",
                "editable": True
            },
            "n_hypotheses_per_analyst": {
                "type": "int",
                "input_type": "number",
                "view": "text",
                "editable": True,
                "default": 2
            },
            "description": {
                "type": "str",
                "editable": True,
                "input_type": "textarea",
                "view": "text"
            }
        }
    },
    # MARK: test
    "test": {
        "properties": {
            "analyst_ids": {
                "type": "list_of_object_ids",
                "object_type": "analyst",
                "view": "list_of_object_links",
                "editable": False,
            },
            "dataset_id": {
                "type": "object_id",
                "object_type": "dataset",
                "view": "object_link",
                "editable": False
            },
            "n_hypotheses_per_analyst": {
                "type": "int",
                "editable": False,
                "view": "text"
            },
            "hypothesis_ids": {
                "type": "list_of_object_ids",
                "object_type": "hypothesis",
                "view": "list_of_object_links",
                "editable": False
            },
            "description": {
                "type": "str",
                "editable": True,
                "input_type": "textarea",
                "view": "text"
            }
        }
    },
    # MARK:hypothesis
    "hypothesis": {
        "properties": {
            "data": {
                "type": "csv",
                "view": "scrolling_table",
                "editable": False,
                "object_type": "dataset"
            },
            "hypothesis_text": {
                "type": "str",
                "editable": False,
                "input_type": "textarea",
                "view": "text"
            },
            "analyst_id": {
                "type": "object_id",
                "object_type": "analyst",
                "view": "object_link",
                "editable": False
            },
            "dataset_id": {
                "type": "object_id",
                "object_type": "dataset",
                "view": "object_link",
                "editable": False
            },
            "description": {
                "type": "str",
                "editable": True,
                "input_type": "textarea",
                "view": "text"
            },
            "test_id": {
                "type": "object_id",
                "object_type": "test",
                "view": "object_link",
                "editable": False
            }
        }
    },
    # MARK:reviewer
    "reviewer": {
        "properties": {
            "llm_id": {
                "type": "object_id",
                "editable": True,
                "input_type": "select_single_object",
                "object_type": "test",
                "view": "object_link"
            },
            "context": {
                "type": "str",
                "editable": True,
                "input_type": "textarea",
                "view": "text"
            },
            "prompt_template": {
                "type": "str",
                "editable": True,
                "input_type": "textarea",
                "view": "text"
            },
            "name": {
                "type": "str",
                "editable": True,
                "input_type": "text",
                "view": "text"
            },
            "description": {
                "type": "str",
                "editable": True,
                "input_type": "textarea",
                "view": "text"
            }
        }
    },
    # MARK:reviewplan
    "reviewplan": {
        "actions": ["create_review"],
        "properties": {
            "reviewer_ids": {
                "type": "list_of_object_ids",
                "editable": True,
                "input_type": "select_multiple_objects",
                "object_type": "reviewer",
                "view": "list_of_object_links"
            },
            "test_id": {
                "type": "object_id",
                "editable": True,
                "input_type": "select_single_object",
                "object_type": "test",
                "view": "object_link"
            },
            "description": {
                "type": "str",
                "editable": True,
                "input_type": "textarea",
                "view": "text"
            }
        }
    },
    # MARK:review
    "review": {
        "properties": {
            "hypotheses_section": {
                "type": "str",
                "editable": False,
                "view": "text"},
            "review_text": {
                "type": "str",
                "editable": False,
                "view": "text"},
            "reviewer_id": {
                "type": "object_id",
                "editable": False,
                "view": "object_link",
                "object_type": "reviewer"},
            "description": {
                "type": "str",
                "editable": True,
                "input_type": "textarea",
                "view": "text"},
            "test_id": {
                "type": "object_id",
                "object_type": "test",
                "view": "object_link",
                "editable": False}
            }
        },
    
    # MARK:reviewset
    "reviewset": {
        "properties": {
            "review_plan_id": {
                "type": "object_id",
                "editable": False,
                "view": "object_link",
                "object_type": "reviewplan"},
            "review_ids": {
                "type": "list_of_object_ids",
                "editable": False,
                "view": "list_of_object_links",
                "object_type": "review"
            },
            "description": {
                "type": "str",
                "editable": True,
                "input_type": "textarea",
                "view": "text"
            }
        }
    }
}

from jsonschema import validate, ValidationError

# Define the JSON schema for validating your object specifications
schema = {
    "type": "object",
    "patternProperties": {
        "^.+$": {  # Applies to all properties at this level
            "type": "object",
            "properties": {
                "properties": {
                    "type": "object",
                    "patternProperties": {
                        "^.+$": {
                            "type": "object",
                            "required": ["type", "editable", "view"],
                            "properties": {
                                "type": {"type": "string"},
                                "input_type": {"type": "string"},
                                "options": {
                                    "oneOf": [
                                        {"type": "array"},
                                        {"type": "object"}
                                    ]
                                },
                                "object_type": {"type": "string"},
                                "view": {"type": "string"},
                                "editable": {"type": "boolean"},
                                "conditional_on": {"type": "string"},
                                "description": {"type": "string"},
                                "default": {}
                            },
                            "dependencies": {
                                "editable": {
                                    "oneOf": [
                                        {
                                            "properties": {
                                                "editable": {"enum": [True]},
                                                "input_type": {"type": "string"}
                                            }
                                        },
                                        {
                                            "properties": {
                                                "editable": {"enum": [False]}
                                            }
                                        }
                                    ]
                                },
                                "type": {
                                    "oneOf": [
                                        {
                                            "properties": {
                                                "type": {"enum": ["object_id", "list_of_object_ids"]},
                                                "object_type": {"type": "string"},
                                                "view": {"type": "string", "pattern": ".*object_link.*|.*list_of_object_links.*"}
                                            }
                                        },
                                        {
                                            "properties": {
                                                "type": {"not": {"enum": ["object_id", "list_of_object_ids"]}}
                                            }
                                        }
                                    ]
                                }
                            },
                            "additionalProperties": False
                        }
                    },
                    "additionalProperties": False
                }
            },
            "required": ["properties"]
        }
    },
    "additionalProperties": False
}

def validate_object_specifications(specs):
    try:
        validate(instance=specs, schema=schema)
        print("Validation passed.")
    except ValidationError as e:
        print("Validation failed:", e.message)


