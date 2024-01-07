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
        


    # Extract from the whole document without taking in consideration the tags
    def extract_doc_content(self, file_path):
        tree_structure = self.build_tree_structure(file_path)
        
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            docno = os.path.splitext(os.path.basename(file_path))[0]
            content = re.sub(r'<[^>]+>', '', content)  # we don't use XML tags in this case
        return docno, content

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
            print(formatted_paths)
        return formatted_paths
    

      
    def extract_tags_indices(self, tag_string):
        pattern = re.compile(r'(\w+)\[(\d+)\]')
        matches = pattern.findall(tag_string)
        tag_indices = {}
        for tag, index in matches:
            tag_indices[tag] = int(index)

        return tag_indices

    

    def extract_from_tags(self, file_path, tags):
        tree_structure = self.build_tree_structure(file_path)
        with open(file_path, 'r', encoding='utf-8') as file:
            data = file.read()
        data = data.replace('&', '&amp;')
        docno = os.path.splitext(os.path.basename(file_path))[0]
        result_dicts = {"docno":"", "metadata":[]}
        result_dicts["docno"] = docno
        for tag in tags:
            if tag in tree_structure:
                #print(tree_structure[tag])
                occurrences = tree_structure[tag]
                for occurrence in occurrences:
                    tags_indices = self.extract_tags_indices(occurrence)
                    current_dict = {"hierarchies": [], "start_tag": "", "end_tag": "", "content": ""}
                    
                    for tag_name, index in tags_indices.items():
                        current_dict["start_tag"] += f"/{tag_name}"
                        current_dict["end_tag"] += f"/{tag_name}"

                    current_dict["hierarchies"].append(occurrence)

                    start_tag = re.escape(current_dict["start_tag"])
                    root = etree.fromstring(unescape(data).encode('utf-8'), parser=etree.XMLParser(resolve_entities=False))
                    elements = root.xpath(f'//{start_tag}//*')
                  
                    for element in elements:
                        content = etree.tostring(element, encoding='unicode', method='text')
                        current_dict["content"] = content.strip()

                    result_dicts["metadata"].append(current_dict)        
        return docno, result_dicts


    def process_result_tags(self, result_dicts):
        index = defaultdict(set)
        term_frequency = defaultdict(lambda: defaultdict(int))
        docno = result_dicts["docno"]
        for metadata in result_dicts["metadata"]:
            content = metadata["content"]
            terms = content.split()
            for term in terms:
                index[term].add(docno)
                term_frequency[term][docno] += 1
        return index, term_frequency

    def preprocess_files(self,extraction_method):
        print(f"Preprocessing files for case {extraction_method}")
        index = defaultdict(set)
        term_frequency = defaultdict(lambda: defaultdict(int))
        if extraction_method == "tags" :
            tags = input("Enter tags separated with a comma to extract content: ").split(',')
            file_counter = 0  #Counter
            limit = 5
            for filename in os.listdir(self.folder_path):
                if filename.endswith(".xml"):
                    file_path = os.path.join(self.folder_path, filename)
                    docno, result_contents = self.extract_from_tags(file_path,tags)
                    print(result_contents.get("metadata"))
                    file_counter += 1  
                    if file_counter >= limit:  
                        break
        else:
            
            file_counter = 0  #Counter
            limit = 2
            for filename in os.listdir(self.folder_path):
                if filename.endswith(".xml"):
                    file_path = os.path.join(self.folder_path, filename)
                    docno, content = self.extract_doc_content(file_path)
                    terms = content.split()
                    for term in terms:
                        index[term].add(docno)
                        term_frequency[term][docno] += 1
                    file_counter += 1  

                    if file_counter >= limit:  
                        break
        return index, term_frequency
    
