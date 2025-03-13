#!/usr/bin/env python3

import os
import sys
import argparse
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Tuple
import networkx as nx
import ndex2.client as nc2
from ndex2.cx2 import CX2Network, RawCX2NetworkFactory
from weighted_propagation import load_ndex_credentials, load_from_ndex, score_limited_random_walk_with_restart

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

def enhance_network_with_propagation(original_cx2: CX2Network, weights: Dict[str, float], 
                                      viral_protein_id: str, viral_protein_name: str) -> CX2Network:
    """
    Enhance the original CX2 network with propagation results
    
    Args:
        original_cx2: Original CX2Network
        weights: Node weights from propagation
        viral_protein_id: ID of the viral protein used as start node
        viral_protein_name: Name of the viral protein
        
    Returns:
        Enhanced CX2 network
    """
    # Create a copy of the original network
    # (We'll actually modify the original, but this makes it clear we're working with a new instance)
    enhanced_network = original_cx2
    
    # Update network attributes to reflect propagation
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Update network name
    original_name = enhanced_network.get_name()
    new_name = f"Propagation from {viral_protein_name} - {timestamp}"
    enhanced_network.set_name(new_name)
    
    # Add propagation-specific network attributes
    enhanced_network.add_network_attribute('description', 
                                         f"Propagation network from viral protein {viral_protein_name}. Original network: {original_name}")
    enhanced_network.add_network_attribute('viral_protein_id', viral_protein_id)
    enhanced_network.add_network_attribute('viral_protein_name', viral_protein_name)
    enhanced_network.add_network_attribute('propagation_timestamp', timestamp)
    
    # Add propagation_weight to attribute declarations if not already present
    attr_declarations = enhanced_network.get_attribute_declarations()
    if 'nodes' not in attr_declarations:
        attr_declarations['nodes'] = {}
    if 'propagation_weight' not in attr_declarations['nodes']:
        attr_declarations['nodes']['propagation_weight'] = {'d': 'double'}
    enhanced_network.set_attribute_declarations(attr_declarations)
    
    # Add propagation weights to nodes
    for node_id_str, weight in weights.items():
        try:
            # Convert node_id from string to int for CX2
            node_id = int(node_id_str)
            
            # Add propagation weight to node attributes
            enhanced_network.add_node_attribute(node_id, 'propagation_weight', weight)
        except (ValueError, KeyError) as e:
            print(f"Warning: Could not add propagation weight to node {node_id_str}: {str(e)}")
    
    return enhanced_network

def upload_to_ndex(cx2_network: CX2Network) -> str:
    """
    Upload a CX2 network to NDEx
    
    Args:
        cx2_network: CX2Network object
        
    Returns:
        UUID of the uploaded network
    """
    username, password = load_ndex_credentials()
    
    if not username or not password:
        raise EnvironmentError("NDEX_USERNAME and NDEX_PASSWORD environment variables must be set")
        
    client = nc2.Ndex2(
        "http://public.ndexbio.org",
        username=username,
        password=password
    )
    
    # Convert to CX2 format
    cx2_data = cx2_network.to_cx2()
    
    # Upload to NDEx
    response = client.save_new_cx2_network(cx2_data)
    return response

