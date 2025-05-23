from jsonschema import validate, ValidationError

object_specifications = {
    # MARK:llm
    "llm": {
        "documentation": "The llm object represents a specific Large Language Model such as ChatGPT 4o or Claude 3.5 and  associated query properties such as temperature or seed.",
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
                "options": {"OpenAI": ["gpt-4o-mini-2024-07-18",
                                       "gpt-4o-2024-08-06",
                                       "gpt-4-turbo", 
                                       "gpt-4-turbo-2024-04-09",
                                       "gpt-3.5-turbo",
                                       "o1-preview",
                                       "o1-mini"
                                       ],
                            "Anthropic": ["claude-3-haiku-20240307", 
                                          "claude-3-sonnet-20240229", 
                                          "claude-3-opus-20240229", 
                                          "claude-3-5-sonnet-20240620"],
                            "Groq": ["llama-3.1-8b-instant",
                                     "llama-3.1-70b-versatile",
                                     "llama-3.1-405b-reasoning",
                                     "mixtral-8x7b-32768",
                                     "gemma-7b-it",
                                     "gemma2-9b-it",
                                     "llama3-8b-8192", 
                                     "llama3-70b-8192"],                                    
                            "GoogleAI": ["gemini-1.5-pro-latest", 
                                         "gemini-1.5-pro-001",  
                                         "gemini-1.5-flash-latest", 
                                         "gemini-1.5-flash-001", 
                                         "gemini-1.0-pro-latest", 
                                         "gemini-1.0-pro-001"], 
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
    # MARK:agent
    "agent": {
        "documentation": "An agent object serves as a scaffold to build queries for a linked llm object. Agent objects are referenced throughout the application whenever text generation occurs.",
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
                "view": "text"
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
        "documentation": "The dataset object holds information regarding a specific CSV file and its experimental context.",
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
        "documentation": "The analysis process generates hypotheses. The analysis_plan object provides a framework to automate hypothesis creation. Here agents are linked to a dataset, a biological context, and a number of hypotheses to generate. Upon executing an analysis_plan, LLMs will be queried, and an analysis_run and hypotheses will be automatically created.",
        "actions": ["create_analysis_run"],
        "properties": {
            "name": {
                "type": "string",
                "editable": True,
                "input_type": "text",
                "view": "text"
            },
            "agent_ids": {
                "type": "list_of_object_ids",
                "label": "agents",
                "input_type": "select_multiple_objects",
                "object_type": "agent",
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
            "n_hypotheses_per_agent": {
                "type": "int",
                "label": "hypotheses\nper agent",
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
        "documentation": "An analysis_run represents an instance of an analysis_plan being executed. Each analysis_run connects a group of hypotheses together that have similar attributes.",
        "properties": {
            "name": {
                "type": "string",
                "editable": True,
                "input_type": "text",
                "view": "text"
            },
            "agent_ids": {
                "type": "list_of_object_ids",
                "label": "agents",
                "object_type": "agent",
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
            "n_hypotheses_per_agent": {
                "type": "int",
                "editable": False,
                "input_type": "number",
                "view": "text",
                "label": "hypotheses\nper agent",
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
        "documentation": "Hypotheses are the product of the analysis process. Each hypothesis object is self-contained meaning that all the information necessary to reproduce the hypothesis is stored within it. Hypotheses are importable and exportable as a JSON file.",
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
            "agent_id": {
                "type": "object_id",
                "object_type": "agent",
                "label": "agent",
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
                "object_type": "analysis_run",
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
            },
            "agent_copy": {
                "type": "string",
                "label": "agent data copy",
                "editable": False,
                "view": "text",
                "collapsible": True
            },
            "llm_copy": {
                "type": "string",
                "label": "llm data copy",
                "editable": False,
                "view": "text",
                "collapsible": True
            },
            "dataset_copy": {
                "type": "string",
                "label": "dataset data copy",
                "editable": False,
                "view": "text",
                "collapsible": True
            },
        }
    },
    # MARK:reviewplan
    "review_plan": {
        "documentation": "The review_plan object provides a framework to automate review creation. Here, agents are linked to set of hypotheses. Upon executing a review_plan, LLMs will be queried, and a review_set and reviews will be automatically created.",
        "actions": ["create_review"],
        "properties": {
            "name": {
                "type": "string",
                "editable": True,
                "input_type": "text",
                "view": "text"
            },
            "agent_ids": {
                "type": "list_of_object_ids",
                "label": "agents",
                "input_type": "select_multiple_objects",
                "object_type": "agent",
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
        "documentation": "An review_set represents an instance of an review_plan being executed. Each review_set connects a group of reviews together that were generated at the same time.",
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
        "documentation": "Review objects are generated either by automated queries to LLMs or by human reviewers through the review portal. Reviews rank hypotheses by assigning each hypothesis a star rating. In addition to stars, comments justifying the rating for each hypothesis is provided. Reviews have a human friendly viewing mode to replicate the review portal.",
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
            "agent_id": {
                "type": "object_id",
                "label": "agent",
                "editable": False,
                "view": "object_link",
                "object_type": "agent"
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
        "documentation": "Users allow human reviewers to claim an identity before reviewing hypothesis.",
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
    },
    # MARK:judgment_space
    "judgment_space": {
        "documentation": "A JudgmentSpace enables the comparison and analysis of a group of human reviewers and Reviewer agents. The analysis is based on an ordered list of ReviewSet objects, each containing Reviews generated by the reviewer group.",
        # "actions": ["create_analysis_run"],
        "properties": {
            "name": {
                "type": "string",
                "editable": True,
                "input_type": "text",
                "view": "text"
            },
            "review_set_ids": {
                "type": "list_of_object_ids",
                "label": "review_sets",
                "input_type": "select_multiple_objects",
                "object_type": "review_set",
                "view": "list_of_object_links",
                "editable": True
            },
            "description": {
                "type": "string",
                "editable": True,
                "input_type": "textarea",
                "view": "text"
            },
            "visualizations": {
                "type": "string",
                "label": "visualizations",
                "editable": False,
                "view": "judgment_space_visualizations",
                "collapsible": True
            }
        }
    },
    "json": {
        "properties": {
            "name": {
                "label": "Name",
                "type": "string",
                "editable": True
            },
            "object_id": {
                "label": "ID",
                "type": "string",
                "editable": False
            },
            "created": {
                "label": "Created",
                "type": "string",
                "editable": False
            },
            "json": {
                "label": "JSON",
                "type": "object",
                "editable": False,
                "view": "json_tree",
                "collapsible": True
            },
            "markdown": {
                "label": "JSON Markdown",
                "type": "object",
                "editable": False,
                "view": "markdown",
                "collapsible": False
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


