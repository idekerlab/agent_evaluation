import csv
import logging
from io import StringIO, BytesIO
import re
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import base64

from app.sqlite_database import SqliteDatabase
from services.gene_validator import GeneValidator
from models.judgment_space import JudgmentSpace

# Configure logging
logger = logging.getLogger(__name__)

def preprocess_properties(properties: Dict, object_type: str, object_specifications: Dict) -> Dict:
    """Preprocess object properties, handling CSV data formatting."""
    logger.info(f"Preprocessing properties for {object_type}")
    try:
        for prop_name, prop_spec in object_specifications[object_type]['properties'].items():
            if prop_spec.get('type') == 'csv' and properties.get(prop_name):
                logger.debug(f"Processing CSV data for property: {prop_name}")
                csv_data = StringIO(str(properties[prop_name]))
                reader = csv.reader(csv_data)
                rows = list(reader)

                # Format numeric values in CSV content, 2 decimal places
                from app.handlers.form_handlers import format_numeric_values
                formatted_rows = format_numeric_values(rows)
                properties[prop_name] = formatted_rows

        return properties
    except Exception as e:
        logger.error(f"Error preprocessing properties for {object_type}: {str(e)}")
        raise

def convert_to_csv(data: List[List[str]]) -> str:
    """Convert list of lists to CSV string."""
    output = StringIO()
    csv_writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
    
    # Write each row from the list of lists to the CSV
    for row in data:
        csv_writer.writerow(row)

    csv_content = output.getvalue()
    output.close()

    return csv_content

def process_object_links(db: SqliteDatabase, properties: Dict, object_specifications: Dict, object_type: str) -> Dict:
    """Process object links in properties, getting names for linked objects."""
    logger.info(f"Processing object links for {object_type}")
    link_names = {}
    try:
        for prop_name, prop_spec in object_specifications[object_type]['properties'].items():
            if prop_name not in ['object_id', 'created', 'name'] and prop_name in properties:
                if prop_spec['view'] == 'object_link':
                    obj_id = properties[prop_name]
                    logger.debug(f"Processing single link for {prop_name}: {obj_id}")
                    link_names[obj_id] = get_link_name(db, obj_id)
                elif prop_spec['view'] == 'list_of_object_links':
                    logger.debug(f"Processing multiple links for {prop_name}")
                    for obj_id in properties[prop_name]:
                        link_names[obj_id] = get_link_name(db, obj_id)
        return link_names
    except Exception as e:
        logger.error(f"Error processing object links for {object_type}: {str(e)}")
        raise

def get_link_name(db: SqliteDatabase, obj_id: str) -> str:
    """Get the name of a linked object."""
    if not obj_id:
        logger.warning("Attempted to get link name for empty object ID")
        return "[Missing Link]"
    try:
        linked_object_properties, obj_type = db.load(obj_id)
        if not linked_object_properties:
            logger.warning(f"No properties found for object ID: {obj_id}")
            return f"[Missing {obj_type or 'Object'}: {obj_id}]"
        name = linked_object_properties.get('name')
        if not name:
            logger.warning(f"No name property for object ID: {obj_id}")
            return f"[Unnamed {obj_type or 'Object'}: {obj_id}]"
        logger.debug(f"Retrieved name for {obj_id}: {name}")
        return name
    except Exception as e:
        logger.warning(f"Failed to get link name for {obj_id}: {str(e)}")
        return f"[Invalid Link: {obj_id}]"

def handle_hypothesis(properties: Dict) -> Dict:
    """Process hypothesis text to validate gene symbols."""
    logger.info("Processing hypothesis text")
    logger.debug(f"Hypothesis properties received: {properties.keys()}")
    
    try:
        # First check if the hypothesis has properties_involved directly
        if 'proteins_involved' in properties:
            logger.info("Using proteins_involved field directly")
            if isinstance(properties['proteins_involved'], str):
                # If it's a string that might be semicolon separated
                gene_symbols = [g.strip() for g in properties['proteins_involved'].split(';')]
                properties['gene_symbols'] = gene_symbols
                logger.debug(f"Found gene symbols from proteins_involved: {gene_symbols}")
                return properties
            elif isinstance(properties['proteins_involved'], list):
                properties['gene_symbols'] = properties['proteins_involved']
                logger.debug(f"Found gene symbols from proteins_involved list: {properties['proteins_involved']}")
                return properties
        
        # Get hypothesis text from various possible fields
        hypo_text = None
        potential_fields = [
            "hypothesis_text", 
            "alternative_hypothesis", 
            "null_hypothesis", 
            "rationale"
        ]
        
        for field in potential_fields:
            if field in properties and properties[field]:
                logger.debug(f"Using {field} as hypothesis text")
                hypo_text = properties[field]
                break
        
        if not hypo_text:
            logger.warning("No hypothesis text found in any expected field")
            properties['gene_symbols'] = []
            return properties
            
        file_path = "data/hgnc_genes.tsv"

        # Remove punctuation and parentheses, but keep hyphens
        cleaned_text = re.sub(r'[^\w\s-]', '', hypo_text)
        # Split into words
        words = re.split(r'\s+', cleaned_text)

        validator = GeneValidator(file_path)
        result = validator.validate_human_genes(words)
        
        properties['gene_symbols'] = result['official_genes']
        logger.debug(f"Found gene symbols: {result['official_genes']}")
        return properties
    except KeyError as e:
        logger.warning(f"Missing key in hypothesis: {str(e)}")
        # Don't fail on missing keys, just return the original properties
        properties['gene_symbols'] = []
        return properties
    except Exception as e:
        logger.error(f"Error processing hypothesis: {str(e)}", exc_info=True)
        # Return the original properties instead of failing
        properties['gene_symbols'] = []
        return properties

def generate_judgment_space_visualization(judgment_space: JudgmentSpace) -> Tuple[Optional[str], Optional[str]]:
    """Generate visualization for judgment space data."""
    if not judgment_space.review_sets:
        return None, None

    try:
        judgment_space.generate_reviewer_judgment_dict()
        data = np.array(list(judgment_space.reviewer_judgment_dict.values()))
        
        plt.figure(figsize=(12, 8))
        sns.heatmap(data, cmap='YlGnBu', cbar_kws={'label': 'Judgment Score'})
        plt.title('Reviewer Judgment Heatmap')
        plt.xlabel('Judgment Vector Index')
        plt.ylabel('Reviewer Index')
        
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='svg')
        img_buffer.seek(0)
        svg_string = img_buffer.getvalue().decode()
        
        return svg_string, "image/svg+xml"
    except Exception as e:
        print(f"Error generating visualization: {str(e)}")
        return None, None
