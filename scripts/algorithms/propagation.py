#!/usr/bin/env python3

"""
Network propagation algorithms including random walk with restart.
"""

import random
import json
import sys
import os
import networkx as nx
from datetime import datetime
from typing import Dict, List, Any, Set, Optional, Tuple

# Add parent directory to the path so we can import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.network_utils import networkx_to_cx2, extract_subnetwork

def score_multi_seed_random_walk(
    G: nx.Graph, 
    seed_nodes: List[str],           # Now accepts multiple seed nodes
    restart_prob: float = 0.2, 
    max_cumulative_score: float = 10.0, 
    max_steps: int = 100, 
    type_score_dict: Optional[Dict[str, float]] = None, 
    default_score: float = 1.0, 
    allow_revisits: bool = True,
    seed_selection_strategy: str = 'uniform'  # Strategy for selecting seed node on restart
) -> Dict[str, Any]:
    """
    Perform a random walk with restart on graph G, from multiple seed nodes.
    The walk is limited by a maximum cumulative score.
    
    Args:
        G: NetworkX graph
        seed_nodes: List of starting node IDs
        restart_prob: Probability to restart at one of the seed nodes
        max_cumulative_score: Maximum cumulative score before the walk terminates
        max_steps: Maximum number of steps before the walk terminates
        type_score_dict: Dictionary mapping node types to scores
        default_score: Default score for node types not in type_score_dict
        allow_revisits: Whether to allow visiting the same node multiple times
        seed_selection_strategy: Strategy for selecting seed node on restart
                              - 'uniform': Equal probability for all seeds
                              - 'weighted': Weighted by node scores
                              - 'proportional': Proportional to node degree
        
    Returns:
        Dictionary with walk results including node weights
    """
    # Validate seed nodes
    valid_seed_nodes = [node for node in seed_nodes if node in G]
    if not valid_seed_nodes:
        raise ValueError(f"None of the provided seed nodes were found in the graph")
    
    # Use valid seeds going forward
    seed_nodes = valid_seed_nodes
    
    # Initialize type_score_dict if not provided
    if type_score_dict is None:
        type_score_dict = {'default': default_score}
    
    # Get node score based on its type
    def get_node_score(node):
        node_type = G.nodes[node].get('type', 'default')
        return type_score_dict.get(node_type, default_score)
    
    # Function to select a seed node based on the specified strategy
    def select_seed_node():
        if seed_selection_strategy == 'uniform':
            # Equal probability for all seeds
            return random.choice(seed_nodes)
        elif seed_selection_strategy == 'weighted':
            # Weight by node score
            weights = [get_node_score(node) for node in seed_nodes]
            total = sum(weights)
            if total == 0:
                return random.choice(seed_nodes)
            probs = [w/total for w in weights]
            return random.choices(seed_nodes, weights=probs, k=1)[0]
        elif seed_selection_strategy == 'proportional':
            # Weight by node degree
            weights = [G.degree(node) for node in seed_nodes]
            total = sum(weights)
            if total == 0:
                return random.choice(seed_nodes)
            probs = [w/total for w in weights]
            return random.choices(seed_nodes, weights=probs, k=1)[0]
        else:
            # Default to uniform if unknown strategy
            return random.choice(seed_nodes)
    
    # Initialize walk with a randomly selected seed node
    current_node = select_seed_node()
    path = [current_node]
    cumulative_score = get_node_score(current_node)
    step_count = 1
    restart_count = 0
    
    # Track node visit counts
    visit_counts = {node: 0 for node in G.nodes()}
    for seed in seed_nodes:
        if seed in visit_counts:  # Safety check
            visit_counts[seed] = 0  # Reset seeds to 0 to start
    visit_counts[current_node] = 1  # Count first node
    
    # Track seed contributions
    seed_contributions = {seed: {node: 0 for node in G.nodes()} for seed in seed_nodes}
    current_seed = current_node
    if current_node in seed_nodes:
        seed_contributions[current_node][current_node] = 1
    
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
            elif not any(seed in neighbors for seed in seed_nodes):
                # If all neighbors visited and no seed in neighbors
                termination_reason = "all_neighbors_visited"
                break
        
        # Decide whether to restart
        if random.random() < restart_prob:
            # Select a seed node based on strategy
            next_seed = select_seed_node()
            
            if current_node != next_seed:  # Only count as restart if moving to different node
                current_node = next_seed
                current_seed = next_seed  # Track current seed for contribution
                path.append(current_node)
                restart_count += 1
                visit_counts[current_node] += 1
                cumulative_score += get_node_score(current_node)
                step_count += 1
                
                # Update seed contribution
                seed_contributions[current_seed][current_node] += 1
        else:
            # Choose random neighbor
            next_node = random.choice(neighbors)
            current_node = next_node
            path.append(current_node)
            visit_counts[current_node] += 1
            cumulative_score += get_node_score(current_node)
            step_count += 1
            
            # Update seed contribution
            seed_contributions[current_seed][current_node] += 1
    
    # Set termination reason if not set
    if termination_reason == "unknown":
        if cumulative_score >= max_cumulative_score:
            termination_reason = "max_score_reached"
        elif step_count >= max_steps:
            termination_reason = "max_steps_reached"
    
    # Calculate node weights based on visit frequency
    total_visits = sum(visit_counts.values())
    node_weights = {node: count / total_visits for node, count in visit_counts.items() if count > 0}
    
    # Calculate seed contribution percentages
    seed_contribution_percentages = {}
    for seed in seed_nodes:
        seed_contribution_percentages[seed] = {}
        for node, visits in seed_contributions[seed].items():
            if node in node_weights and visit_counts[node] > 0:
                seed_contribution_percentages[seed][node] = visits / visit_counts[node]
    
    # Prepare results
    results = {
        'node_weights': node_weights,
        'path': path,
        'walk_stats': {
            'cumulative_score': cumulative_score,
            'steps': step_count,
            'restarts': restart_count,
            'termination_reason': termination_reason,
            'seed_nodes': seed_nodes,
            'seed_selection_strategy': seed_selection_strategy
        },
        'seed_contributions': seed_contribution_percentages,
        'execution_time': 0.0  # Will be set by caller
    }
    
    return results

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
    Legacy wrapper for backward compatibility with single-seed propagation.
    
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
    return score_multi_seed_random_walk(
        G,
        [start_node],
        restart_prob=restart_prob,
        max_cumulative_score=max_cumulative_score,
        max_steps=max_steps,
        type_score_dict=type_score_dict,
        default_score=default_score,
        allow_revisits=allow_revisits,
        seed_selection_strategy='uniform'  # Default strategy for single seed
    )

