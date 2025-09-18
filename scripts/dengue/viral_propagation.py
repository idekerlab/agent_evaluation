#!/usr/bin/env python3

"""
Dengue-specific viral protein propagation module.
"""

import sys
import os
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional, Union
import networkx as nx
import ndex2.client as nc2
from ndex2.cx2 import CX2Network, RawCX2NetworkFactory

# Add parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from algorithms.propagation import score_limited_random_walk_with_restart, score_multi_seed_random_walk
from algorithms.propagation import create_propagation_network
from utils.network_utils import cx2_to_networkx, save_cx2_to_file

# Import app utilities
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from app.ndex_utils import get_ndex_client, get_complete_network
from app.config import load_api_keys

def identify_viral_proteins(G: nx.Graph) -> List[Tuple[str, str]]:
    """
    Identify viral proteins in the network
    
    Args:
        G: NetworkX graph
        
    Returns:
        List of tuples (node_id, name) for viral proteins
    """
    viral_proteins = []
    
    for node_id, attrs in G.nodes(data=True):
        # Check if this is a viral protein by looking at viral_protein property or type
        is_viral = attrs.get('viral_protein', False) or attrs.get('type', '') == 'viral'
        
        if is_viral:
            # Get name from attributes
            name = attrs.get('name', '')
            if not name:
                name = attrs.get('GeneSymbol', str(node_id))
            
            viral_proteins.append((node_id, name))
    
    return viral_proteins

def propagate_from_viral_protein(
    G: nx.Graph,
    original_cx2: Union[CX2Network, Dict, List],
    viral_protein_id: str,
    viral_protein_name: str,
    restart_prob: float = 0.2,
    max_score: float = 10.0,
    max_steps: int = 100,
    type_score_dict: Optional[Dict[str, float]] = None,
    default_score: float = 1.0,
    allow_revisits: bool = True,
    include_all_nodes: bool = False
) -> Tuple[Dict, Dict[str, Any]]:
    """
    Propagate from a viral protein and create network with results.
    
    Args:
        G: NetworkX graph
        original_cx2: Original CX2Network (or CX2 data as dict/list)
        viral_protein_id: ID of the viral protein used as seed node
        viral_protein_name: Name of the viral protein
        restart_prob: Restart probability
        max_score: Maximum cumulative score
        max_steps: Maximum steps per propagation
        type_score_dict: Dictionary mapping node types to scores
        default_score: Default node score
        allow_revisits: Allow revisiting nodes
        include_all_nodes: If True, include all nodes, otherwise only nodes with weights
        
    Returns:
        Tuple of (Enhanced CX2 network as dict, propagation results)
    """
    # Run propagation
    start_time = time.time()
    results = score_limited_random_walk_with_restart(
        G,
        viral_protein_id,
        restart_prob=restart_prob,
        max_cumulative_score=max_score,
        max_steps=max_steps,
        type_score_dict=type_score_dict,
        default_score=default_score,
        allow_revisits=allow_revisits
    )
    execution_time = time.time() - start_time
    results['execution_time'] = execution_time
    
    # Create network with propagation results
    network_name = f"Propagation from {viral_protein_name}"
    cx2_data = create_propagation_network(
        original_cx2,
        results['node_weights'],
        [viral_protein_id],
        include_all_nodes=include_all_nodes,
        network_name=network_name
    )
    
    # Use the standard ndex2 library to update network attributes
    from utils.network_utils import create_cx2_from_dict
    cx2_network = create_cx2_from_dict(cx2_data)
    
    # Add viral protein specific attributes
    cx2_network.set_network_attributes({"viral_protein_id": viral_protein_id})
    cx2_network.set_network_attributes({"viral_protein_name": viral_protein_name})
    
    # Convert back to CX2 data format
    return cx2_network.to_cx2(), results

