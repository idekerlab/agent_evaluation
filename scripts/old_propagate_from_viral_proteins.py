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

def create_propagation_network(original_g: nx.Graph, weights: Dict[str, float], 
                               viral_protein_id: str, viral_protein_name: str) -> CX2Network:
    """
    Create a CX2 network from the propagation results
    
    Args:
        original_g: Original NetworkX graph
        weights: Node weights from propagation
        viral_protein_id: ID of the viral protein used as start node
        viral_protein_name: Name of the viral protein
        
    Returns:
        CX2 network
    """
    # Create a new CX2 network
    cx2_network = CX2Network()
    
    # Set network attributes
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    network_name = f"Dengue Propagation from {viral_protein_name} - {timestamp}"
    
    cx2_network.set_name(network_name)
    cx2_network.add_network_attribute('description', 
                                     f"Propagation network from viral protein {viral_protein_name}")
    cx2_network.add_network_attribute('viral_protein_id', viral_protein_id)
    cx2_network.add_network_attribute('viral_protein_name', viral_protein_name)
    cx2_network.add_network_attribute('propagation_timestamp', timestamp)
    
    # Add attribute declarations
    attr_declarations = {
        'nodes': {
            'name': {'d': 'string'},
            'GeneSymbol': {'d': 'string'},
            'type': {'d': 'string'},
            'viral_protein': {'d': 'boolean'},
            'propagation_weight': {'d': 'double'},
            'x': {'d': 'double'},
            'y': {'d': 'double'}
        },
        'edges': {
            'interaction': {'d': 'string'},
            'combined_score': {'d': 'double'}
        }
    }
    cx2_network.set_attribute_declarations(attr_declarations)
    
    # Add nodes to network (only include nodes with weight > 0)
    for node_id, weight in weights.items():
        if weight > 0:
            # Get original node attributes
            if node_id in original_g.nodes:
                attrs = dict(original_g.nodes[node_id])
                
                # Add propagation weight
                attrs['propagation_weight'] = weight
                
                # Add node to CX2 network
                cx2_network.add_node(int(node_id), {"name": attrs.get('name', '')})
                
                # Add node attributes
                for key, value in attrs.items():
                    if key not in ['id', 'name']:
                        cx2_network.add_node_attribute(int(node_id), key, value)
    
    # Add edges between nodes that are in the new network
    for u, v, attrs in original_g.edges(data=True):
        if u in weights and v in weights and weights[u] > 0 and weights[v] > 0:
            # Add edge to CX2 network
            source_id = int(u)
            target_id = int(v)
            
            # Add edge to CX2 network with attributes
            cx2_network.add_edge(source_id, target_id)
            
            # Add edge attributes
            for key, value in attrs.items():
                if key != 'id':
                    cx2_network.add_edge_attribute(source_id, target_id, key, value)
    
    return cx2_network

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
    
    # Load graph from NDEx
    print(f"Loading network {args.uuid} from NDEx...")
    G, network_name = load_from_ndex(args.uuid)
    print(f"Loaded network '{network_name}' with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    
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
            
            # Create network from propagation results
            if args.upload_to_ndex:
                print("  Creating propagation network...")
                cx2_network = create_propagation_network(G, results['node_weights'], node_id, name)
                
                # Upload to NDEx
                print("  Uploading network to NDEx...")
                uuid = upload_to_ndex(cx2_network)
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
