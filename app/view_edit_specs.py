from jsonschema import validate, ValidationError

object_specifications = {
    # MARK:llm
    "llm": {
        "properties": {
            "name": {
                "type": "string",
                "editable": True,
                "input_type": "text",
                "view": "text"
            },
            "type": {
                "type": "string",
                "input_type": "dropdown",
                "options": ["OpenAI", "Anthropic", "Groq", "GoogleAI", "LocalModel"],
                "view": "text",
                "editable": True,
                "default": "Groq"
            },
            "model_name": {
                "type": "string",
                "input_type": "dropdown",
                "label": "model name",
                "conditional_on": "type",
                "options": {"OpenAI": ["gpt-3.5-turbo", "gpt-4-turbo", "gpt-4-turbo-2024-04-09","gpt-4o-2024-05-13"],
                            "Anthropic": ["claude-3-haiku-20240307", "claude-3-sonnet-20240229", "claude-3-opus-20240229", "claude-3-5-sonnet-20240620"],
                            "Groq": ["llama3-8b-8192", "llama3-70b-8192", "llama-3.1-70b-versatile","llama-3.1-405b-reasoning"],
                            "GoogleAI": ["gemini-1.5-pro-latest", "gemini-1.5-pro-001",  "gemini-1.5-flash-latest", "gemini-1.5-flash-001", "gemini-1.0-pro-latest", "gemini-1.0-pro-001"], 
                            "LocalModel": [ 'mixtral:latest', 'mixtral:instruct', 'llama2:latest']},
                "view": "text",
                "default": "llama3-8b-8192",
                "editable": True
            },
            "max_tokens": {
                "type": "int",
                "label": "max tokens",
                "input_type": "number",
                "view": "text",
                "default": 2048,
                "min": 0,
                "max": "",
                "step": 1,
                "editable": True
            },
            "seed": {
                "type": "int",
                "input_type": "number",
                "view": "text",
                "default": 42,
                "min": 0,
                "max": "",
                "step": 1,
                "editable": True
            },
            "temperature": {
                "type": "float",
                "input_type": "number",
                "view": "text",
                "default": 0.0,
                "min": 0.0,
                "max": 1.0,
                "step": 0.1,
                "editable": True
            },
            "description": {
                "type": "string",
                "editable": True,
                "input_type": "textarea",
                "view": "text"
            }
        },
    },
    # MARK:analyst
    "analyst": {
        "properties": {
            "name": {
                "type": "string",
                "editable": True,
                "input_type": "text",
                "view": "text"
            },
            "context": {
                "type": "string",
                "editable": True,
                "input_type": "textarea",
                "view": "text"
            },
            "prompt_template": {
                "type": "string",
                "editable": True,
                "label": "prompt\ntemplate",
                "input_type": "textarea",
                "view": "text",
                # "regex": ".*\{experiment_description\}[^]*\{data\}.*|.*\{data\}[^]*\{experiment_description\}.*",
                # "regex_description": "The text must include \{data\} and \{experiment_description\} in any order. Valid keywords are: \{data\}, \{experiment_description\}, \{biological_context\}, \{hypotheses_text\}. Do not add open curly braces."
            },
            "description": {
                "type": "string",
                "editable": True,
                "input_type": "textarea",
                "view": "text"
            },
            "llm_id": {
                "type": "object_id",
                "label": "LLM",
                "input_type": "select_single_object",
                "object_type": "llm",
                "view": "object_link",
                "editable": True
            }
        }
    },
    # MARK:dataset
    "dataset": {
        "properties": {
            "name": {
                "type": "string",
                "input_type": "text",
                "view": "text",
                "editable": True
            },
            "experiment_description": {
                "label": "experiment description",
                "type": "string",
                "editable": True,
                "input_type": "textarea",
                "view": "text"
            },
            "data": {
                "type": "csv",
                "input_type": "upload_table",
                "view": "scrolling_table",
                "editable": True
            },
            "description": {
                "type": "string",
                "editable": True,
                "input_type": "textarea",
                "view": "text"
            }
        }
    },
    # MARK:analysis_plan
    "analysis_plan": {
        "actions": ["create_analysis_run"],
        "properties": {
            "name": {
                "type": "string",
                "editable": True,
                "input_type": "text",
                "view": "text"
            },
            "analyst_ids": {
                "type": "list_of_object_ids",
                "label": "analysts",
                "input_type": "select_multiple_objects",
                "object_type": "analyst",
                "view": "list_of_object_links",
                "editable": True
            },
            "dataset_id": {
                "type": "object_id",
                "label": "dataset",
                "input_type": "select_single_object",
                "object_type": "dataset",
                "view": "object_link",
                "editable": True
            },
            "n_hypotheses_per_analyst": {
                "type": "int",
                "label": "hypotheses\nper analyst",
                "input_type": "number",
                "view": "text",
                "editable": True,
                "default": 2,
                "min": 1,
                "max": "",
                "step": 1,
            },
            "biological_context": {
                "type": "string",
                "label": "biological context",
                "editable": True,
                "input_type": "textarea",
                "view": "text"
            },
            "description": {
                "type": "string",
                "editable": True,
                "input_type": "textarea",
                "view": "text"
            }
        }
    },
    # MARK: analysis_run
    "analysis_run": {
        "properties": {
            "name": {
                "type": "string",
                "editable": True,
                "input_type": "text",
                "view": "text"
            },
            "analyst_ids": {
                "type": "list_of_object_ids",
                "label": "analysts",
                "object_type": "analyst",
                "view": "list_of_object_links",
                "input_type": "select_multiple_objects",
                "editable": False,
            },
            "dataset_id": {
                "type": "object_id",
                "object_type": "dataset",
                "label": "dataset",
                "view": "object_link",
                "editable": False
            },
            "n_hypotheses_per_analyst": {
                "type": "int",
                "editable": False,
                "input_type": "number",
                "view": "text",
                "label": "hypotheses\nper analyst",
            },
            "biological_context": {
                "type": "string",
                "label": "biological context",
                "editable": False,
                "input_type": "textarea",
                "view": "text"
            },
            "hypothesis_ids": {
                "type": "list_of_object_ids",
                "object_type": "hypothesis",
                "view": "list_of_object_links",
                "input_type": "select_multiple_objects",
                "label": "hypotheses",
                "editable": False
            },
            "analysis_plan_id": {
                "type": "object_id",
                "object_type": "analysis_plan",
                "label": "analysis plan",
                "view": "object_link",
                "editable": False
            },
            "user_ids": {
                "type": "list_of_object_ids",
                "label": "user reviewers",
                "input_type": "select_multiple_objects",
                "object_type": "user",
                "view": "list_of_object_links",
                "editable": True
            },
            "description": {
                "type": "string",
                "editable": True,
                "input_type": "textarea",
                "view": "text"
            },
            "run_log": {
                "type": "string",
                "label": "run log",
                "editable": False,
                "input_type": "textarea",
                "view": "text",
                "collapsible": True
            }
        }
    },
    # MARK:hypothesis
    "hypothesis": {
        "properties": {
            "name": {
                "type": "string",
                "editable": True,
                "input_type": "text",
                "view": "text"
            },
            "hypothesis_text": {
                "type": "string",
                "label": "hypothesis",
                "editable": True,
                "input_type": "textarea",
                "view": "text"
            },
            "data": {
                "type": "csv",
                "view": "scrolling_table",
                "editable": False,
                "object_type": "dataset"
            },
            "biological_context": {
                "type": "string",
                "label": "biological context",
                "editable": False,
                "input_type": "textarea",
                "view": "text"
            },
            "analyst_id": {
                "type": "object_id",
                "object_type": "analyst",
                "label": "analyst",
                "view": "object_link",
                "editable": False
            },
            "dataset_id": {
                "type": "object_id",
                "object_type": "dataset",
                "label": "dataset",
                "view": "object_link",
                "editable": False
            },
            "description": {
                "type": "string",
                "editable": True,
                "input_type": "textarea",
                "view": "text"
            },
            "analysis_run_id": {
                "type": "object_id",
                "view": "object_link",
                "label": "analysis run",
                "editable": False
            },
            "full_prompt": {
                "type": "string",
                "label": "prompt",
                "editable": False,
                "input_type": "textarea",
                "view": "text",
                "collapsible": True
            }
        }
    },
    # MARK:reviewplan
    "review_plan": {
        "actions": ["create_review"],
        "properties": {
            "name": {
                "type": "string",
                "editable": True,
                "input_type": "text",
                "view": "text"
            },
            "analyst_ids": {
                "type": "list_of_object_ids",
                "label": "analysts",
                "input_type": "select_multiple_objects",
                "object_type": "analyst",
                "view": "list_of_object_links",
                "editable": True
            },
            "analysis_run_id": {
                "type": "object_id",
                "label": "analysis run",
                "editable": True,
                "input_type": "select_single_object",
                "object_type": "analysis_run",
                "view": "object_link"
            },
            "description": {
                "type": "string",
                "editable": True,
                "input_type": "textarea",
                "view": "text"
            }
        }
    },
    # MARK:reviewset
    "review_set": {
        "properties": {
            "name": {
                "type": "string",
                "editable": True,
                "input_type": "text",
                "view": "text"
            },
            "review_plan_id": {
                "type": "object_id",
                "label": "review plan",
                "editable": False,
                "view": "object_link",
                "object_type": "review_plan"
            },
            "review_ids": {
                "type": "list_of_object_ids",
                "label": "reviews",
                "editable": False,
                "view": "list_of_object_links",
                "object_type": "review"
            },
            "description": {
                "type": "string",
                "editable": True,
                "input_type": "textarea",
                "view": "text"
            },
            "run_log": {
                "type": "string",
                "label": "run log",
                "editable": False,
                "input_type": "textarea",
                "view": "text",
                "collapsible": True
            }
        }
    },
    # MARK:review
    "review": {
        "properties": {
            "name": {
                "type": "string",
                "editable": True,
                "input_type": "text",
                "view": "text"
            },
            "review_text": {
                "type": "string",
                "label": "review",
                "editable": True,
                "view": "text"
            },
            "ranking_data": {
                "type": "string",
                "label": "ranking data",
                "view": "text",
                "editable": True,
            },
            "summary_review": {
                "type": "string",
                "label": "summary review",
                "editable": True,
                "view": "text"
            },
            "hypotheses_text": {
                "type": "string",
                "label": "hypotheses list",
                "editable": False,
                "view": "text",
                "collapsible": True
            },
            "analyst_id": {
                "type": "object_id",
                "label": "analyst",
                "editable": False,
                "view": "object_link",
                "object_type": "analyst"
            },
            "description": {
                "type": "string",
                "editable": True,
                "input_type": "textarea",
                "view": "text"
            },
            "review_set_id": {
                "type": "object_id",
                "label": "review set",
                "object_type": "review_set",
                "view": "object_link",
                "editable": False
            },
            "analysis_run_id": {
                "type": "object_id",
                "label": "analysis run",
                "object_type": "analysis_run",
                "view": "object_link",
                "editable": False
            }
        }
    },
    "user": {
        "properties": {
            "name": {
                "type": "string",
                "editable": True,
                "input_type": "text",
                "view": "text"
            },
            "username": {
                "type": "string",
                "editable": True,
                "input_type": "text",
                "view": "text"
            }
        }
    }
}

