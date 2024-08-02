import csv
import xml.etree.ElementTree as ET
from io import StringIO

def csv_to_string(filepath):
    """Read a CSV file and convert it to a string representation."""
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        lines = []
        for row in reader:
            line = ', '.join(f'{key}: {value}' for key, value in row.items())
            lines.append(line)
    return '\n'.join(lines)

def csv_to_xml(data, root_tag="root"):
    # Parse the JSON string into CSV rows
    csv_data = StringIO(data)
    reader = csv.reader(csv_data)
    rows = list(reader)
    # Convert formatted rows to XML
    root = ET.Element(root_tag)
    headers = rows[0]
    
    for row in rows[1:]:
        item = ET.Element("item")
        for header, value in zip(headers, row):
            child = ET.SubElement(item, header.strip())
            child.text = value if value is not None else ''
        root.append(item)
    
    return ET.tostring(root, encoding='unicode')