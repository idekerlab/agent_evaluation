#!/usr/bin/env python3

import os
import argparse
import random
import time
import json
import networkx as nx
from datetime import datetime
from typing import Dict, List, Tuple, Any, Set, Optional
import ndex2 as nd2
import ndex2.client as nc2
from ndex2.cx2 import CX2Network
from ndex2.cx2 import RawCX2NetworkFactory

def load_ndex_credentials() -> Tuple[str, str]:
    """Load NDEx credentials from environment variables"""
    username = os.environ.get("NDEX_USERNAME")
    password = os.environ.get("NDEX_PASSWORD")
    return username, password

def load_from_ndex(uuid: str) -> Tuple[nx.Graph, str]:
    """Load knowledge graph from NDEx network
    
    Args:
        uuid: NDEx network UUID
        
    Returns:
        Tuple containing (networkx graph, network name)
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
    # Use get_name() method or get name from network attributes
    network_name = cx2_network.get_name()
    if not network_name:
        # Fallback to network attributes
        network_attrs = cx2_network.get_network_attributes()
        network_name = network_attrs.get('name', f"network-{uuid[:8]}")
    
    # Convert CX2 to NetworkX
    G = cx2_to_networkx(cx2_network)
    
    return G, network_name

def cx2_to_networkx(cx2_network: CX2Network) -> nx.Graph:
    """Convert CX2 network to NetworkX graph
    
    Args:
        cx2_network: CX2 network object
        
    Returns:
        NetworkX graph
    """
    # Create empty graph
    G = nx.Graph()
    
    # Create a lookup from gene symbols to node IDs
    gene_to_id = {}
    
    # Add nodes with attributes
    for node_id, node_attrs in cx2_network.get_nodes().items():
        # Use numeric ID as the node identifier in NetworkX
        node_id_str = str(node_id)
        
        # Extract attributes from 'v' if present
        v_attrs = {}
        if 'v' in node_attrs and isinstance(node_attrs['v'], dict):
            v_attrs = node_attrs['v']
        
        # Prepare node attributes dict (include all attributes)
        attrs = {
            'id': node_id,
            'x': node_attrs.get('x', 0),
            'y': node_attrs.get('y', 0)
        }
        
        # Add all attributes from 'v'
        for k, v in v_attrs.items():
            attrs[k] = v
            
        # Store gene symbol to node ID mapping if available
        gene_name = attrs.get('name', '')
        if gene_name:
            gene_to_id[gene_name] = node_id_str
            
        # Also use GeneSymbol as a lookup if different from name
        gene_symbol = attrs.get('GeneSymbol', '')
        if gene_symbol and gene_symbol != gene_name:
            gene_to_id[gene_symbol] = node_id_str
        
        # Add node to graph with ID as the node identifier
        G.add_node(node_id_str, **attrs)
    
    # Add edges with attributes
    for edge_id, edge_attrs in cx2_network.get_edges().items():
        source_id = str(edge_attrs.get('s'))
        target_id = str(edge_attrs.get('t'))
        
        # Extract attributes from 'v' if present
        v_attrs = {}
        if 'v' in edge_attrs and isinstance(edge_attrs['v'], dict):
            v_attrs = edge_attrs['v']
        
        # Prepare edge attributes
        attrs = {
            'id': edge_id
        }
        
        # Add all attributes from 'v'
        for k, v in v_attrs.items():
            attrs[k] = v
        
        # Add edge to graph
        if source_id in G and target_id in G:
            G.add_edge(source_id, target_id, **attrs)
    
    # Store the gene symbol to ID mapping in graph metadata
    G.graph['gene_to_id'] = gene_to_id
    
    return G

def score_limited_random_walk_with_restart(
    G: nx.Graph, 
    start_node: str, 
    restart_prob: float = 0.2, 
    max_cumulative_score: float = 10.0, 
    max_steps: int = 100, 
    type_score_dict: Optional[Dict[str, float]] = None, 
    default_score: float = 1.0, 
    allow_revisits: bool = True
) -> Dict[str, Any]:
    """
    Perform a random walk with restart on graph G, starting from start_node.
    The walk is limited by a maximum cumulative score.
    
    Args:
        G: NetworkX graph
        start_node: Name of the starting node
        restart_prob: Probability to restart at the start_node
        max_cumulative_score: Maximum cumulative score before the walk terminates
        max_steps: Maximum number of steps before the walk terminates
        type_score_dict: Dictionary mapping node types to scores
        default_score: Default score for node types not in type_score_dict
        allow_revisits: Whether to allow visiting the same node multiple times
        
    Returns:
        Dictionary with walk results
    """
    if start_node not in G:
        raise ValueError(f"Start node '{start_node}' not found in graph")
    
    # Initialize type_score_dict if not provided
    if type_score_dict is None:
        type_score_dict = {'default': default_score}
    
    # Get node score based on its type
    def get_node_score(node):
        node_type = G.nodes[node].get('type', 'default')
        return type_score_dict.get(node_type, default_score)
    
    # Initialize walk
    current_node = start_node
    path = [current_node]
    cumulative_score = get_node_score(current_node)
    step_count = 1
    restart_count = 0
    
    # Track node visit counts
    visit_counts = {node: 0 for node in G.nodes()}
    visit_counts[start_node] = 1
    
    # Track termination reason
    termination_reason = "unknown"
    
    # Perform walk
    while cumulative_score < max_cumulative_score and step_count < max_steps:
        # Check if we have neighbors to visit
        neighbors = list(G.neighbors(current_node))
        
        if not neighbors:
            termination_reason = "dead_end"
            break
            
        # Filter neighbors that have already been visited if revisits not allowed
        if not allow_revisits:
            unvisited_neighbors = [n for n in neighbors if visit_counts[n] == 0]
            if unvisited_neighbors:
                neighbors = unvisited_neighbors
            else:
                # If all neighbors have been visited and revisits not allowed
                if not G.neighbors(start_node) or (start_node in neighbors and len(neighbors) == 1):
                    termination_reason = "all_neighbors_visited"
                    break
        
        # Decide whether to restart
        if random.random() < restart_prob:
            if current_node != start_node:  # Only count as restart if not already at start
                current_node = start_node
                path.append(current_node)
                restart_count += 1
                visit_counts[start_node] += 1
                cumulative_score += get_node_score(start_node)
                step_count += 1
        else:
            # Choose random neighbor
            next_node = random.choice(neighbors)
            current_node = next_node
            path.append(current_node)
            visit_counts[current_node] += 1
            cumulative_score += get_node_score(current_node)
            step_count += 1
    
    # Set termination reason if not set
    if termination_reason == "unknown":
        if cumulative_score >= max_cumulative_score:
            termination_reason = "max_score_reached"
        elif step_count >= max_steps:
            termination_reason = "max_steps_reached"
    
    # Calculate node weights based on visit frequency
    total_visits = sum(visit_counts.values())
    node_weights = {node: count / total_visits for node, count in visit_counts.items() if count > 0}
    
    # Prepare results
    results = {
        'node_weights': node_weights,
        'path': path,
        'walk_stats': {
            'cumulative_score': cumulative_score,
            'steps': step_count,
            'restarts': restart_count,
            'termination_reason': termination_reason
        },
        'execution_time': 0.0  # Will be set by caller
    }
    
    return results

def main():
    parser = argparse.ArgumentParser(description='Random Walk with Restart Graph Propagation')
    
    # Required arguments
    parser.add_argument('--uuid', type=str, required=True, help='NDEx network UUID')
    parser.add_argument('--start-node', type=str, required=True, help='Name of the starting node or gene symbol')
    
    # Optional arguments
    parser.add_argument('--restart-prob', type=float, default=0.2, help='Restart probability')
    parser.add_argument('--max-score', type=float, default=10.0, help='Maximum cumulative score')
    parser.add_argument('--max-steps', type=int, default=100, help='Maximum number of steps')
    parser.add_argument('--default-score', type=float, default=1.0, help='Default node score')
    parser.add_argument('--allow-revisits', action='store_true', help='Allow revisiting nodes')
    parser.add_argument('--type-scores', type=str, help='JSON file with node type to score mapping')
    parser.add_argument('--output-dir', type=str, default='.', help='Output directory for results')
    parser.add_argument('--list-genes', action='store_true', help='List gene symbols found in the network')
    
    args = parser.parse_args()
    
    # Load type scores if provided
    type_score_dict = None
    if args.type_scores:
        with open(args.type_scores, 'r') as f:
            type_score_dict = json.load(f)
    
    # Load graph from NDEx
    print(f"Loading network {args.uuid} from NDEx...")
    G, network_name = load_from_ndex(args.uuid)
    print(f"Loaded network '{network_name}' with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    
    # If just listing genes, show the gene symbols and exit
    if args.list_genes:
        print("\nGene symbols found in network:")
        gene_symbols = set()
        
        # Collect gene symbols from node attributes
        for node, attrs in G.nodes(data=True):
            if 'name' in attrs:
                gene_symbols.add(attrs['name'])
            if 'GeneSymbol' in attrs and attrs['GeneSymbol'] != attrs.get('name', ''):
                gene_symbols.add(attrs['GeneSymbol'])
        
        for i, symbol in enumerate(sorted(gene_symbols)):
            if symbol:  # Only show non-empty symbols
                print(f"  {symbol}")
            if i >= 99 and len(gene_symbols) > 100:
                print(f"  ... and {len(gene_symbols) - 100} more")
                break
        return
    
    # Find start node ID from gene symbol if needed
    start_node_id = args.start_node
    
    # If the start node is not directly a node ID, try to find it through gene symbol mapping
    if start_node_id not in G and hasattr(G, 'graph') and 'gene_to_id' in G.graph:
        if args.start_node in G.graph['gene_to_id']:
            start_node_id = G.graph['gene_to_id'][args.start_node]
            print(f"Found start node '{args.start_node}' with ID: {start_node_id}")
    
    # Check if start node exists
    if start_node_id not in G:
        print(f"Error: Start node '{args.start_node}' not found in graph")
        
        # Try to find similar nodes
        print("\nSearching for similar gene symbols...")
        similar_genes = []
        for node, attrs in G.nodes(data=True):
            gene_symbol = attrs.get('GeneSymbol', attrs.get('name', ''))
            if gene_symbol and args.start_node.upper() in gene_symbol.upper():
                similar_genes.append((node, gene_symbol))
        
        if similar_genes:
            print(f"Found {len(similar_genes)} similar gene symbols:")
            for node_id, symbol in similar_genes[:10]:
                print(f"  Node ID: {node_id}, Symbol: {symbol}")
            if len(similar_genes) > 10:
                print(f"  ... and {len(similar_genes) - 10} more")
        
        print("\nTry using --list-genes to see available gene symbols")
        return
    
    # Perform random walk
    print(f"Starting random walk from node '{start_node_id}' ({args.start_node})...")
    start_time = time.time()
    results = score_limited_random_walk_with_restart(
        G,
        start_node_id,
        restart_prob=args.restart_prob,
        max_cumulative_score=args.max_score,
        max_steps=args.max_steps,
        type_score_dict=type_score_dict,
        default_score=args.default_score,
        allow_revisits=args.allow_revisits
    )
    execution_time = time.time() - start_time
    results['execution_time'] = execution_time
    
    # Add gene symbols to results
    results['gene_weights'] = {}
    for node_id, weight in results['node_weights'].items():
        if node_id in G.nodes:
            # Get gene name from attributes
            gene_symbol = G.nodes[node_id].get('name', '')
            if gene_symbol:
                results['gene_weights'][gene_symbol] = weight
            else:
                # Fallback to GeneSymbol if name is not available
                gene_symbol = G.nodes[node_id].get('GeneSymbol', node_id)
                results['gene_weights'][gene_symbol] = weight
    
    # Create output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{network_name}_{args.start_node}_{timestamp}.json"
    filename = os.path.join(args.output_dir, filename.replace(" ", "_"))
    
    # Save results
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Walk completed in {execution_time:.2f} seconds")
    print(f"Results saved to {filename}")
    print(f"Walk stats: {results['walk_stats']}")
    
    # Display top nodes by weight with gene symbols
    print(f"Top 10 genes by weight:")
    for gene, weight in sorted(results['gene_weights'].items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {gene}: {weight:.4f}")
    
if __name__ == "__main__":
    main()