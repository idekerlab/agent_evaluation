#!/usr/bin/env python3

"""
Test script to verify the refactored CX2 handling code works correctly.
"""

import os
import sys
import json
from pathlib import Path

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the refactored utilities
from scripts.utils.network_utils import (
    create_cx2_from_dict, 
    cx2_to_networkx, 
    networkx_to_cx2, 
    save_cx2_to_file,
    merge_visual_properties
)

def test_cx2_conversion():
    """Test CX2 conversion utilities with the test.cx2 file"""
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
    
    # Print some NetworkX information
    print(f"NetworkX node count: {G.number_of_nodes()}")
    print(f"NetworkX edge count: {G.number_of_edges()}")
    
    # Convert back to CX2
    print("Converting NetworkX back to CX2...")
    cx2_data_new = networkx_to_cx2(G)
    
    # Merge visual properties
    print("Merging visual properties...")
    merged_cx2 = merge_visual_properties(cx2_data_new, cx2_data)
    
    # Save the result
    output_path = str(Path(__file__).parent / 'test_output.cx2')
    print(f"Saving results to: {output_path}")
    save_cx2_to_file(merged_cx2, output_path)
    
    print("Test complete! Check if visual styles were preserved in the output file.")
    return True

if __name__ == "__main__":
    test_cx2_conversion()
