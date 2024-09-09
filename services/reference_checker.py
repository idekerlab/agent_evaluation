from Bio import Entrez
import openai
import requests
import pandas as pd
from urllib import request
import urllib.parse as parse
from models.llm import LLM
from models.dataset import Dataset
from models.agent import Agent
from models.hypothesis import Hypothesis
from models.analysis_run import AnalysisRun
from helpers.safe_dict import SafeDict
from helpers.parse_text import parse_text_to_json
from app.config import load_constant_from_config
import os 
import json
import re



def get_genes(dict_value, verbose=False):
    '''
    dict_value: dictionary parsed from a previous LLM with 'proteins' and 'analysis' key
    '''
    if 'proteins' not in dict_value.keys():
        if verbose:
            print("No proteins found in the dict_value")
        return ['Unknown']
    else:
        return dict_value['proteins']
    

def get_functions_from_paragraph(db,  dict_value, agent_id,verbose=False):
    '''
    dict_value: dictionary parsed from a previous LLM with 'proteins' and 'analysis' key
    '''
    paragraph = dict_value['analysis']
    query = f"""
I would like to search PubMed to find supporting evidence for the statements in a paragraph. Give me a maximum of 3 keywords related to the functions or biological processes in the statements. 

Example paragraph:  Involvement of pattern recognition receptors: TLR1, TLR2, and TLR3 are part of the Toll-like receptor family, which recognize pathogen-associated molecular patterns and initiate innate immune responses. NOD2 and NLRP3 are intracellular sensors that also contribute to immune activation.
Example response: immune response,receptors,pathogen

Please don't include gene symbols. Please order keywords by their importance in the paragraph, from high importance to low importance. Return the keywords as a comma separated list without spaces. If there are no keywords matching the criteria, return \"Unknown\" 

Please find keywords for this paragraph:
{paragraph}
    """
    agent = Agent.load(db, agent_id)
    # Load the LLM associated with the agent
    llm = LLM.load(db, agent.llm_id)
    if not llm:
        raise ValueError("LLM not found")
    # Generate hypothesis text using the LLM
    result = llm.query(agent.context, query)
    if result is not None:
        if verbose:
            print("Query: ", query)
            print("Result: ", result)
        if result.lower()=='unknown':
            return ['Unknown']
        return [keyword.strip() for keyword in result.split(",")]
        
def is_formated_gene_symbol(symbol):
    # A simple regex to check if the gene symbol is alphanumeric and may contain underscores
    return re.match(r'^\w+$', symbol)
def get_aliased_symbol(gene_symbol):
    encoded_gene_symbol = parse.quote(gene_symbol)  # URL encode the gene symbol
    if not is_formated_gene_symbol(gene_symbol):
        return gene_symbol
    try:
        url = f'http://mygene.info/v3/query?q=symbol:{encoded_gene_symbol}&species=human'
        with request.urlopen(url) as requested:
            result_dict = json.loads(requested.read().decode())

        if len(result_dict['hits']) == 0:
            url = f'http://mygene.info/v3/query?q=alias:{encoded_gene_symbol}&species=human'
            with request.urlopen(url) as requested:
                result_dict = json.loads(requested.read().decode())

            if len(result_dict['hits']) == 0:
                return None
            else:
                return result_dict['hits'][0]['symbol']
        else:
            return gene_symbol
    except Exception as e:
        print("Error detail: ", e)
        return None
    
def get_keywords_combinations(db,  dict_value, agent_id, verbose=False):
    # get genes
    genes = get_genes(dict_value, verbose)
    if genes[0]=='Unknown':
            return None, [], functions
    else: 
        # check aliases
        genes = list(filter(None, [get_aliased_symbol(gene) for gene in genes]))

    functions = get_functions_from_paragraph(db,  dict_value, agent_id, verbose)

    # format
    if (genes is None) or len(genes)==0:
        return None, [], functions

    if functions is None or functions[0]=='Unknown': # CH updated the condition
            return None, genes, []
    
    #Create a search query for genes/functions, allowing them to appear in anywhere (because later we will check if they are in title or abstract)
    gene_query = " OR ".join(["%s[Title/Abstract]"%gene for gene in genes])
    function_query = " OR ".join(["%s[Title/Abstract]"%function for function in functions])

    # Construct the final search query:
    # - Includes genes and functions 
    # - Filters to include only articles with abstracts
    # - Limits the search to human studies
    # - Excludes retracted publications
    keywords = "(%s) AND (%s)"%(gene_query, function_query)

    return keywords, genes, functions
    
