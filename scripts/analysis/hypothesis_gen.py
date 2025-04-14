#!/usr/bin/env python3

"""
Hypothesis generation module for creating scientific hypotheses from network analysis.
"""

import sys
import os
import json
import random
import math
from datetime import datetime
from typing import List, Dict, Any, Tuple, Set, Optional
import networkx as nx
from ndex2.cx2 import CX2Network

# Add parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.network_utils import get_experimental_data_properties

class LLMWrapper:
    """
    Simplified wrapper around the LLM class that doesn't require database operations.
    """
    def __init__(self, llm_type, model_name, api_keys=None, max_tokens=2048, seed=42, temperature=0.7):
        """
        Initialize the LLM wrapper with the given parameters.
        
        Args:
            llm_type: Type of LLM (OpenAI, Anthropic, Groq, GoogleAI, LocalModel)
            model_name: Name of the model to use
            api_keys: Dictionary of API keys for different LLM providers
            max_tokens: Maximum number of tokens to generate
            seed: Random seed for reproducibility
            temperature: Temperature for generation
        """
        # Import here to avoid circular imports
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from models.llm import LLM
        
        # Initialize with API keys if provided
        if api_keys and llm_type in api_keys:
            os.environ[f"{llm_type.upper()}_API_KEY"] = api_keys[llm_type]
        
        self.llm = LLM(
            type=llm_type,
            model_name=model_name,
            max_tokens=max_tokens,
            seed=seed,
            temperature=temperature
        )
    
    def query(self, context, prompt):
        """
        Query the LLM with the given context and prompt.
        
        Args:
            context: System context/instructions
            prompt: User query/prompt
            
        Returns:
            The model's response
        """
        return self.llm.query(context, prompt)