def propagate_from_multiple_viral_proteins(
    G: nx.Graph,
    original_cx2: Union[CX2Network, Dict, List],
    viral_proteins: List[Tuple[str, str]],
    restart_prob: float = 0.2,
    max_score: float = 10.0,
    max_steps: int = 100,
    type_score_dict: Optional[Dict[str, float]] = None,
    default_score: float = 1.0,
    allow_revisits: bool = True,
    include_all_nodes: bool = False,
    seed_selection_strategy: str = 'uniform'
) -> Tuple[Dict, Dict[str, Any]]:
    """
    Propagate from multiple viral proteins and create a combined network.
    
    Args:
        G: NetworkX graph
        original_cx2: Original CX2Network (or CX2 data as dict/list)
        viral_proteins: List of (node_id, name) tuples for viral proteins
        restart_prob: Restart probability
        max_score: Maximum cumulative score
        max_steps: Maximum steps per propagation
        type_score_dict: Dictionary mapping node types to scores
        default_score: Default node score
        allow_revisits: Allow revisiting nodes
        include_all_nodes: If True, include all nodes, otherwise only nodes with weights
        seed_selection_strategy: Strategy for selecting seed nodes during restarts
        
    Returns:
        Tuple of (Enhanced CX2 network as dict, propagation results)
    """
    # Extract just the node IDs for propagation
    viral_protein_ids = [vp[0] for vp in viral_proteins]
    viral_protein_names = [vp[1] for vp in viral_proteins]
    
    # Run multi-seed propagation
    start_time = time.time()
    results = score_multi_seed_random_walk(
        G,
        viral_protein_ids,
        restart_prob=restart_prob,
        max_cumulative_score=max_score,
        max_steps=max_steps,
        type_score_dict=type_score_dict,
        default_score=default_score,
        allow_revisits=allow_revisits,
        seed_selection_strategy=seed_selection_strategy
    )
    execution_time = time.time() - start_time
    results['execution_time'] = execution_time
    
    # Create network with propagation results
    protein_names_str = ", ".join(viral_protein_names[:3])
    if len(viral_protein_names) > 3:
        protein_names_str += f" and {len(viral_protein_names) - 3} more"
    
    network_name = f"Propagation from {protein_names_str}"
    cx2_data = create_propagation_network(
        original_cx2,
        results['node_weights'],
        viral_protein_ids,
        include_all_nodes=include_all_nodes,
        network_name=network_name
    )
    
    # Add viral proteins list as an attribute using the standard library
    from utils.network_utils import create_cx2_from_dict
    cx2_network = create_cx2_from_dict(cx2_data)
    
    # Create JSON representation of viral proteins
    viral_proteins_json = json.dumps([
        {"id": vp_id, "name": vp_name} for vp_id, vp_name in viral_proteins
    ])
    
    # Set the attribute using the CX2Network API
    cx2_network.set_network_attributes({"viral_proteins": viral_proteins_json})
    
    # Convert back to CX2 data format
    return cx2_network.to_cx2(), results

def upload_to_ndex(cx2_data: Union[Dict, List, CX2Network]) -> str:
    """
    Upload a CX2 network to NDEx
    
    Args:
        cx2_data: CX2 network data (as dict, list, or CX2Network object)
        
    Returns:
        UUID of the uploaded network
    """
    # Get NDEx client
    client = get_ndex_client()
    
    # Convert to CX2Network object if needed
    if isinstance(cx2_data, CX2Network):
        cx2_data = cx2_data.to_cx2()
    
    # Upload to NDEx using the standard client method
    response = client.save_new_cx2_network(cx2_data)
    return response

