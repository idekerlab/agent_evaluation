#!/usr/bin/env python3
"""
JSON to Markdown Converter

This script reads a JSON file containing knowledge extraction results and
converts it into a nicely formatted markdown file according to the specified format.
"""

import json
import argparse
from pathlib import Path

def json_to_markdown(json_data):
    """
    Convert JSON data to markdown format.
    
    Args:
        json_data (dict or list): JSON data containing knowledge extraction results
        
    Returns:
        str: Formatted markdown content
    """
    markdown = []
    
    # Handle the top-level structure - check for the LLM_extractions key
    if isinstance(json_data, dict) and "LLM_extractions" in json_data:
        # Extract the array from the LLM_extractions key
        elements = json_data["LLM_extractions"]
    elif isinstance(json_data, list):
        # Already a list
        elements = json_data
    else:
        # Single object, wrap in list
        elements = [json_data]
    
    # Process each element in the JSON data
    for element in elements:
        # Add heading with the Index
        markdown.append(f"## Paragraph {int(element['Index']) + 1}")

        # Add a blank line
        markdown.append("")

        # Add the text content on a new line
        markdown.append(element['text'])
        
        # Add a blank line
        markdown.append("")
        
        # Add annotations
        for annotation in element['annotations']:
            markdown.append(f"{annotation['db']}:{annotation['id']} = **{annotation['entry_name']}**     ")
        
        # Add a blank line
        markdown.append("")

        # Add the extracted knowledge (BEL statements and evidence)
        for result in element['Results']:
            markdown.append(f"*{result['evidence']}*")
            markdown.append(f"- `{result['bel_statement']}`")
        
            # Add a blank line
            markdown.append("")

        # Add empty line between paragraphs
        markdown.append("")
        markdown.append("")
    
    return "\n".join(markdown)

def process_json_file(input_file, output_file):
    """
    Process a JSON file and convert it to markdown
    
    Args:
        input_file (str): Path to input JSON file
        output_file (str): Path to output markdown file
    """
    # Read the input JSON file
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read().strip()
        
        # Parse the JSON
        try:
            json_data = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"Error: Could not parse JSON: {e}")
            return
    
    # Convert JSON to markdown
    markdown_content = json_to_markdown(json_data)
    
    # Write the output markdown file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    # Determine the number of elements processed
    if isinstance(json_data, dict) and "LLM_extractions" in json_data:
        num_elements = len(json_data["LLM_extractions"])
    elif isinstance(json_data, list):
        num_elements = len(json_data)
    else:
        num_elements = 1
    
    print(f"Conversion completed. Markdown file saved to: {output_file}")
    print(f"Processed {num_elements} paragraphs.")

def main():
    parser = argparse.ArgumentParser(description='Convert JSON knowledge extraction to markdown format')
    parser.add_argument('input_file', help='Input JSON file path')
    parser.add_argument('--output', '-o', help='Output markdown file path')
    
    args = parser.parse_args()
    
    # Default output file is input name with .md extension
    if not args.output:
        input_path = Path(args.input_file)
        output_path = input_path.with_suffix('.md')
    else:
        output_path = args.output
    
    process_json_file(args.input_file, output_path)

if __name__ == "__main__":
    main()