def create_propagation_network(
    original_cx2, 
    weights: Dict[str, float], 
    seed_nodes: List[str],
    include_all_nodes: bool = False,
    network_name: str = None
) -> Dict:
    """
    Create a network with propagation results.
    
    Args:
        original_cx2: Original CX2Network
        weights: Node weights from propagation
        seed_nodes: List of seed nodes used for propagation
        include_all_nodes: If True, include all nodes from original network,
                           If False, include only nodes with propagation weights
        network_name: Optional name for the network
        
    Returns:
        Dictionary in CX2 format containing the enhanced network
    """
    # Import here to avoid circular imports
    from utils.network_utils import cx2_to_networkx, networkx_to_cx2, merge_visual_properties
    
    # Get the original CX2 data if we received a CX2Network object
    original_cx2_data = None
    if isinstance(original_cx2, dict) or isinstance(original_cx2, list):
        original_cx2_data = original_cx2
    else:
        # Assume it's a CX2Network object and convert to dict
        original_cx2_data = original_cx2.to_cx2()
    
    # Start by converting CX2 to NetworkX for manipulation
    G = cx2_to_networkx(original_cx2)
    
    # Add propagation weights to nodes in the NetworkX graph
    for node_id_str, weight in weights.items():
        if node_id_str in G.nodes:
            G.nodes[node_id_str]['propagation_weight'] = weight
    
    # Create filtered network if needed
    if not include_all_nodes:
        # Extract only nodes with propagation weights
        weighted_nodes = [node for node in G.nodes if 'propagation_weight' in G.nodes[node]]
        G = extract_subnetwork(G, weighted_nodes, include_connecting_edges=True)
    
    # Update network attributes
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Set network name
    if network_name:
        G.graph['name'] = network_name
    else:
        seed_names = []
        for node_id in seed_nodes:
            if node_id in G.nodes:
                name = G.nodes[node_id].get('name', G.nodes[node_id].get('GeneSymbol', node_id))
                seed_names.append(name)
        
        seeds_str = ", ".join(seed_names[:3])
        if len(seed_names) > 3:
            seeds_str += f" and {len(seed_names) - 3} more"
            
        G.graph['name'] = f"Propagation from {seeds_str} - {timestamp}"
    
    # Add propagation-specific network attributes
    G.graph['description'] = f"Propagation network from {len(seed_nodes)} seed nodes"
    G.graph['seed_nodes'] = json.dumps(seed_nodes)
    G.graph['propagation_timestamp'] = timestamp
    G.graph['include_all_nodes'] = include_all_nodes
    G.graph['version'] = "1.0"
    
    # Convert to CX2 format
    result_cx2_data = networkx_to_cx2(G)
    
    # Preserve visual styles from the original network by merging them into the result
    result_cx2_data = merge_visual_properties(result_cx2_data, original_cx2_data)
    
    return result_cx2_data

if __name__ == "__main__":
    # This module is not meant to be run directly
    print("This module provides propagation algorithms for use in other scripts")
    print("For example usage, see scripts/propagate_from_viral_proteins.py")