def get_mla_citation(doi):
    url = f'https://api.crossref.org/works/{doi}'
    headers = {'accept': 'application/json'}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        #print(data)
        item = data['message']
        
        authors = item['author']
        formatted_authors = []
        for author in authors:
            formatted_authors.append(f"{author['family']}, {author.get('given', '')}")
        authors_str = ', '.join(formatted_authors)
        
        title = item['title'][0]
        container_title = item['container-title'][0]
        year = item['issued']['date-parts'][0][0]
        volume = item.get('volume', '')
        issue = item.get('issue', '')
        page = item.get('page', '')
        
        mla_citation = f"{authors_str}. \"{title}.\" {container_title}"
        if volume or issue:
            mla_citation += f", vol. {volume}" if volume else ''
            mla_citation += f", no. {issue}" if issue else ''
        mla_citation += f", {year}, pp. {page}."
        
        return mla_citation

## 12/18/2023 IL updated the following main function
def get_mla_citation_from_pubmed_id(paper_dict):
    article = paper_dict['MedlineCitation']['Article']
    #print(article.keys())
    authors = article['AuthorList']
    formatted_authors = []
    for author in authors:
        try:
            last_name = author['LastName'] if author['LastName'] is not None else ''
        except:
            last_name = ''
        try:
            first_name = author['ForeName'] if author['ForeName'] is not None else ''
        except:
            first_name = ''
        formatted_authors.append(f"{last_name}, {first_name}")
    authors_str = ', '.join(formatted_authors)

    title = article['ArticleTitle']
    journal = article['Journal']['Title']
    year = article['Journal']['JournalIssue']['PubDate']['Year']
    try:
        page = article['Pagination']['MedlinePgn']
    except:
        page = " "
    mla_citation = f"{authors_str}. \"{title}\" {journal}"
    if "Volume" in article['Journal']['JournalIssue']['PubDate']:
        volume = article['Journal']['JournalIssue']['PubDate']['Volume']
        mla_citation += f", vol. {volume}" if volume else ''
    elif "Issue" in article['Journal']['JournalIssue']['PubDate']:
        issue = article['Journal']['JournalIssue']['PubDate']['Issue']
        mla_citation += f", no. {issue}" if issue else ''
    mla_citation += f", {year}, pp. {page}"
    no_doi = True
    if "ArticleIdList" in paper_dict['PubmedData'].keys():
        for other_id in paper_dict['PubmedData']['ArticleIdList']:
            if other_id.attributes['IdType']=='doi':
                doi = str(other_id)
                mla_citation += f", doi: https://doi.org/{doi}"
                no_doi = False
    if no_doi:
        mla_citation += "."
    return mla_citation

def get_citation(paper):
    names = ",".join([author['name'] for author in paper['authors']])
    corrected_title = paper['title']
    journal = paper['journal']['name']
    pub_date = paper['publicationDate']
    if 'volume' in paper['journal'].keys(): 
        volume = paper['journal']['volume'].strip()
    else:
        volume = ''
    if 'pages' in paper['journal'].keys():
        pages = paper['journal']['pages'].strip()
    else:
        doi = paper['externalIds']['DOI']
        pages = doi.strip().split(".")[-1]
    citation = f"{names}. {corrected_title} {journal} {volume} ({pub_date[0:4]}):{pages}"
    return citation

