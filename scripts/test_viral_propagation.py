#!/usr/bin/env python3

"""
Test script to verify the refactored viral propagation code works correctly.
"""

import os
import sys
import json
from pathlib import Path
import time

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the refactored utilities
from scripts.utils.network_utils import (
    create_cx2_from_dict, 
    cx2_to_networkx, 
    save_cx2_to_file
)

# Import the viral propagation module
from scripts.dengue.viral_propagation import (
    identify_viral_proteins,
    propagate_from_viral_protein
)

def test_viral_propagation():
    """Test viral propagation with the test CX2 file"""
    # Path to the test CX2 file (relative to project root)
    test_cx2_path = str(Path(__file__).parent.parent / 'test.cx2')
    print(f"Loading test CX2 file from: {test_cx2_path}")
    
    # Load the test CX2 data
    with open(test_cx2_path, 'r') as f:
        cx2_data = json.load(f)
    
    # Convert CX2 data to a CX2Network object
    print("Converting CX2 data to CX2Network object...")
    cx2_network = create_cx2_from_dict(cx2_data)
    
    # Print some basic information about the network
    print(f"Network name: {cx2_network.get_name()}")
    print(f"Node count: {len(cx2_network.get_nodes())}")
    print(f"Edge count: {len(cx2_network.get_edges())}")
    
    # Convert to NetworkX
    print("Converting CX2Network to NetworkX...")
    G = cx2_to_networkx(cx2_network)
    
    # For testing, designate a node as viral protein
    print("Setting up viral protein for propagation...")
    # Get the first node
    first_node_id = list(G.nodes())[0]
    # Set the first node as a viral protein
    G.nodes[first_node_id]['viral_protein'] = True
    G.nodes[first_node_id]['type'] = 'viral'
    
    # Identify viral proteins
    viral_proteins = identify_viral_proteins(G)
    print(f"Identified viral proteins: {viral_proteins}")
    
    # Set up parameters for propagation
    restart_prob = 0.2
    max_score = 10.0
    max_steps = 50
    type_score_dict = {"protein": 1.0, "viral": 0.5}
    default_score = 0.75
    
    # Run propagation
    print("Running viral propagation...")
    start_time = time.time()
    cx2_result, results = propagate_from_viral_protein(
        G, 
        cx2_network,
        viral_proteins[0][0], 
        viral_proteins[0][1],
        restart_prob=restart_prob,
        max_score=max_score,
        max_steps=max_steps,
        type_score_dict=type_score_dict,
        default_score=default_score,
        allow_revisits=True,
        include_all_nodes=True
    )
    execution_time = time.time() - start_time
    
    # Print propagation results
    print(f"Propagation completed in {execution_time:.2f} seconds")
    print(f"Visited {len(results['node_weights'])} nodes")
    
    # Save the propagation result
    output_path = str(Path(__file__).parent / 'propagation_result.cx2')
    print(f"Saving propagation result to: {output_path}")
    save_cx2_to_file(cx2_result, output_path)
    
    print("Test complete! Check propagation_result.cx2 to verify visual styles were preserved.")
    return True

if __name__ == "__main__":
    test_viral_propagation()
