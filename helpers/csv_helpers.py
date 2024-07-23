import csv

def csv_to_string(filepath):
    """Read a CSV file and convert it to a string representation."""
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        lines = []
        for row in reader:
            line = ', '.join(f'{key}: {value}' for key, value in row.items())
            lines.append(line)
    return '\n'.join(lines)