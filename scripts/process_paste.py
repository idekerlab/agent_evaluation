#!/usr/bin/env python3
"""
Process Paste Script

A simple script to process the paste.txt file in the current directory
"""

import json
import os
import sys
from pathlib import Path

# Import the json_to_markdown function from the main script
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from json_to_markdown import json_to_markdown

def process_paste_file(paste_file="paste.txt", output_file=None):
    """
    Process a paste file and convert it to markdown
    
    Args:
        paste_file (str): Path to paste file (default: paste.txt)
        output_file (str): Path to output markdown file (default: paste.md)
    """
    if not output_file:
        output_file = Path(paste_file).with_suffix('.md')
    
    try:
        # Read the paste file
        with open(paste_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        # Remove trailing comma if present
        if content.endswith(','):
            content = content[:-1]
        
        # Parse the JSON
        json_data = json.loads(content)
        
        # Convert to markdown
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
            
    except FileNotFoundError:
        print(f"Error: File '{paste_file}' not found.")
    except json.JSONDecodeError as e:
        print(f"Error: Could not parse JSON: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Process paste.txt and convert to markdown')
    parser.add_argument('--input', '-i', default='paste.txt', help='Input paste file path (default: paste.txt)')
    parser.add_argument('--output', '-o', help='Output markdown file path')
    
    args = parser.parse_args()
    
    process_paste_file(args.input, args.output)