## check if the title of the paper matches the paragraph
def check_title_matching(db, paper,  dict_value, agent_id,  n=10, verbose=False):
    paragraph = dict_value['analysis']
    sentences = paragraph.split(".")
    sentences = [sentence.strip() for sentence in sentences if len(sentence.strip())>0]
    indexed_sentences = {i: sentence for i, sentence in enumerate(sentences)}
    # load agent 
    agent = Agent.load(db, agent_id)
    if not agent:
        raise ValueError("Agent not found in reference_checker")
    llm = LLM.load(db, agent.llm_id)
    if not llm:
        raise ValueError("LLM not found")
    
    try:
        title = paper['MedlineCitation']['Article']['ArticleTitle']
    except (KeyError, IndexError) as e:
        if verbose:
            print("Error in getting title from paper.")
            print("Error detail: ", e)
        return False

    message = f"""
I have a paragraph that was separated into sentences. Each sentence is indexed.
Paragraph:
{indexed_sentences}

a scientific paper title
Title:
{title}

Please analyze whether this title directly and explicitly supports any sentence in the paragraph. Please print yes or no at the begining of your response. 
"""    
    try:
        result = llm.query(agent.context, message)
    except Exception as e:
        print("Error in query title matching")
        print("Error detail: ", e)
        result = None
        return False
    if result is not None:
        if verbose:
            print("Query: \n", message)
            print("Result: \n", result)
        if result[:3].lower()=='yes':
    
            return True
        else:
            return False


def check_abstract_match(db, paper,  dict_value, agent_id,  n=10, verbose=False):
    paragraph = dict_value['analysis']
    # separate paragraph into sentences. and index the sentences
    sentences = paragraph.split(".")
    sentences = [sentence.strip() for sentence in sentences if len(sentence.strip())>0]
    indexed_sentences = {i: sentence for i, sentence in enumerate(sentences)}
    # load agent 
    agent = Agent.load(db, agent_id)
    if not agent:
        raise ValueError("Agent not found in reference_checker")
    llm = LLM.load(db, agent.llm_id)
    if not llm:
        raise ValueError("LLM not found")
    try:
        abstract = "\n".join(paper['MedlineCitation']['Article']['Abstract']['AbstractText'])
    except (KeyError, IndexError) as e:
        print("Error in getting abstract from paper.")
        print("Error detail: ", e)
        return False
    message = f"""
I have a paragraph that was separated into sentences. Each sentence is indexed.
Paragraph:
{indexed_sentences}

and an abstract.
Abstract:
{abstract}

Please analyze whether this abstract directly supports any assertion in the paragraph. 
Follow these steps:

- For each indexed sentence, state whether it is directly supported by findings in the abstract.
- If a sentence is supported, quote the specific part of the abstract that provides this support.
- If a sentence is not supported, briefly explain why.
- After analyzing all sentences, decide whether the abstract directly supports any parts of the paragraph.
- Present your findings in the following format:
    - If any sentence supports the paragraph, print "yes" at the beginning of your response. And provide a dictionary containing indexes for the supported sentences and the list of quoted sentences from the supporting abstract
    - e.g.,'Yes \n supporting sentences: {{\"1\": [\"A variety of viruses can induce the expression of IFIT3, which in turn inhibits the replication of viruses, with the underlying mechanism showing its crucial role in antiviral innate immunity.\"], \"3\": [\"<quoted abstract text>\"]}}'
    - If no sentences are supported at all,  print "no" at the beginning of your response.
    - Then print your analysis.  
        """
        
    try:
        result = llm.query(agent.context, message)
    except Exception as e:
        print("Error in query abstract matching")
        print("Error detail: ", e)
        result = None
    if result is not None:
        if verbose:
            print("Query: \n", message)
            print("Result: \n", result)
        if result[:3].lower()=='yes':
            dict_str = result.split("supporting sentences:")[-1].split("\n")[0]
            # Parsing the cleaned string as a JSON object
            try:
                supporting_sentences_dict = json.loads(dict_str)
            except json.JSONDecodeError as e:
                supporting_sentences_dict = {"error": f"Failed to parse JSON from abstract match: {str(e)}"}
            return True, supporting_sentences_dict
        else:
            return False, {}

## 12/18/2023 IL updated the following main function
def get_genes_in_abstract(paper, genes, verbose=False):
    ## load config for openai query
    try:
        title = paper['MedlineCitation']['Article']['ArticleTitle']
        abstract = paper['MedlineCitation']['Article']['Abstract']['AbstractText'][0]
    except (KeyError, IndexError) as e:

        print("Error in getting abstract from paper.")
        print("Error detail: ", e)
        return []
    gene_counts = 0
    genes_in_abstract = []
    for gene in genes:
        if gene.lower() in abstract.lower():
            gene_counts += 1
            genes_in_abstract.append(gene)
    if verbose:
        print("Title: ", title)
        print("Abstract: ", abstract)
        print("Genes: ", ", ".join(genes_in_abstract))
        print(" ")
    return genes_in_abstract
    
