#!/usr/bin/env python3

import os
import sys
import argparse
import subprocess
import time
from datetime import datetime
import re

def extract_uuid(input_str):
    """Extract just the UUID from a string that might be a full NDEx URL"""
    # Match pattern for UUIDs in NDEx URLs
    uuid_pattern = r'(?:https?://(?:www\.)?ndexbio\.org/(?:v3/)?networks/)?([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})'
    match = re.search(uuid_pattern, input_str)
    if match:
        return match.group(1)
    return input_str  # Return original if no UUID pattern found

def run_command(command, description):
    """Run a command and print its output"""
    print(f"\n=== {description} ===")
    print(f"Running: {command}")
    
    start_time = time.time()
    process = subprocess.Popen(
        command, 
        shell=True, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    
    # Print output in real-time
    for line in process.stdout:
        print(line.strip())
    
    process.wait()
    execution_time = time.time() - start_time
    
    print(f"Command completed in {execution_time:.2f} seconds with exit code: {process.returncode}")
    return process.returncode

def main():
    parser = argparse.ArgumentParser(description='Test the full dengue hypothesis workflow')
    
    # Required arguments
    parser.add_argument('--uuid', type=str, required=True, 
                       help='NDEx UUID of the source dengue network')
    
    # Optional arguments
    parser.add_argument('--output-dir', type=str, default='./results', 
                       help='Output directory for results')
    parser.add_argument('--viral-proteins', type=str, nargs='+',
                       help='Specific viral proteins to process (names as they appear in the network)')
    parser.add_argument('--skip-propagation', action='store_true',
                      help='Skip the propagation step and just generate hypotheses')
    parser.add_argument('--propagation-uuids', type=str, nargs='+',
                      help='UUIDs of existing propagation networks to use for hypothesis generation')
    parser.add_argument('--n-hypotheses', type=int, default=2,
                      help='Number of hypotheses to generate per viral protein')
    parser.add_argument('--model-name', type=str, default='claude-3-7-sonnet-20250219',
                      help='Claude model name to use')
    
    args = parser.parse_args()
    
    # Extract UUID from input (in case it's a full URL)
    source_uuid = extract_uuid(args.uuid)
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Create timestamp for this run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = os.path.join(args.output_dir, f"run_{timestamp}")
    os.makedirs(run_dir, exist_ok=True)
    
    # Capture UUIDs of propagation networks
    propagation_uuids = []
    
    # Step 1: Run propagation if not skipped
    if not args.skip_propagation:
        propagation_command = [
            f"python propagate_from_viral_proteins_updated.py",
            f"--uuid {source_uuid}",
            f"--output-dir {run_dir}",
            "--type-scores type_scores.json",
            "--restart-prob 0.4",
            "--max-score 200",
            "--max-steps 500",
            "--allow-revisits",
            "--upload-to-ndex"
        ]
        
        # Add viral protein filter if specified
        if args.viral_proteins:
            # We can't directly filter in the script, but we'll check the results after
            print(f"Note: Will generate hypotheses only for viral proteins: {', '.join(args.viral_proteins)}")
        
        propagation_result = run_command(" ".join(propagation_command), "Running propagation from viral proteins")
        
        if propagation_result != 0:
            print("Error: Propagation failed. Exiting.")
            return
        
        # Extract UUIDs from the results file
        results_files = [f for f in os.listdir(run_dir) if f.startswith("viral_propagation_results_")]
        if results_files:
            import json
            latest_results_file = os.path.join(run_dir, sorted(results_files)[-1])
            
            with open(latest_results_file, 'r') as f:
                results = json.load(f)
                
            # Filter by viral proteins if needed
            if args.viral_proteins:
                filtered_networks = {}
                for protein, uuid in results.get('ndex_networks', {}).items():
                    if any(vp.lower() in protein.lower() for vp in args.viral_proteins):
                        filtered_networks[protein] = uuid
                        propagation_uuids.append(uuid)
                print(f"Filtered to {len(filtered_networks)} propagation networks for specified viral proteins")
            else:
                propagation_uuids = list(results.get('ndex_networks', {}).values())
            
            print(f"Found {len(propagation_uuids)} propagation network UUIDs")
        else:
            print("Warning: No propagation results file found")
    else:
        # Use provided propagation UUIDs
        if args.propagation_uuids:
            # Extract clean UUIDs from any provided strings
            propagation_uuids = [extract_uuid(uuid) for uuid in args.propagation_uuids]
            print(f"Using {len(propagation_uuids)} provided propagation network UUIDs")
        else:
            print("Error: Must provide --propagation-uuids when using --skip-propagation")
            return
    
    # Step 2: Generate hypotheses
    if propagation_uuids:
        # Make sure we're just using the clean UUIDs
        clean_uuids = [extract_uuid(uuid) for uuid in propagation_uuids]
        
        hypothesis_command = [
            f"python generate_hypotheses_updated.py",
            f"--uuids {' '.join(clean_uuids)}",
            f"--output-dir {run_dir}",
            f"--n-hypotheses {args.n_hypotheses}",
            "--llm-type Anthropic",
            f"--model-name {args.model_name}",
            "--max-tokens 4000",
            "--temperature 0.7"
        ]
        
        hypothesis_result = run_command(" ".join(hypothesis_command), "Generating hypotheses")
        
        if hypothesis_result != 0:
            print("Error: Hypothesis generation failed.")
            return
    else:
        print("No propagation networks available. Skipping hypothesis generation.")
    
    # Final summary
    print("\n=== Workflow Complete ===")
    print(f"Results directory: {run_dir}")
    
    # Look for the hypothesis network UUID
    uuid_files = [f for f in os.listdir(run_dir) if f.startswith("hypothesis_network_uuid_")]
    if uuid_files:
        with open(os.path.join(run_dir, uuid_files[-1]), 'r') as f:
            hypothesis_uuid = f.read().strip()
        print(f"Hypothesis network UUID: {hypothesis_uuid}")
        print(f"View in NDEx: https://www.ndexbio.org/viewer/networks/{hypothesis_uuid}")
    
if __name__ == "__main__":
    main()
