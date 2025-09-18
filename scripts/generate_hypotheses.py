#!/usr/bin/env python3

"""
Entry point script for generating hypotheses from viral protein propagation networks.
Uses the refactored modular code structure for network analysis.
"""

import os
import sys
import argparse
from typing import List, Dict, Any
from datetime import datetime

# Add the script directories to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the dengue-specific hypothesis generation module
from dengue.generate_hypotheses import generate_dengue_hypotheses, extract_uuid

def main():
    parser = argparse.ArgumentParser(description='Generate hypotheses from viral protein propagation networks')
    
    # Required arguments
    parser.add_argument('--uuids', type=str, nargs='+', required=True, 
                       help='NDEx UUIDs of propagation networks')
    
    # Optional arguments
    parser.add_argument('--output-dir', type=str, default='.', help='Output directory for results')
    parser.add_argument('--n-hypotheses', type=int, default=2, help='Number of hypotheses per viral protein')
    parser.add_argument('--llm-type', type=str, default='Anthropic', 
                        choices=['OpenAI', 'Anthropic', 'Groq', 'GoogleAI', 'LocalModel'],
                        help='Type of LLM to use')
    parser.add_argument('--model-name', type=str, default='claude-3-7-sonnet-20250219', 
                       help='Name of the model to use')
    parser.add_argument('--max-tokens', type=int, default=4000, help='Maximum tokens for LLM response')
    parser.add_argument('--temperature', type=float, default=0.7, help='Temperature for LLM generation')
    parser.add_argument('--seed', type=int, default=42, help='Random seed for reproducibility')
    parser.add_argument('--no-upload', dest='upload_network', action='store_false',
                       help='Disable uploading hypothesis network to NDEx')
    parser.set_defaults(upload_network=True)
    
    args = parser.parse_args()
    
    # Call the dengue-specific hypothesis generation function
    hypotheses = generate_dengue_hypotheses(
        ndex_uuids=args.uuids,
        output_dir=args.output_dir,
        n_hypotheses=args.n_hypotheses,
        llm_type=args.llm_type,
        model_name=args.model_name,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
        seed=args.seed,
        upload_network=args.upload_network
    )
    
    # Exit with success if we generated at least one hypothesis
    if hypotheses and len(hypotheses) > 0:
        return 0
    else:
        # Exit with error code if no hypotheses were generated
        return 1

if __name__ == "__main__":
    sys.exit(main())
