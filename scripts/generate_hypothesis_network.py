#!/usr/bin/env python3

import os
import sys
import json
from datetime import datetime
from typing import List, Dict, Any

# Add the parent directory to the path so we can import from the scripts directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.generate_hypotheses import (
    LLMWrapper, 
    load_from_ndex, 
    analyze_network, 
    generate_hypotheses, 
    create_hypothesis_network
)

def main():
    """
    Generate a hypothesis network from a list of NDEx UUIDs and save it to a file.
    """
    # List of UUIDs to process
    uuids = [
        "faa974fc-ff5f-11ef-b81d-005056ae3c32",
        # Add more UUIDs here as needed
    ]
    
    print(f"Processing {len(uuids)} networks...")
    
    # Create timestamp for output filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create LLM wrapper (using default values from generate_hypotheses.py)
    llm_wrapper = LLMWrapper(
        llm_type="Anthropic",
        model_name="claude-3-7-sonnet-20250219",
        max_tokens=4000,
        seed=42,
        temperature=0.7
    )
    
    # Store all hypotheses from all viral proteins
    all_hypotheses = []
    all_network_stats = {}
    
    # Number of hypotheses to generate per viral protein
    n_hypotheses = 2
    
    # Process each viral protein network
    for i, uuid in enumerate(uuids):
        print(f"\nProcessing network {i+1}/{len(uuids)}: {uuid}")
        
        try:
            # Load network from NDEx
            G, network_name, network_attrs = load_from_ndex(uuid)
            print(f"Loaded network '{network_name}' with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
            
            # Analyze network
            print("Analyzing network...")
            network_stats = analyze_network(G, network_attrs)
            
            # Store network stats for later reference
            viral_protein = network_stats['viral_protein']['name']
            all_network_stats[viral_protein] = network_stats
            
            # Generate hypotheses for this viral protein
            print(f"Generating {n_hypotheses} hypotheses for {viral_protein}...")
            hypotheses = generate_hypotheses(network_stats, llm_wrapper, n_hypotheses)
            
            # Add hypotheses to the overall list
            all_hypotheses.extend(hypotheses)
            
            # Save individual protein hypotheses to file
            protein_filename = f"hypotheses_{viral_protein}_{timestamp}.json"
            protein_filepath = os.path.join(os.path.dirname(__file__), protein_filename.replace(" ", "_"))
            
            with open(protein_filepath, 'w') as f:
                json.dump(hypotheses, f, indent=2)
            
            print(f"Saved {len(hypotheses)} hypotheses for {viral_protein} to {protein_filepath}")
            
        except Exception as e:
            print(f"Error processing network {uuid}: {str(e)}")
    
    # Save all hypotheses to file
    all_hypotheses_filename = f"all_hypotheses_{timestamp}.json"
    all_hypotheses_filepath = os.path.join(os.path.dirname(__file__), all_hypotheses_filename)
    
    with open(all_hypotheses_filepath, 'w') as f:
        json.dump(all_hypotheses, f, indent=2)
    
    print(f"\nSaved {len(all_hypotheses)} total hypotheses to {all_hypotheses_filepath}")
    
    # Create hypothesis network
    print("\nCreating hypothesis network...")
    hypothesis_network = create_hypothesis_network(all_hypotheses)
    
    # Save CX2 network to file
    cx2_network_filename = f"hypothesis_network_{timestamp}.cx2"
    cx2_network_filepath = os.path.join(os.path.dirname(__file__), cx2_network_filename)
    
    with open(cx2_network_filepath, 'w') as f:
        json.dump(hypothesis_network.to_cx2(), f, indent=2)
    
    print(f"Saved hypothesis network to {cx2_network_filepath}")
    
    # Display summary of generated hypotheses
    print("\nGenerated Hypotheses Summary:")
    for viral_protein, stats in all_network_stats.items():
        protein_hypotheses = [h for h in all_hypotheses if h['viral_protein'] == viral_protein]
        print(f"\n{viral_protein}: {len(protein_hypotheses)} hypotheses")
        
        for h in protein_hypotheses:
            print(f"  [{h['id']}] {h['title']} (Confidence: {h['confidence']}/5)")
    
    print(f"\nTotal hypotheses: {len(all_hypotheses)}")

if __name__ == "__main__":