def get_n_citation(paper):
    links = Entrez.elink(dbfrom="pubmed", id=paper["MedlineCitation"]["PMID"], linkname="pubmed_pubmed_citedin")
    link_list = []
    record = Entrez.read(links)
    if len(record[0][u'LinkSetDb'])==0:
        return 0
    records = record[0][u'LinkSetDb'][0][u'Link']
    for link in records:
        link_list.append(link[u'Id'])
    return len(link_list)


def sort_paper_by_n_genes_in_abstract(papers, genes, verbose=False):
    return sorted(papers, key=lambda paper: (-len(get_genes_in_abstract(paper, genes, verbose=verbose)), -get_n_citation(paper)))


def search_pubmed(keywords, email, sort_by='relevance', retmax=10): ### CH: sort by relevance
    Entrez.email = email
    # makesure it is searching paper that has abstract and is not retracted, and they are talking about human
    search_query = f"{keywords} AND (hasabstract[text]) AND humans[mh] NOT Retracted Publication[pt]"
    search_handle = Entrez.esearch(db='pubmed', term=search_query, sort=sort_by, retmax=retmax)
    search_results = Entrez.read(search_handle)
    search_handle.close()

    id_list = search_results['IdList']

    if not id_list:
        print("No results found.")
        return []

    fetch_handle = Entrez.efetch(db='pubmed', id=id_list, retmode='xml')
    articles = Entrez.read(fetch_handle)['PubmedArticle']
    fetch_handle.close()

    return articles

def get_papers(keywords, n, email):
    total_papers = []
    #for keyword in keywords:
    print("Searching Keyword :", keywords)
    try:
        pubmed_queried_keywords= search_pubmed(keywords, email=email)
        print("%d papers are found"%len(pubmed_queried_keywords))
        total_papers += list(pubmed_queried_keywords[:n])

    except:
        print("No paper found")
        pass
    return total_papers

# def get_references_for_paragraph(db, dict_value, agent_id, email, n=5, papers_query=20, verbose=False):
#     paragraph = dict_value['analysis']
#     if verbose:
#         print("""Extracting keywords from paragraph\nParagraph:\n%s"""%paragraph)
#         print("="*75)
#     # get keywords
#     keywords, genes, functions= get_keywords_combinations(db,  dict_value, agent_id, verbose=verbose)
#     if keywords is None:
#         print("No keyword generated skip referencing")
#         return None
#     if verbose:
#         print("PubMed Keywords: ", keywords)
#     print("Serching paper with keywords...")
#     # search papers via pubmed
#     papers = search_pubmed(keywords, email, retmax=papers_query)
#     print("%d references are queried"%(len(papers)))
    
#     if len(papers)==0:
#         print("No paper searched!!")
#     # sort the papers by the number of query genes in the abstract
#     sorted_papers = sort_paper_by_n_genes_in_abstract(papers, genes, verbose=verbose)
    
#     #title_matchings = check_title_matching(paper, paragraph, config, verbose=verbose) for paper in sorted_papers]
#     title_matching_papers = []
#     genes_to_be_searched = genes.copy() # copy the genes to be searched

#     # prioritize the papers that have the most genes in the abstract and verify their relavence
#     # first check verified in title then in abstract
#     for paper in sorted_papers:
#         # iterate the genes in the search list to find relavent paper 
#         # reach to the end when there is no remaining gene to be searched
#         genes_in_abstract = get_genes_in_abstract(paper, genes,verbose=False)
#         title = paper['MedlineCitation']['Article']['ArticleTitle']
#         if len(genes)==1:
#             single_gene = True
#         else:
#             single_gene = False
#         # find if the title matching the paragraph
#         if len(genes_in_abstract)>=1:
#             title_matching = check_title_matching(db, paper,  dict_value, agent_id, verbose=verbose)
#             if title_matching:

