"""Helper module to convert JSON structures to markdown text."""
from typing import Union, Any

def json_to_markdown(data: Union[dict, list], level: int = 0) -> str:
    """Convert a JSON structure to markdown text.
    
    First two levels of nesting are reflected as "##" and "###" headings.
    Deeper levels use bullet points with increasing indentation.
    
    Args:
        data: The JSON structure (dict or list) to convert
        level: The current nesting level (used internally for recursion)
        
    Returns:
        str: The markdown representation of the JSON structure
    """
    result = []
    
    if isinstance(data, dict):
        for key, value in data.items():
            # First two levels use headings
            if level == 0:
                result.append(f"## {key}")
            elif level == 1:
                result.append(f"### {key}")
            else:
                # Deeper levels use bullet points with indentation
                indent = "  " * (level - 2)  # 2 spaces per level after heading levels
                result.append(f"{indent}* {key}")
                
            # Handle the value
            if isinstance(value, (dict, list)):
                result.append(json_to_markdown(value, level + 1))
            else:
                # For simple values, add them inline or as bullet points
                if level <= 1:  # For heading levels
                    result.append(str(value))
                else:
                    indent = "  " * (level - 1)
                    result.append(f"{indent}  - {value}")
                    
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                result.append(json_to_markdown(item, level))
            else:
                # Simple list items as bullet points
                indent = "  " * (level - 2 if level > 1 else 0)
                result.append(f"{indent}* {item}")
                
    return "\n".join(result)