def run_viral_propagation(
    ndex_uuid: str,
    output_dir: str = '.',
    type_scores_file: str = None,
    restart_prob: float = 0.2,
    max_score: float = 10.0,
    max_steps: int = 100,
    default_score: float = 1.0,
    allow_revisits: bool = True,
    include_all_nodes: bool = False,
    upload_networks: bool = False,
    save_cx2_files: bool = False,
    process_all_proteins: bool = True,
    specific_proteins: List[str] = None
) -> Dict[str, Any]:
    """
    Main entry point for viral protein propagation
    
    Args:
        ndex_uuid: NDEx UUID of the dengue network
        output_dir: Output directory for results
        type_scores_file: JSON file with node type to score mapping
        restart_prob: Restart probability
        max_score: Maximum cumulative score
        max_steps: Maximum steps per propagation
        default_score: Default node score
        allow_revisits: Allow revisiting nodes
        include_all_nodes: Include all nodes in output network
        upload_networks: Upload networks to NDEx
        process_all_proteins: Process all viral proteins
        specific_proteins: List of specific viral protein IDs/names to process
        
    Returns:
        Dictionary with propagation results
    """
    # Import utility functions from network_utils
    from utils.network_utils import cx2_to_networkx, save_cx2_to_file
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Load type scores if provided
    type_score_dict = None
    if type_scores_file and os.path.exists(type_scores_file):
        with open(type_scores_file, 'r') as f:
            print(f"Loading type scores from {type_scores_file}")
            type_score_dict = json.load(f)
    
    # Load network from NDEx
    print(f"Loading network {ndex_uuid} from NDEx...")
    network_data = get_complete_network(ndex_uuid)
    network_name = network_data.get('name', f"network-{ndex_uuid[:8]}")
    print(f"Loaded network '{network_name}' with {network_data['nodeCount']} nodes and {network_data['edgeCount']} edges")
    
    # Get original CX2 network using standard ndex2 library approach
    client = get_ndex_client()
    response = client.get_network_as_cx2_stream(ndex_uuid)
    cx2_raw_data = response.json()
    
    # Create CX2Network object using factory
    factory = RawCX2NetworkFactory()
    original_cx2 = factory.get_cx2network(cx2_raw_data)
    
    # Convert to NetworkX for propagation using our utility
    G = cx2_to_networkx(original_cx2)
    
    # Identify viral proteins
    print("Identifying viral proteins...")
    viral_proteins = identify_viral_proteins(G)
    print(f"Found {len(viral_proteins)} viral proteins:")
    for node_id, name in viral_proteins:
        print(f"  {name} (ID: {node_id})")
    
    # Filter to specific proteins if requested
    if not process_all_proteins and specific_proteins:
        filtered_proteins = []
        for node_id, name in viral_proteins:
            if node_id in specific_proteins or name in specific_proteins:
                filtered_proteins.append((node_id, name))
        
        if not filtered_proteins:
            print(f"Warning: None of the specified proteins {specific_proteins} were found")
            print("Available proteins:")
            for node_id, name in viral_proteins:
                print(f"  {name} (ID: {node_id})")
            return {"error": "No specified proteins found"}
        
        viral_proteins = filtered_proteins
        print(f"Filtered to {len(viral_proteins)} specified viral proteins")
    
    # Create output file to store results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = os.path.join(output_dir, f"viral_propagation_results_{timestamp}.json")
    
    # Initialize results storage
    all_results = {
        'source_network': {
            'uuid': ndex_uuid,
            'name': network_name
        },
        'propagation_parameters': {
            'restart_prob': restart_prob,
            'max_score': max_score,
            'max_steps': max_steps,
            'default_score': default_score,
            'allow_revisits': allow_revisits,
            'include_all_nodes': include_all_nodes,
            'type_scores': type_score_dict
        },
        'viral_proteins': {},
        'ndex_networks': {}
    }
    
    # Run propagation for each viral protein
    total_start_time = time.time()
    
    for i, (node_id, name) in enumerate(viral_proteins):
        print(f"\nProcessing viral protein {i+1}/{len(viral_proteins)}: {name} (ID: {node_id})")
        
        try:
            # Run propagation and create network
            # Pass both the original CX2Network object and the raw data
            # to ensure visual styles are preserved
            enhanced_network, results = propagate_from_viral_protein(
                G,
                original_cx2,  # Using the CX2Network object
                node_id,
                name,
                restart_prob=restart_prob,
                max_score=max_score,
                max_steps=max_steps,
                type_score_dict=type_score_dict,
                default_score=default_score,
                allow_revisits=allow_revisits,
                include_all_nodes=include_all_nodes
            )
            
            # Store results
            all_results['viral_proteins'][name] = {
                'node_id': node_id,
                'walk_stats': results['walk_stats'],
                'execution_time': results['execution_time']
            }
            
            print(f"  Propagation completed in {results['execution_time']:.2f} seconds")
            print(f"  Walk stats: {results['walk_stats']}")
            
            # Upload to NDEx if requested
            if upload_networks:
                print("  Uploading network to NDEx...")
                uuid = upload_to_ndex(enhanced_network)
                print(f"  Upload successful. New network UUID: {uuid}")
                
                # Store network UUID
                all_results['ndex_networks'][name] = uuid
                
            # Save CX2 files if requested
            if save_cx2_files:
                # Create a filename based on the viral protein name
                sanitized_name = name.replace(' ', '_').replace('/', '_')
                cx2_file_path = os.path.join(output_dir, f"{sanitized_name}_propagation_{timestamp}.cx2")
                print(f"  Saving CX2 network to file...")
                save_cx2_to_file(enhanced_network, cx2_file_path)
                
                # Store file path in results
                if 'cx2_files' not in all_results:
                    all_results['cx2_files'] = {}
                all_results['cx2_files'][name] = cx2_file_path
            
            # Save results periodically
            with open(results_file, 'w') as f:
                json.dump(all_results, f, indent=2)
            
        except Exception as e:
            print(f"Error processing viral protein {name}: {str(e)}")
            all_results['viral_proteins'][name] = {
                'node_id': node_id,
                'error': str(e)
            }
    
    # Calculate total execution time
    total_execution_time = time.time() - total_start_time
    all_results['total_execution_time'] = total_execution_time
    
    # Save final results
    with open(results_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\nAll propagations completed in {total_execution_time:.2f} seconds")
    print(f"Results saved to {results_file}")
    
    if upload_networks:
        print("\nUploaded networks:")
        for name, uuid in all_results['ndex_networks'].items():
            print(f"  {name}: {uuid}")
    
    return all_results

if __name__ == "__main__":
    # This module is not meant to be run directly
    print("This module provides dengue viral propagation functions for use in propagate_from_viral_proteins.py")