#                 title_matching_papers.append(paper) 
#                 if verbose:
#                     print(title, genes_in_abstract, get_n_citation(paper))
#                 # remove the genes that are found in the abstract
#                 for gene_in_abstract in genes_in_abstract:
#                     if gene_in_abstract in genes_to_be_searched:
#                         genes_to_be_searched.remove(gene_in_abstract)
#                 #print(title)
#     print("The number of title matching paper: %d"%len(title_matching_papers))

#     paper_for_references = []
#     reference_with_sentencesIDs = [] # CH: added list of support along with paper
#     genes_to_be_searched = genes.copy()
#     # in the list of title_matching_papers, find the abstract also matches the paragraph
#     # prioritize papers that already mathching in title 
#     for paper in title_matching_papers:
        
#         genes_in_abstract = get_genes_in_abstract(paper, genes, verbose=False)
#         if verbose:
#                 print("Search matching abstract for remained genes: ", ",".join(genes_to_be_searched))
#                 print("Current search containing genes: ", ",".join(genes_in_abstract))
#         if len(set(genes_to_be_searched).intersection(set(genes_in_abstract)))==0: # if no gene in the abstract is in the search list, skip the paper
#             continue
#         abstract_match, abstract_support_evidence = check_abstract_match(db, paper,  dict_value, agent_id, verbose=verbose)
        
#         if abstract_match:

#             paper_for_references.append(paper)
#             # supporting_sentences = list(set(abstract_support_indexes).union(set(title_support_indexes))) #no longer print index support from title
#             reference_with_sentencesIDs.append({'citation': get_mla_citation_from_pubmed_id(paper),
#                 'support_indexes': abstract_support_evidence }) #CH: added list of support along with paper
#             for gene_in_abstract in genes_in_abstract:
#                 if gene_in_abstract in genes_to_be_searched:
#                     genes_to_be_searched.remove(gene_in_abstract)
#                     print(title)
#             if (len(paper_for_references)>=n):
#                 if not single_gene:
#                     if len([ gene_in_abstract for gene_in_abstract in genes_in_abstract if gene_in_abstract in genes_to_be_searched])==0:
#                         break
#                 else:
#                     break

#     genes_to_be_searched = genes.copy()
#     # keep searching paper that are not found in the title matching (added by CH)
#     if len(paper_for_references)<n:
#         for paper in sorted_papers:
#             if paper not in  title_matching_papers:
#                 abstract_match, abstract_support_evidence = check_abstract_match(db, paper,  dict_value, agent_id, verbose=verbose)
#                 if abstract_match:
#                     genes_in_abstract = get_genes_in_abstract(paper, genes, verbose=False)
#                     if verbose:
#                         print("Remained genes: ", ",".join(genes_to_be_searched))
#                     paper_for_references.append(paper)
                    
