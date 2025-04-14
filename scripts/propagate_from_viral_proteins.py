#!/usr/bin/env python3

"""
Entry point script for propagating from viral proteins in a dengue network.
Uses the refactored modular code structure for network analysis.
"""

import os
import sys
import argparse
from typing import List, Dict, Any
from datetime import datetime

# Add the script directories to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the dengue-specific viral propagation module
from dengue.viral_propagation import run_viral_propagation

def main():
    parser = argparse.ArgumentParser(description='Propagate from all viral proteins in a dengue network')
    
    # Required arguments
    parser.add_argument('--uuid', type=str, required=True, help='NDEx UUID of the dengue network')
    
    # Optional arguments
    parser.add_argument('--output-dir', type=str, default='.', help='Output directory for results')
    parser.add_argument('--type-scores', type=str, default='type_scores.json', 
                      help='JSON file with node type to score mapping')
    parser.add_argument('--restart-prob', type=float, default=0.2, help='Restart probability')
    parser.add_argument('--max-score', type=float, default=10.0, help='Maximum cumulative score')
    parser.add_argument('--max-steps', type=int, default=100, help='Maximum steps per propagation')
    parser.add_argument('--default-score', type=float, default=1.0, help='Default node score')
    parser.add_argument('--allow-revisits', action='store_true', help='Allow revisiting nodes')
    parser.add_argument('--include-all-nodes', action='store_true', 
                      help='Include all nodes in output network (default: only include nodes with propagation weights)')
    parser.add_argument('--upload-to-ndex', action='store_true', help='Upload networks to NDEx')
    parser.add_argument('--save-cx2-files', action='store_true', help='Save networks as CX2 files locally')
    parser.add_argument('--dry-run', action='store_true', help='Identify viral proteins but do not run propagation')
    parser.add_argument('--specific-proteins', type=str, nargs='+', 
                      help='Specific viral proteins to process (by ID or name)')
    
    args = parser.parse_args()
    
    # Check if specific proteins were provided
    process_all_proteins = not bool(args.specific_proteins)
    
    # Call the dengue-specific viral propagation function
    results = run_viral_propagation(
        ndex_uuid=args.uuid,
        output_dir=args.output_dir,
        type_scores_file=args.type_scores,
        restart_prob=args.restart_prob,
        max_score=args.max_score,
        max_steps=args.max_steps,
        default_score=args.default_score,
        allow_revisits=args.allow_revisits,
        include_all_nodes=args.include_all_nodes,
        upload_networks=args.upload_to_ndex,
        save_cx2_files=args.save_cx2_files,
        process_all_proteins=process_all_proteins,
        specific_proteins=args.specific_proteins
    )
    
    # Exit with success if we got results
    if results and not isinstance(results, dict) or ('error' not in results):
        return 0
    else:
        # Exit with error code if something went wrong
        return 1

if __name__ == "__main__":
    sys.exit(main())