def load_cx2_from_ndex(uuid: str) -> Tuple[CX2Network, str]:
    """
    Load a CX2 network directly from NDEx
    
    Args:
        uuid: NDEx network UUID
        
    Returns:
        Tuple of (CX2Network, network name)
    """
    username, password = load_ndex_credentials()
    
    if not username or not password:
        raise EnvironmentError("NDEX_USERNAME and NDEX_PASSWORD environment variables must be set")
        
    client = nc2.Ndex2(
        "http://public.ndexbio.org",
        username=username,
        password=password
    )
    
    # Download from NDEx
    response = client.get_network_as_cx2_stream(uuid)
    factory = RawCX2NetworkFactory()
    cx2_network = factory.get_cx2network(response.json())
    
    # Get network name
    network_name = cx2_network.get_name()
    if not network_name:
        # Fallback to network attributes
        network_attrs = cx2_network.get_network_attributes()
        network_name = network_attrs.get('name', f"network-{uuid[:8]}")
    
    return cx2_network, network_name

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
    parser.add_argument('--upload-to-ndex', action='store_true', help='Upload networks to NDEx')
    parser.add_argument('--dry-run', action='store_true', help='Identify viral proteins but do not run propagation')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Load type scores if provided
    type_score_dict = None
    if os.path.exists(args.type_scores):
        with open(args.type_scores, 'r') as f:
            print(f"Loading type scores from {args.type_scores}")
            type_score_dict = json.load(f)
    else:
        print(f"Warning: Type scores file {args.type_scores} not found, using default scores")
    
    # Load graph from NDEx for the propagation algorithm
    print(f"Loading network {args.uuid} from NDEx...")
    G, network_name = load_from_ndex(args.uuid)
    print(f"Loaded network '{network_name}' with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    
    # Also load the original CX2 network to preserve all properties
    print(f"Loading CX2 network {args.uuid} to preserve all node properties...")
    original_cx2, _ = load_cx2_from_ndex(args.uuid)
    
    # Identify viral proteins
    print("Identifying viral proteins...")
    viral_proteins = identify_viral_proteins(G)
    print(f"Found {len(viral_proteins)} viral proteins:")
    for node_id, name in viral_proteins:
        print(f"  {name} (ID: {node_id})")
    
    # Exit if dry run
    if args.dry_run:
        print("Dry run completed. Exiting without running propagation.")
        return
    
    # Create output file to store results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = os.path.join(args.output_dir, f"viral_propagation_results_{timestamp}.json")
    
    # Initialize results storage
    all_results = {
        'source_network': {
            'uuid': args.uuid,
            'name': network_name
        },
        'propagation_parameters': {
            'restart_prob': args.restart_prob,
            'max_score': args.max_score,
            'max_steps': args.max_steps,
            'default_score': args.default_score,
            'allow_revisits': args.allow_revisits,
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
            # Run propagation
            start_time = time.time()
            results = score_limited_random_walk_with_restart(
                G,
                node_id,
                restart_prob=args.restart_prob,
                max_cumulative_score=args.max_score,
                max_steps=args.max_steps,
                type_score_dict=type_score_dict,
                default_score=args.default_score,
                allow_revisits=args.allow_revisits
            )
            execution_time = time.time() - start_time
            results['execution_time'] = execution_time
            
            # Store results
            all_results['viral_proteins'][name] = {
                'node_id': node_id,
                'walk_stats': results['walk_stats'],
                'execution_time': execution_time
            }
            
            print(f"  Propagation completed in {execution_time:.2f} seconds")
            print(f"  Walk stats: {results['walk_stats']}")
            
            # Create enhanced network with propagation results
            if args.upload_to_ndex:
                print("  Enhancing network with propagation weights...")
                
                # Make a deep copy of the original CX2 for this viral protein
                # We need this because we're modifying the network for each viral protein
                import copy
                current_cx2 = copy.deepcopy(original_cx2)
                
                enhanced_network = enhance_network_with_propagation(
                    current_cx2, 
                    results['node_weights'], 
                    node_id, 
                    name
                )
                
                # Upload to NDEx
                print("  Uploading network to NDEx...")
                uuid = upload_to_ndex(enhanced_network)
                print(f"  Upload successful. New network UUID: {uuid}")
                
                # Store network UUID
                all_results['ndex_networks'][name] = uuid
            
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
    
    if args.upload_to_ndex:
        print("\nUploaded networks:")
        for name, uuid in all_results['ndex_networks'].items():
            print(f"  {name}: {uuid}")
    
if __name__ == "__main__":
    main()
