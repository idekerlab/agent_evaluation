#!/usr/bin/env python3

import os
import sys
import argparse
import json
import time
from datetime import datetime
import networkx as nx
import ndex2.client as nc2
from ndex2.cx2 import CX2Network
from ndex2.cx2 import RawCX2NetworkFactory
from typing import List, Dict, Any, Tuple, Set
import random

# Add the parent directory to the path so we can import the models/llm.py module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.llm import LLM

class LLMWrapper:
    """
    Simplified wrapper around the LLM class that doesn't require database operations.
    """
    def __init__(self, llm_type, model_name, max_tokens=2048, seed=42, temperature=0.7):
        """
        Initialize the LLM wrapper with the given parameters.
        
        Args:
            llm_type: Type of LLM (OpenAI, Anthropic, Groq, GoogleAI, LocalModel)
            model_name: Name of the model to use
            max_tokens: Maximum number of tokens to generate
            seed: Random seed for reproducibility
            temperature: Temperature for generation
        """
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


def load_ndex_credentials() -> Tuple[str, str]:
    """Load NDEx credentials from environment variables"""
    username = os.environ.get("NDEX_USERNAME")
    password = os.environ.get("NDEX_PASSWORD")
    return username, password


def load_from_ndex(uuid: str) -> Tuple[nx.Graph, str]:
    """Load network from NDEx and convert to NetworkX
    
    Args:
        uuid: NDEx network UUID
        
    Returns:
        Tuple of (NetworkX graph, network name)
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
    
    # Add network attributes
    G.graph['name'] = cx2_network.get_name()
    for attr_name, attr_value in cx2_network.get_network_attributes().items():
        G.graph[attr_name] = attr_value
    
    # Add nodes with attributes
    for node_id, node_attrs in cx2_network.get_nodes().items():
        # Use numeric ID as the node identifier in NetworkX
        node_id_str = str(node_id)
        
        # Get node name
        node_name = node_attrs.get('n', '')
        
        # Extract attributes from 'v' if present
        v_attrs = {}
        if 'v' in node_attrs and isinstance(node_attrs['v'], dict):
            v_attrs = node_attrs['v']
        
        # Prepare node attributes dict
        attrs = {
            'id': node_id,
            'name': node_name,
            'x': node_attrs.get('x', 0),
            'y': node_attrs.get('y', 0)
        }
        
        # Add all attributes from 'v'
        for k, v in v_attrs.items():
            attrs[k] = v
        
        # Add node to graph with all attributes
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
    
    return G


def analyze_network(G: nx.Graph) -> Dict[str, Any]:
    """
    Analyze a network to extract information for hypothesis generation
    
    Args:
        G: NetworkX graph
        
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
    
    # Find viral protein node (source of propagation)
    viral_protein_name = G.graph.get('viral_protein_name', None)
    viral_protein_id = G.graph.get('viral_protein_id', None)
    
    stats['viral_protein'] = {
        'name': viral_protein_name,
        'id': viral_protein_id
    }
    
    # Get nodes with propagation weights
    weighted_nodes = {}
    for node, attrs in G.nodes(data=True):
        if 'propagation_weight' in attrs:
            weight = attrs['propagation_weight']
            name = attrs.get('name', attrs.get('GeneSymbol', node))
            weighted_nodes[node] = {
                'id': node,
                'name': name,
                'weight': weight
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
    
    return stats


def generate_hypothesis_prompt(network_stats: Dict[str, Any], n_hypotheses: int = 3) -> str:
    """
    Generate a prompt for hypothesis generation based on network analysis
    
    Args:
        network_stats: Dictionary with network analysis results
        n_hypotheses: Number of hypotheses to generate
        
    Returns:
        Prompt for the LLM
    """
    # Extract information from network stats
    viral_protein = network_stats['viral_protein']['name'] or "Unknown viral protein"
    top_nodes = network_stats['top_nodes'][:20]  # Use top 20 nodes in prompt
    
    # Format top nodes for prompt
    top_nodes_text = "\n".join([
        f"- {node['name']} (weight: {node['weight']:.4f})"
        for node in top_nodes
    ])
    
    # Create prompt
    prompt = f"""
Based on a dengue virus protein interaction network analysis for {viral_protein}, I need to generate {n_hypotheses} scientific hypotheses.

The propagation analysis identified the following top human proteins with the highest propagation weights (most closely connected to the viral protein):

{top_nodes_text}

For each hypothesis, please:
1. Propose a specific testable hypothesis about how {viral_protein} might interact with these human proteins
2. Focus on potential mechanisms of viral pathogenesis, immune evasion, or drug targeting
3. Explain the biological rationale based on the proteins involved
4. Suggest what experiments could validate this hypothesis

Format each hypothesis as a JSON object with the following fields:
- "hypothesis": A clear, concise statement of the hypothesis (1-2 sentences)
- "rationale": Biological reasoning behind the hypothesis (2-3 sentences) 
- "proteins_involved": List of key proteins mentioned in the hypothesis
- "experimental_validation": Brief description of how this could be tested
- "confidence": A value from 1-5 indicating your confidence in this hypothesis (5 being highest)

Return ONLY a valid JSON array of hypothesis objects. Do not include any explanation or other text outside the JSON.
"""
    
    return prompt


def generate_hypotheses(network_stats: Dict[str, Any], llm_wrapper: LLMWrapper, n_hypotheses: int = 3) -> List[Dict[str, Any]]:
    """
    Generate hypotheses using LLM based on network analysis
    
    Args:
        network_stats: Dictionary with network analysis results
        llm_wrapper: LLMWrapper for LLM query
        n_hypotheses: Number of hypotheses to generate
        
    Returns:
        List of hypothesis dictionaries
    """
    # Generate prompt for the LLM
    prompt = generate_hypothesis_prompt(network_stats, n_hypotheses)
    
    # System context for the LLM
    context = """
You are a virology and systems biology expert specializing in dengue virus research. 
Your task is to generate scientifically plausible hypotheses based on protein interaction network analysis.
Focus on mechanistic insights that could explain viral pathogenesis or suggest new therapeutic approaches.
Return your response in valid JSON format only.
"""
    
    # Query the LLM
    print(f"Generating {n_hypotheses} hypotheses with the LLM...")
    response = llm_wrapper.query(context, prompt)
    
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
            required_fields = ['hypothesis', 'rationale', 'proteins_involved', 'experimental_validation', 'confidence']
            for field in required_fields:
                if field not in hypothesis:
                    hypothesis[field] = f"Missing {field}"
            
            # Add hypothesis ID
            hypothesis['id'] = f"H{i+1}"
        
        return hypotheses
    
    except json.JSONDecodeError as e:
        print(f"Error parsing LLM response as JSON: {e}")
        print("LLM response:")
        print(response)
        
        # Return a placeholder in case of failure
        return [{
            "id": "H1",
            "hypothesis": "Failed to generate valid hypotheses",
            "rationale": f"LLM response could not be parsed as JSON: {str(e)}",
            "proteins_involved": [],
            "experimental_validation": "N/A",
            "confidence": 0
        }]


def create_hypothesis_network(hypotheses: List[Dict[str, Any]], source_stats: Dict[str, Any]) -> CX2Network:
    """
    Create a CX2 network containing hypotheses as nodes
    
    Args:
        hypotheses: List of hypothesis dictionaries
        source_stats: Source network statistics
        
    Returns:
        CX2Network object
    """
    # Create a new CX2 network
    cx2_network = CX2Network()
    
    # Set network attributes
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    viral_protein = source_stats['viral_protein']['name'] or "Unknown viral protein"
    network_name = f"Dengue {viral_protein} Hypotheses - {timestamp}"
    
    cx2_network.set_name(network_name)
    cx2_network.add_network_attribute('description', 
                                      f"Hypotheses generated for {viral_protein} propagation network")
    cx2_network.add_network_attribute('viral_protein', viral_protein)
    cx2_network.add_network_attribute('source_network', source_stats['name'])
    cx2_network.add_network_attribute('generation_timestamp', timestamp)
    
    # Add attribute declarations
    attr_declarations = {
        'nodes': {
            'name': {'d': 'string'},
            'hypothesis_text': {'d': 'string'},
            'rationale': {'d': 'string'},
            'experimental_validation': {'d': 'string'},
            'confidence': {'d': 'integer'},
            'node_type': {'d': 'string'},
            'x': {'d': 'double'},
            'y': {'d': 'double'}
        },
        'edges': {
            'interaction': {'d': 'string'},
        }
    }
    cx2_network.set_attribute_declarations(attr_declarations)
    
    # Create central node for viral protein
    center_id = 1
    cx2_network.add_node(center_id, name=viral_protein)
    cx2_network.add_node_attribute(center_id, 'node_type', 'viral_protein')
    cx2_network.add_node_attribute(center_id, 'x', 0)
    cx2_network.add_node_attribute(center_id, 'y', 0)
    
    # Add hypothesis nodes in a circle around the center
    n_hypotheses = len(hypotheses)
    radius = 300
    
    for i, hypothesis in enumerate(hypotheses):
        # Calculate position in a circle
        angle = 2 * 3.14159 * i / n_hypotheses
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        
        # Create node for hypothesis
        node_id = i + 2  # Start from 2 since center is 1
        node_name = f"Hypothesis {hypothesis['id']}"
        
        cx2_network.add_node(node_id, name=node_name)
        
        # Add node attributes
        cx2_network.add_node_attribute(node_id, 'hypothesis_text', hypothesis['hypothesis'])
        cx2_network.add_node_attribute(node_id, 'rationale', hypothesis['rationale'])
        cx2_network.add_node_attribute(node_id, 'experimental_validation', hypothesis['experimental_validation'])
        cx2_network.add_node_attribute(node_id, 'confidence', hypothesis['confidence'])
        cx2_network.add_node_attribute(node_id, 'node_type', 'hypothesis')
        cx2_network.add_node_attribute(node_id, 'x', x)
        cx2_network.add_node_attribute(node_id, 'y', y)
        
        # Create proteins involved as nodes and connect to hypothesis
        proteins_involved = hypothesis.get('proteins_involved', [])
        
        for j, protein in enumerate(proteins_involved):
            if isinstance(protein, str) and protein.strip():
                # Check if protein node already exists
                protein_id = None
                for existing_id, attrs in cx2_network.get_nodes().items():
                    if 'n' in attrs and attrs['n'] == protein and 'v' in attrs and attrs['v'].get('node_type') == 'protein':
                        protein_id = existing_id
                        break
                
                # If protein node doesn't exist, create it
                if protein_id is None:
                    protein_id = len(cx2_network.get_nodes()) + 1
                    
                    # Calculate position near the hypothesis node
                    protein_angle = angle + (j * 0.3 - 0.5)  # Spread proteins around hypothesis
                    protein_radius = radius * 1.3  # Place slightly outside the hypothesis circle
                    protein_x = protein_radius * math.cos(protein_angle)
                    protein_y = protein_radius * math.sin(protein_angle)
                    
                    cx2_network.add_node(protein_id, name=protein)
                    cx2_network.add_node_attribute(protein_id, 'node_type', 'protein')
                    cx2_network.add_node_attribute(protein_id, 'x', protein_x)
                    cx2_network.add_node_attribute(protein_id, 'y', protein_y)
                
                # Connect protein to hypothesis
                cx2_network.add_edge(protein_id, node_id)
                cx2_network.add_edge_attribute(protein_id, node_id, 'interaction', 'involved_in')
        
        # Connect hypothesis to center
        cx2_network.add_edge(center_id, node_id)
        cx2_network.add_edge_attribute(center_id, node_id, 'interaction', 'has_hypothesis')
    
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
    parser = argparse.ArgumentParser(description='Generate hypotheses from propagation networks')
    
    # Required arguments
    parser.add_argument('--uuid', type=str, required=True, help='NDEx UUID of propagation network')
    
    # Optional arguments
    parser.add_argument('--output-dir', type=str, default='.', help='Output directory for results')
    parser.add_argument('--n-hypotheses', type=int, default=3, help='Number of hypotheses to generate')
    parser.add_argument('--llm-type', type=str, default='OpenAI', 
                        choices=['OpenAI', 'Anthropic', 'Groq', 'GoogleAI', 'LocalModel'],
                        help='Type of LLM to use')
    parser.add_argument('--model-name', type=str, default='gpt-4', help='Name of the model to use')
    parser.add_argument('--max-tokens', type=int, default=2048, help='Maximum tokens for LLM response')
    parser.add_argument('--temperature', type=float, default=0.7, help='Temperature for LLM generation')
    parser.add_argument('--seed', type=int, default=42, help='Random seed for reproducibility')
    parser.add_argument('--upload-to-ndex', action='store_true', help='Upload networks to NDEx')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Load network from NDEx
    print(f"Loading network {args.uuid} from NDEx...")
    G, network_name = load_from_ndex(args.uuid)
    print(f"Loaded network '{network_name}' with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    
    # Analyze network
    print("Analyzing network...")
    network_stats = analyze_network(G)
    
    # Create LLM wrapper
    llm_wrapper = LLMWrapper(
        llm_type=args.llm_type,
        model_name=args.model_name,
        max_tokens=args.max_tokens,
        seed=args.seed,
        temperature=args.temperature
    )
    
    # Generate hypotheses
    print(f"Generating {args.n_hypotheses} hypotheses using {args.llm_type} {args.model_name}...")
    hypotheses = generate_hypotheses(network_stats, llm_wrapper, args.n_hypotheses)
    
    # Save hypotheses to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    viral_protein = network_stats['viral_protein']['name'] or "Unknown"
    filename = f"hypotheses_{viral_protein}_{timestamp}.json"
    filepath = os.path.join(args.output_dir, filename.replace(" ", "_"))
    
    with open(filepath, 'w') as f:
        json.dump(hypotheses, f, indent=2)
    
    print(f"Saved {len(hypotheses)} hypotheses to {filepath}")
    
    # Display generated hypotheses
    print("\nGenerated Hypotheses:")
    for h in hypotheses:
        print(f"\n[{h['id']}] {h['hypothesis']}")
        print(f"Confidence: {h['confidence']}/5")
        print(f"Proteins: {', '.join(h['proteins_involved'])}")
    
    # Create hypothesis network
    print("\nCreating hypothesis network...")
    
    # Import math module (needed for create_hypothesis_network)
    import math
    
    hypothesis_network = create_hypothesis_network(hypotheses, network_stats)
    
    # Upload to NDEx if requested
    if args.upload_to_ndex:
        print("Uploading hypothesis network to NDEx...")
        uuid = upload_to_ndex(hypothesis_network)
        print(f"Upload successful. Network UUID: {uuid}")
        
        # Save UUID to file
        uuid_file = os.path.join(args.output_dir, f"hypothesis_network_uuid_{timestamp}.txt")
        with open(uuid_file, 'w') as f:
            f.write(uuid)
        print(f"Saved network UUID to {uuid_file}")
    
if __name__ == "__main__":
    main()