def analyze_network(G: nx.Graph, network_attrs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze a network to extract information for hypothesis generation
    
    Args:
        G: NetworkX graph
        network_attrs: Network attributes
        
    Returns:
        Dictionary with network analysis results
    """
    # Extract basic network statistics
    stats = {
        'name': G.graph.get('name', 'Unknown Network'),
        'node_count': G.number_of_nodes(),
        'edge_count': G.number_of_edges(),
        'avg_degree': sum(dict(G.degree()).values()) / G.number_of_nodes(),
    }
    
    # Find source nodes (e.g., viral proteins for dengue networks)
    source_node_name = network_attrs.get('source_node_name', None)
    source_node_id = network_attrs.get('source_node_id', None)
    
    # If source node info isn't in network attributes, try to find it in the graph
    if not source_node_name or not source_node_id:
        for node, attrs in G.nodes(data=True):
            # Look for nodes marked as source (can be customized for different network types)
            is_source = (
                attrs.get('viral_protein', False) or 
                attrs.get('type', '') == 'viral' or 
                attrs.get('node_type', '') == 'source'
            )
            
            if is_source:
                source_node_id = node
                source_node_name = attrs.get('name', attrs.get('GeneSymbol', node))
                break
    
    stats['source_node'] = {
        'name': source_node_name,
        'id': source_node_id
    }
    
    # Get nodes with propagation weights
    weighted_nodes = {}
    for node, attrs in G.nodes(data=True):
        if 'propagation_weight' in attrs:
            weight = attrs['propagation_weight']
            name = attrs.get('name', attrs.get('GeneSymbol', node))
            gene_symbol = attrs.get('GeneSymbol', name)
            
            # Extract all node attributes for experimental data
            node_data = {k: v for k, v in attrs.items() if k not in ['x', 'y', 'id']}
            
            weighted_nodes[node] = {
                'id': node,
                'name': name,
                'gene_symbol': gene_symbol,
                'weight': weight,
                'properties': node_data
            }
    
    # Sort nodes by propagation weight
    top_nodes = sorted(
        weighted_nodes.values(),
        key=lambda x: x['weight'],
        reverse=True
    )[:50]  # Get top 50 nodes by weight
    
    stats['top_nodes'] = top_nodes
    
    # Get node types distribution
    type_counts = {}
    for node, attrs in G.nodes(data=True):
        node_type = attrs.get('type', 'undefined')
        if node_type in type_counts:
            type_counts[node_type] += 1
        else:
            type_counts[node_type] = 1
    
    stats['type_distribution'] = type_counts
    
    # Identify experimental data properties
    stats['property_groups'] = get_experimental_data_properties(G)
    
    return stats

def get_top_nodes_with_experimental_data(network_stats: Dict[str, Any], max_nodes: int = 15) -> str:
    """
    Generate a formatted string of top nodes with their experimental data
    
    Args:
        network_stats: Dictionary with network analysis results
        max_nodes: Maximum number of nodes to include
        
    Returns:
        Formatted string for the prompt
    """
    top_nodes = network_stats['top_nodes'][:max_nodes]
    property_groups = network_stats['property_groups']
    
    # Select key experimental properties to display
    exp_properties = property_groups.get('experimental', [])
    
    # Limit to most informative properties if there are too many
    if len(exp_properties) > 5:
        exp_properties = exp_properties[:5]
    
    # Build the text
    lines = []
    
    for node in top_nodes:
        node_props = node['properties']
        name = node['name']
        gene_symbol = node.get('gene_symbol', '')
        weight = node['weight']
        
        # Include gene symbol if different from name
        node_name = name
        if gene_symbol and gene_symbol != name:
            node_name = f"{name} ({gene_symbol})"
            
        # Start with basic info
        line = f"- {node_name}: Weight: {weight:.4f}"
        
        # Add experimental data if available
        exp_data = []
        for prop in exp_properties:
            if prop in node_props:
                value = node_props[prop]
                if isinstance(value, float):
                    value = f"{value:.4f}"
                exp_data.append(f"{prop}: {value}")
        
        if exp_data:
            line += " | " + ", ".join(exp_data)
            
        lines.append(line)
    
    return "\n".join(lines)

def generate_hypothesis_prompt(network_stats: Dict[str, Any], n_hypotheses: int = 2, domain_name: str = "biological") -> str:
    """
    Generate a prompt for hypothesis generation based on network analysis
    
    Args:
        network_stats: Dictionary with network analysis results
        n_hypotheses: Number of hypotheses to generate
        domain_name: Domain name (e.g., "biological", "dengue virus", etc.)
        
    Returns:
        Prompt for the LLM
    """
    # Extract information from network stats
    source_node = network_stats['source_node']['name'] or "Unknown source node"
    
    # Get formatted nodes with experimental data
    top_nodes_text = get_top_nodes_with_experimental_data(network_stats, max_nodes=15)
    
    # Get experimental properties for context
    property_groups = network_stats['property_groups']
    all_exp_properties = property_groups.get('experimental', [])
    exp_properties_text = ", ".join(all_exp_properties)
    
    # Create prompt
    prompt = f"""
Based on a {domain_name} network analysis for {source_node}, I need to generate {n_hypotheses} formal scientific hypotheses.

The dataset includes the following experimental data properties for nodes: {exp_properties_text}

The propagation analysis identified the following top nodes with the highest propagation weights (most closely connected to the source node), along with their experimental data:

{top_nodes_text}

For each hypothesis, please:
1. Propose a specific testable hypothesis about how {source_node} might interact with these nodes
2. Focus on relationships supported by the experimental data shown above
3. Format as formal null (H0) and alternative (H1) hypotheses
4. Explain the biological rationale based on the nodes and experimental data involved
5. Suggest specific experiments that could falsify the hypothesis

Format each hypothesis as a JSON object with the following fields:
- "title": A brief descriptive title for the hypothesis (5-10 words)
- "null_hypothesis": The formal null hypothesis statement (H0)
- "alternative_hypothesis": The formal alternative hypothesis statement (H1)
- "rationale": Reasoning behind the hypothesis, referencing the experimental data (3-5 sentences)
- "entities_involved": List of key entities mentioned in the hypothesis
- "experimental_data_used": Brief description of which experimental data properties influenced this hypothesis
- "experimental_validation": 2-3 specific experiments that could falsify the hypothesis
- "confidence": A value from 1-5 indicating your confidence in this hypothesis (5 being highest)

Return ONLY a valid JSON array of hypothesis objects. Do not include any explanation or other text outside the JSON.
"""
    
    return prompt

def generate_hypotheses(
    network_stats: Dict[str, Any], 
    llm_wrapper: LLMWrapper, 
    n_hypotheses: int = 2,
    domain_name: str = "biological",
    system_context: str = None
) -> List[Dict[str, Any]]:
    """
    Generate hypotheses using LLM based on network analysis
    
    Args:
        network_stats: Dictionary with network analysis results
        llm_wrapper: LLMWrapper for LLM query
        n_hypotheses: Number of hypotheses to generate
        domain_name: Domain name for the prompt
        system_context: Optional custom system context for the LLM
        
    Returns:
        List of hypothesis dictionaries
    """
    # Generate prompt for the LLM
    prompt = generate_hypothesis_prompt(network_stats, n_hypotheses, domain_name)
    
    # Default system context for the LLM if none provided
    if system_context is None:
        system_context = f"""
You are a {domain_name} expert specializing in network analysis. 
Your task is to generate scientifically plausible, falsifiable hypotheses based on the network analysis and experimental data.
Each hypothesis should be formally defined with null (H0) and alternative (H1) hypotheses.
Focus on mechanistic insights that are specifically supported by the experimental data provided.
Return your response in valid JSON format only.
"""
    
    # Query the LLM
    print(f"Generating {n_hypotheses} hypotheses with the LLM...")
    response = llm_wrapper.query(system_context, prompt)
    
    # Try to parse the response as JSON
    try:
        # The LLM might include additional text, so try to extract just the JSON part
        response = response.strip()
        
        # If response starts with backticks (markdown code block), remove them
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        
        # Parse JSON
        hypotheses = json.loads(response.strip())
        
        # Validate hypotheses
        for i, hypothesis in enumerate(hypotheses):
            # Ensure required fields exist
            required_fields = ['title', 'null_hypothesis', 'alternative_hypothesis', 'rationale', 
                              'entities_involved', 'experimental_data_used', 'experimental_validation', 'confidence']
            for field in required_fields:
                if field not in hypothesis:
                    hypothesis[field] = f"Missing {field}"
            
            # Add hypothesis ID
            hypothesis['id'] = f"H{i+1}"
            
            # Add source node
            hypothesis['source_node'] = network_stats['source_node']['name']
        
        return hypotheses
    
    except json.JSONDecodeError as e:
        print(f"Error parsing LLM response as JSON: {e}")
        print("LLM response:")
        print(response)
        
        # Return a placeholder in case of failure
        return [{
            "id": "H1",
            "title": "Failed to generate valid hypothesis",
            "null_hypothesis": "Failed to generate valid null hypothesis",
            "alternative_hypothesis": "Failed to generate valid alternative hypothesis",
            "rationale": f"LLM response could not be parsed as JSON: {str(e)}",
            "entities_involved": [],
            "experimental_data_used": "N/A",
            "experimental_validation": "N/A",
            "confidence": 0,
            "source_node": network_stats['source_node']['name']
        }]

def create_hypothesis_network(all_hypotheses: List[Dict[str, Any]], network_name: str = None) -> CX2Network:
    """
    Create a CX2 network containing hypotheses as nodes
    
    Args:
        all_hypotheses: List of all hypothesis dictionaries
        network_name: Optional name for the network
        
    Returns:
        CX2Network object
    """
    # Create a new CX2 network
    cx2_network = CX2Network()
    
    # Set network attributes
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if network_name:
        cx2_network.set_name(network_name)
    else:
        # Default network name
        cx2_network.set_name(f"Hypothesis Network - {timestamp}")
    
    cx2_network.add_network_attribute('description', 
                                      f"Network of generated hypotheses")
    cx2_network.add_network_attribute('generation_timestamp', timestamp)
    
    # Add attribute declarations - including both node and network attributes
    attr_declarations = {
        'nodes': {
            'name': {'d': 'string'},
            'title': {'d': 'string'},
            'null_hypothesis': {'d': 'string'},
            'alternative_hypothesis': {'d': 'string'},
            'rationale': {'d': 'string'},
            'entities_involved': {'d': 'string'},
            'experimental_data_used': {'d': 'string'},
            'experimental_validation': {'d': 'string'},
            'confidence': {'d': 'integer'},
            'source_node': {'d': 'string'},
            'node_type': {'d': 'string'},
            'x': {'d': 'double'},
            'y': {'d': 'double'},
            'n': {'d': 'string'}
        },
        'networkAttributes': {
            'name': {'d': 'string'},
            'description': {'d': 'string'},
            'generation_timestamp': {'d': 'string'}
        }
    }
    cx2_network.set_attribute_declarations(attr_declarations)
    
    # Group hypotheses by source node
    hypotheses_by_source = {}
    for hypothesis in all_hypotheses:
        source_node = hypothesis['source_node']
        if source_node not in hypotheses_by_source:
            hypotheses_by_source[source_node] = []
        hypotheses_by_source[source_node].append(hypothesis)
    
    # Add hypotheses as nodes
    node_id = 1
    
    for source_node, hypotheses in hypotheses_by_source.items():
        # Calculate positions for this group of hypotheses
        base_angle = random.uniform(0, 2 * math.pi)  # Random starting angle for this source
        radius = 500
        
        for i, hypothesis in enumerate(hypotheses):
            # Calculate position in a circle section
            angle = base_angle + (2 * math.pi / len(hypotheses)) * i
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            
            # Format entities involved as semicolon-separated list
            entities_text = "; ".join(hypothesis['entities_involved'])
            
            # Format experimental validation as semicolon-separated list if it's a list
            exp_validation = hypothesis['experimental_validation']
            if isinstance(exp_validation, list):
                exp_validation = "; ".join(exp_validation)
            
            # Create node name (will be displayed in visualization)
            node_name = f"{source_node} - {hypothesis['title']}"
            
            # Add node to network (without name parameter)
            cx2_network.add_node(node_id)
            
            # Add node name as 'n' attribute (this is what CX2 expects)
            cx2_network.add_node_attribute(node_id, 'n', node_name)
            
            # Add node attributes
            cx2_network.add_node_attribute(node_id, 'title', hypothesis['title'])
            cx2_network.add_node_attribute(node_id, 'null_hypothesis', hypothesis['null_hypothesis'])
            cx2_network.add_node_attribute(node_id, 'alternative_hypothesis', hypothesis['alternative_hypothesis'])
            cx2_network.add_node_attribute(node_id, 'rationale', hypothesis['rationale'])
            cx2_network.add_node_attribute(node_id, 'entities_involved', entities_text)
            cx2_network.add_node_attribute(node_id, 'experimental_data_used', hypothesis['experimental_data_used'])
            cx2_network.add_node_attribute(node_id, 'experimental_validation', exp_validation)
            cx2_network.add_node_attribute(node_id, 'confidence', hypothesis['confidence'])
            cx2_network.add_node_attribute(node_id, 'source_node', source_node)
            cx2_network.add_node_attribute(node_id, 'node_type', 'hypothesis')
            cx2_network.add_node_attribute(node_id, 'x', x)
            cx2_network.add_node_attribute(node_id, 'y', y)
            
            node_id += 1
    
    return cx2_network

if __name__ == "__main__":
    # This module is not meant to be run directly
    print("This module provides hypothesis generation functions for use in other scripts")
    print("For example usage, see scripts/generate_hypotheses.py")