#                     reference_with_sentencesIDs.append({'citation': get_mla_citation_from_pubmed_id(paper),
#                         'support_indexes': abstract_support_evidence})
#                     for gene_in_abstract in genes_in_abstract:
#                         if gene_in_abstract in genes_to_be_searched:
#                             genes_to_be_searched.remove(gene_in_abstract)
#                             print(title)
#                     if (len(paper_for_references)>=n):
#                         if not single_gene:
#                             if len([ gene_in_abstract for gene_in_abstract in genes_in_abstract if gene_in_abstract in genes_to_be_searched])==0:
#                                 break
#                         else:
#                             break
#     # references = [get_mla_citation_from_pubmed_id(paper) for paper in paper_for_references]
#     return {"paragraph": paragraph, "keyword": keywords, "references": reference_with_sentencesIDs}
def get_references_for_paragraph(db, dict_value, agent_id, email, n=5, papers_query=20, verbose=False):
    paragraph = dict_value['analysis']
    if verbose:
        print("""Extracting keywords from paragraph\nParagraph:\n%s"""%paragraph)
        print("="*75)
    # get keywords
    keywords, genes, functions= get_keywords_combinations(db,  dict_value, agent_id, verbose=verbose)
    if keywords is None:
        print("No keyword generated skip referencing")
        return None
    if verbose:
        print("PubMed Keywords: ", keywords)
    print("Serching paper with keywords...")
    # search papers via pubmed
    papers = search_pubmed(keywords, email, retmax=papers_query)
    print("%d references are queried"%(len(papers)))
    
    if len(papers)==0:
        print("No paper searched!!")
    # sort the papers by the number of query genes in the abstract
    sorted_papers = sort_paper_by_n_genes_in_abstract(papers, genes, verbose=verbose)
    

    genes_to_be_searched = genes.copy() # copy the genes to be searched

    # prioritize the papers that have the most genes in the abstract and verify their relavence
    paper_for_references = []
    reference_with_sentencesIDs = [] # CH: added list of support along with paper

    # in the list of title_matching_papers, find the abstract also matches the paragraph
    # prioritize papers that already mathching in title 
    less_important_papers = []
    for paper in sorted_papers:
        # iterate the genes in the search list to find relavent paper 
        # reach to the end when there is no remaining gene to be searched
        genes_in_abstract = get_genes_in_abstract(paper, genes,verbose=False)
        title = paper['MedlineCitation']['Article']['ArticleTitle']
        
        if verbose:
                print("Search matching abstract for remained genes: ", ",".join(genes_to_be_searched))
                print("Current search containing genes: ", ",".join(genes_in_abstract))
        # intersect the genes in the abstract and the genes to be searched
        intersec_genes = set(genes_to_be_searched).intersection(set(genes_in_abstract))
        if len(intersec_genes)==0: # if no gene in the abstract is in the search list, skip the paper
            less_important_papers.append(paper) # put in the less important paper list
            continue
    
        abstract_match, abstract_support_evidence = check_abstract_match(db, paper,  dict_value, agent_id, verbose=verbose)
        
        if abstract_match:
            paper_for_references.append(paper)
            # supporting_sentences = list(set(abstract_support_indexes).union(set(title_support_indexes))) #no longer print index support from title
            reference_with_sentencesIDs.append({'citation': get_mla_citation_from_pubmed_id(paper),
                'support_indexes': abstract_support_evidence }) #CH: added list of support along with paper
            for gene_in_abstract in genes_in_abstract:
                if gene_in_abstract in genes_to_be_searched:
                    genes_to_be_searched.remove(gene_in_abstract)
                    print(title)
            if (len(paper_for_references)>=n):
                if not single_gene:
                    if len([ gene_in_abstract for gene_in_abstract in genes_in_abstract if gene_in_abstract in genes_to_be_searched])==0:
                        break
                else:
                    break


    # references = [get_mla_citation_from_pubmed_id(paper) for paper in paper_for_references]
    return {"paragraph": paragraph, "keyword": keywords, "references": reference_with_sentencesIDs}


def get_references_for_paragraphs(db, hypothesis_id, agent_id, n=5, papers_query=20, verbose=False):
    '''
    hypothesis_id: id of the hypothesis
    
    
    n: number of papers to be queried for each paragraph
    papers_query: number of papersf paper td
    verbose: if True, print out the process
    saveto: name of the json file to save the paragraph data
    '''
    email = load_constant_from_config(['email'])

    hypothesis_text = Hypothesis.load(db, hypothesis_id).hypothesis_text

    # Parse the hypothesis data
    response_dict = parse_text_to_json(hypothesis_text)


    references_paragraphs = []
    paragraph_ref_data = {}
    # paragraph_data = {}
    
    for key, dict_value in response_dict.items():
    
        reference_search_result = get_references_for_paragraph(db, dict_value, agent_id, email, n=5, papers_query=20, verbose=verbose)
        if reference_search_result is None:
            references = []
        else:
            references = reference_search_result['references']
        references_paragraphs.append(references)
        # save keywords and references in the dictionary
        paragraph_ref_data[key] = reference_search_result
        print("In process %s analysis, %d references are matched"%(key, len(references)))
        print("")
        print("")
        
        j = 1
        formated_citations = ''
        for reference in references:
           
            formated_citations += "[%d] %s"%(j, reference) + '\n'
            j+=1
        
        # update the citation to the response_dict
        response_dict[key]['citations'] = formated_citations
    
    return response_dict, paragraph_ref_data

        
 