# from jsonschema import validate, ValidationError

# # Define the JSON schema for validating your object specifications
# schema = {
#     "type": "object",
#     "patternProperties": {
#         "^.+$": {  # Applies to all properties at this level
#             "type": "object",
#             "properties": {
#                 "properties": {
#                     "type": "object",
#                     "patternProperties": {
#                         "^.+$": {
#                             "type": "object",
#                             "required": ["type", "editable", "view"],
#                             "properties": {
#                                 "type": {"type": "string"},
#                                 "input_type": {"type": "string"},
#                                 "options": {
#                                     "oneOf": [
#                                         {"type": "array"},
#                                         {"type": "object"}
#                                     ]
#                                 },
#                                 "object_type": {"type": "string"},
#                                 "view": {"type": "string"},
#                                 "editable": {"type": "boolean"},
#                                 "conditional_on": {"type": "string"},
#                                 "description": {"type": "string"},
#                                 "default": {}
#                             },
#                             "dependencies": {
#                                 "editable": {
#                                     "oneOf": [
#                                         {
#                                             "properties": {
#                                                 "editable": {"enum": [True]},
#                                                 "input_type": {"type": "string"}
#                                             }
#                                         },
#                                         {
#                                             "properties": {
#                                                 "editable": {"enum": [False]}
#                                             }
#                                         }
#                                     ]
#                                 },
#                                 "type": {
#                                     "oneOf": [
#                                         {
#                                             "properties": {
#                                                 "type": {"enum": ["object_id", "list_of_object_ids"]},
#                                                 "object_type": {"type": "string"},
#                                                 "view": {"type": "string", "pattern": ".*object_link.*|.*list_of_object_links.*"}
#                                             }
#                                         },
#                                         {
#                                             "properties": {
#                                                 "type": {"not": {"enum": ["object_id", "list_of_object_ids"]}}
#                                             }
#                                         }
#                                     ]
#                                 }
#                             },
#                             "additionalProperties": False
#                         }
#                     },
#                     "additionalProperties": False
#                 }
#             },
#             "required": ["properties"]
#         }
#     },
#     "additionalProperties": False
# }

# def validate_object_specifications(specs):
#     try:
#         validate(instance=specs, schema=schema)
#         print("Validation passed.")
#     except ValidationError as e:
#         print("Validation failed:", e.message)


