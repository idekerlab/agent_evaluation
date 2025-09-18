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
    
    # Handle the case when json_data is a single object, not a list
    if isinstance(json_data, dict):
        json_data = [json_data]
    
    # Process each element in the JSON data
    for element in json_data:
        # Add heading with the Index
        markdown.append(f"## Paragraph {element['Index']}")
        markdown.append("-------")
        
        # Create the table header
        markdown.append("| Text | Extracted Knowledge |")
        markdown.append("| --- | --- |")
        
        # Prepare the content for the right cell
        right_cell_content = []
        
        for result in element['Results']:
            right_cell_content.append(result['bel_statement'])
            right_cell_content.append("")  # Empty line
            right_cell_content.append(result['evidence'])
            right_cell_content.append("------")
        
        # Add annotations list
        right_cell_content.append("> Annotations:")
        for annotation in element['annotations']:
            right_cell_content.append(f"* {annotation['db']}:{annotation['id']} -- {annotation['entry_name']}")
        
        # Format the right cell content with proper newlines and escape pipe characters
        right_cell = "<br>".join(right_cell_content).replace("|", "\\|")
        
        # Add the table row with text and extracted knowledge
        markdown.append(f"| {element['text'].replace('|', '\\|')} | {right_cell} |")
        markdown.append("")  # Empty line between elements
    
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
        
        # Handle different JSON formats
        try:
            # Try as a JSON array
            if content.startswith('[') and content.endswith(']'):
                json_data = json.loads(content)
            else:
                # Try as a comma-separated series of JSON objects
                if content.endswith(','):
                    content = content[:-1]
                
                # Wrap in brackets to make it a valid JSON array
                if not content.startswith('['):
                    content = '[' + content
                if not content.endswith(']'):
                    content = content + ']'
                
                json_data = json.loads(content)
        except json.JSONDecodeError:
            # Try as a single JSON object
            try:
                if content.endswith(','):
                    content = content[:-1]
                json_data = json.loads(content)
            except json.JSONDecodeError as e:
                print(f"Error: Could not parse JSON: {e}")
                return
    
    # Convert JSON to markdown
    markdown_content = json_to_markdown(json_data)
    
    # Write the output markdown file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"Conversion completed. Markdown file saved to: {output_file}")
    
    # Print statistics
    if isinstance(json_data, list):
        print(f"Processed {len(json_data)} paragraphs.")
    else:
        print(f"Processed 1 paragraph with {len(json_data['Results'])} results and {len(json_data['annotations'])} annotations.")

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
