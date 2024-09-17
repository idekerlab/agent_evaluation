import json
import re

def parse_text_to_json(text):
    # Use regex to extract the JSON part of the text
    json_match = re.search(r'{.*}', text, re.DOTALL)
    
    if not json_match:
        raise ValueError("No JSON structure found in the provided text.")
    
    # Extract the JSON string
    json_str = json_match.group(0)
    
    # Parse the JSON string into a Python dictionary
    try:
        parsed_data = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Error decoding JSON: {e}")
    
    return parsed_data