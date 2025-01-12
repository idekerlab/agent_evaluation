import json
import csv
from io import StringIO
from typing import Dict, List
import decimal
from decimal import Decimal, ROUND_HALF_UP

from fastapi import HTTPException
from jsonschema import validate, ValidationError

from app.sqlite_database import SqliteDatabase

class FormSubmissionError(Exception):
    """Custom exception for form submission errors."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

def format_numeric_values(data: List[List[str]]) -> List[List[str]]:
    """Format numeric values in CSV data to 2 decimal places."""
    for i, row in enumerate(data):
        for j, value in enumerate(row):
            # Check if the value is a numeric string, including negative numbers
            if value.lstrip('-').replace('.', '', 1).isdigit():
                try:
                    value_decimal = Decimal(value)
                    data[i][j] = str(value_decimal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
                except decimal.InvalidOperation:
                    continue
    return data

def get_default_properties(object_type: str, specifications: Dict) -> Dict:
    """Get default properties for an object type from specifications."""
    default_properties = {}
    for field_name, field_spec in specifications[object_type]["properties"].items():
        default_properties[field_name] = field_spec.get("default", "")
    return default_properties

def generate_form(db: SqliteDatabase, object_type: str, specifications: Dict, obj_properties: Dict) -> List[Dict]:
    """Generate form fields based on object type and properties."""
    fields = []

    # Ensure the object_type exists in the specifications
    if object_type not in specifications:
        print(f"Error: '{object_type}' is not a valid object type in specifications.")
        return fields

    # Get the specific specifications for the given object_type
    object_spec = specifications[object_type]

    for field_name, field_spec in object_spec["properties"].items():
        try:
            if (field_spec.get("input_type", "") == "select_single_object" 
                or field_spec.get("input_type", "") == "select_multiple_objects"):
                field_object_type = field_spec.get("object_type", "")
                field_objects = db.find(field_object_type)
                option_dicts = []
                for field_object in field_objects:
                    field_obj_id = field_object['object_id']
                    field_obj_name = field_object['properties']['name'] if 'name' in field_object['properties'] else "unnamed"
                    field_obj_name = field_obj_name if len(field_obj_name) > 0 else "unnamed"
                    option_label = f"({field_obj_name}) {field_obj_id}"
                    option_dicts.append({"label": option_label, "value": field_obj_id})
                    
                field_spec["options"] = option_dicts

            field = {
                "name": field_name,
                "type": field_spec.get("type", "text"),  # Default to "text"
                "label": field_spec.get("label") or field_name.replace('_', ' '),
                "input_type": field_spec.get("input_type", "text"),
                "value": obj_properties.get(field_name, field_spec.get("default", "")),
                "options": field_spec.get("options", []),
                "editable": field_spec["editable"],
                "view": field_spec.get("view", "text"),
                "conditional_on": field_spec.get("conditional_on", None),
                "min": field_spec.get("min", ""),
                "max": field_spec.get("max", ""),
                "step": field_spec.get("step", ""),
                "regex": field_spec.get("regex", ""),
                "regex_description": field_spec.get("regex_description", "")
            }
            fields.append(field)
        except KeyError as e:
            print(f"Error in field specification for '{field_name}': missing key {e}")
        except Exception as e:
            print(f"Unexpected error in field specification for '{field_name}': {e}")

    return fields

async def handle_form_submission(form_data: Dict, object_type: str, db: SqliteDatabase):
    """Handle form submission including file uploads and validation."""
    try:
        # Extract CSV file from form data
        csv_file = form_data.pop('data', None) if object_type == "dataset" else None
        if csv_file:
            print("File:", csv_file)
            if (csv_file != "undefined"):
                if isinstance(csv_file, StringIO):
                    # This is the case when uploading a csv file into a dataset object
                    csv_content = csv_file.read()
                else:
                    # This is the case when importing a dataset object
                    csv_content = csv_file
                print("Content", csv_content)
                
                # Process the CSV content
                csv_data = StringIO(csv_content)
                reader = csv.reader(csv_data)
                rows = list(reader)

                # Format numeric values in CSV content
                formatted_rows = format_numeric_values(rows)

                # Convert back to CSV string
                output = StringIO()
                writer = csv.writer(output)
                writer.writerows(formatted_rows)
                form_data['data'] = output.getvalue()
        
        if form_data.get("object_id"):
            db.update(form_data["object_id"], form_data)
        else:
            raise Exception("No object_id provided in form data")
    except ValidationError as e:
        raise FormSubmissionError(f"Form data validation failed: {e.message}")
    except Exception as e:
        raise FormSubmissionError(f"An error occurred while processing the form: {e}")
