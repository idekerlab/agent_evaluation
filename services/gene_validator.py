from collections import defaultdict
import csv

class GeneValidator:
    def __init__(self, file_path):
        self.gene_symbol_set = set()
        self.alias_map = defaultdict(str)

        with open(file_path, 'r') as file:
            reader = csv.reader(file, delimiter='\t')
            next(reader)  # Skip header row
            for cells in reader:
                if cells[0]:
                    gene = cells[0].upper()
                    self.gene_symbol_set.add(gene)

                    if len(cells) > 1 and cells[1]:
                        previous_symbols = cells[1].split(", ")
                        for symbol in previous_symbols:
                            self.alias_map[symbol.upper()] = gene

                    if len(cells) > 2 and cells[2]:
                        alias_symbols = cells[2].split(", ")
                        for alias in alias_symbols:
                            self.alias_map[alias.upper()] = gene

    def validate_human_genes(self, genes):
        official_genes = set()
        invalid_genes = set()
        updated_genes = {}

        for raw_term in genes:
            # print(f'validate Hugo symbol for {raw_term}')
            term = raw_term.upper()
            if term in self.gene_symbol_set:
                official_genes.add(term)
            elif term in self.alias_map:
                official_gene = self.alias_map[term]
                official_genes.add(official_gene)
                updated_genes[term] = official_gene
                invalid_genes.add(term)
            else:
                invalid_genes.add(term)

        return {
            'official_genes': official_genes,
            'invalid': invalid_genes,
            'updated_genes': updated_genes
        }