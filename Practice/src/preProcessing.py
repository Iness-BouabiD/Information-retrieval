from collections import defaultdict
import os
import re
import xml.etree.ElementTree as ET
from html import unescape
import io
from lxml import etree
from bs4 import BeautifulSoup

class Preprocessor:
    def __init__(self, folder_path):
        self.folder_path = folder_path
    
   
    def get_doc_length(self, index, term_frequency):
        doc_length = defaultdict(int)
        for term, postings_list in index.items():
            for docno in postings_list:
                doc_length[docno] += term_frequency[term][docno]
        return doc_length

    #Extracting the tree for getting tags
    def build_tree_structure(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        content_bytes = content.encode('utf-8')
        parser = etree.XMLParser(recover=True)
        root = etree.fromstring(content_bytes, parser=parser)
        tree_structure = defaultdict(list)

        self._traverse_tree(root, tree_structure)
        return tree_structure
    

   # <article> <bdy> <p> <...> </p> <p> </p> </byd> 
    # /article/bdy[1]/p[1]
    # /article/bdy[1]/p[2]
    def _traverse_tree(self, element, tree_structure, parent_path=""):
        current_path = f"{parent_path}/{element.tag}[{len(tree_structure[element.tag]) + 1}]"
        tree_structure[element.tag].append(current_path)
        for child in element:
            self._traverse_tree(child, tree_structure, current_path)

    def organize_tags(self, hierarchy):
        result = []
        self._generate_combinations(hierarchy, 0, "", result)
        return result

    def _generate_combinations(self, hierarchy, level, current_path, result):
        if level == len(hierarchy):
            result.append(current_path)
            return
        for i, tag_content in enumerate(hierarchy[level], start=1):
            next_path = f"{current_path}/{tag_content}"
            self._generate_combinations(hierarchy, level + 1, next_path, result)

    # Not sure if to keep it 
    def format_paths(self, organized_tags):
        formatted_paths = []
        for tag_path in organized_tags:
            formatted_path = ""
            tags = tag_path.split('/')
            for tag in tags:
                if "[" in tag:
                    tag_name, index = tag.split("[")
                    index = index.rstrip("]")
                    formatted_path += f"{tag_name}[{index}]/"
                else:
                    formatted_path += f"{tag}/"
            formatted_paths.append(formatted_path.rstrip("/"))
           
        return formatted_paths
    

      
    def extract_tags_indices(self, tag_string):
        pattern = re.compile(r'(\w+)\[(\d+)\]')
        matches = pattern.findall(tag_string)
        tag_indices = {}
        for tag, index in matches:
            tag_indices[tag] = int(index)
        return tag_indices

    #/article/bdy[1]/p[1]/sec[1] 
    # NEVER NEST != TRUE HEHEHEHEHE why ?
    def extract_from_tags(self, file_path, tags):
        local_index = defaultdict(set)
        local_term_frequency = defaultdict(lambda: defaultdict(int))

        tree_structure = self.build_tree_structure(file_path)
    
        with open(file_path, 'r', encoding='utf-8') as file:
            data = file.read()
        data = data.replace('&', '&amp;')

        docno = os.path.splitext(os.path.basename(file_path))[0]
        result_dicts = {"docno": "", "metadata": []}
        result_dicts["docno"] = docno
         
        # ranking -> p ==> /article/p1 ... 
        for tag in tags:
                
            if tag in tree_structure:
                
                occurrences = tree_structure[tag]
                for occurrence in occurrences:
                    
                    current_dict = {"hierarchies": "", "content": "", "indexation": []}
                    # <p> bla bla iness taha </p> 
                    # indexation['bla'] = [ { "index" : "bla" , "term_frequency": 2 } ]
         
                    current_dict["hierarchies"]=occurrence

                    # un seul doc : ['/p[1]', '/p[2]']
                    root = etree.fromstring(unescape(data).encode('utf-8'), parser=etree.XMLParser(resolve_entities=False))
                    elements = root.xpath(occurrence)


                    for element in elements:
                        content = etree.tostring(element, encoding='unicode', method='text')
                        current_dict["content"] = content.strip()
                        indexation = {"index": {}, "term_frequency": {}}
                        terms = content.split()
                        for term in terms:
                            if indexation['index'] == {} or indexation["index"].get(term) is None:
                                indexation["index"][term] = local_index[term]
                                indexation["term_frequency"][term] = local_term_frequency[term]
                            local_index[term].add(docno)
                            local_term_frequency[term][docno] += 1
                        current_dict["indexation"].append(indexation)

                    #docno has many tags
                    result_dicts["metadata"].append(current_dict)
        return  result_dicts
    

    def preprocess_files(self, extraction_method):
        print(f"Preprocessing files for case {extraction_method}")
        index = defaultdict(set)
        term_frequency = defaultdict(lambda: defaultdict(int))
        limit = 60
        tags = ["article"]
        results = []
        if extraction_method == "tags":
            tags = input("Enter tags separated with a comma to extract content: ").split(',')   
            # ['bdy', 'p']
        
        file_counter = 0 
       
        for filename in os.listdir(self.folder_path):
            if filename.endswith(".xml"):
               
                file_path = os.path.join(self.folder_path, filename)

                if extraction_method == "tags":
                    result_contents = self.extract_from_tags(file_path, tags)
                else:
                    result_contents = self.extract_from_tags(file_path, tags)

                file_counter += 1
                if file_counter >= limit:
                    break
                results.append(result_contents)

        return  results
