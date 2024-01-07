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

    def build_tree_structure(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        content_bytes = content.encode('utf-8')
        parser = etree.XMLParser(recover=True)
        root = etree.fromstring(content_bytes, parser=parser)

        tree_structure = defaultdict(list)

        self._traverse_tree(root, tree_structure)
        #print(tree_structure)

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
      

    def extract_doc_content(self, file_path, extract_method,tags = None):
        tree_structure = self.build_tree_structure(file_path)
        
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

            if extract_method == 'whole_document':
                docno = os.path.splitext(os.path.basename(file_path))[0]
                content = re.sub(r'<[^>]+>', '', content)  # we don't use XML tags in this case

            elif extract_method == 'tags':
                print("HNAAA")    
                docno = os.path.splitext(os.path.basename(file_path))[0]
                print(f"doc no is : {docno}")
                content = self.extract_from_tags(content, tags, tree_structure,docno)
                
                # lmode and tags then loop files, 
            else:
                raise ValueError("Invalid extract_method. Use 'whole_document' or 'tags'.")

        return docno, content


    def extract_from_tags(self, content, tags, tree_structure, docno):
        print(f"EXTRACT FROM TAGS ******************************************************")
        tags_with_hierarchy = []  # List to store dictionaries of tags and content
        content_test = []
        with open("../test.txt", "a") as file:
            for tag in tags:
                if tag in tree_structure:
                    print(f"YES {tag} in tree")
                    occurrences = tree_structure[tag]
                    print(f"occurence : {occurrences}")

                    for occurrence in occurrences:
                        tags_indices = self.extract_tags_indices(occurrence)
                        print(tags_indices)

                        current_dict = {"tag": occurrence, "content": {}}

                        content_list = current_dict.setdefault(f"content for {docno}", [])

                        for tag_name, index in tags_indices.items():
                            start_tag = f"<{tag_name}>" 
                            end_tag = f"</{tag_name}>"
                            #<article> (.*?) </article> 

                            tag_content_pattern = re.compile(f"{re.escape(start_tag)}(.*?){re.escape(end_tag)}", re.DOTALL)
                            
                            tag_content_matches = tag_content_pattern.finditer(content)

                            for tag_content_match in tag_content_matches:
                                content_test.append(tag_content_match.group(1))
                                clean_content = BeautifulSoup(tag_content_match.group(1), 'html.parser').get_text()
                                content_list.append({"index": index, "content": clean_content.strip()})

                        tags_with_hierarchy.append(current_dict)

            for current_dict in tags_with_hierarchy:
                file.write(str(content_test) + '\n')

        return "hello"




    def extract_tags_indices(self, tag_string):
        pattern = re.compile(r'(\w+)\[(\d+)\]')

        matches = pattern.findall(tag_string)

        tag_indices = {}
        for tag, index in matches:
            tag_indices[tag] = int(index)

        return tag_indices


    def preprocess_files(self,extraction_method):
        print(f"Preprocessing files for case {extraction_method}")
        index = defaultdict(set)
        term_frequency = defaultdict(lambda: defaultdict(int))
        if extraction_method == "tags" :
            tags = input("Enter tags separated with a comma to extract content: ").split(',')
        for filename in os.listdir(self.folder_path):
            if filename.endswith(".xml"):
                file_path = os.path.join(self.folder_path, filename)
                print(f"--------<>>>>>>{file_path}")
                docno, content = self.extract_doc_content(file_path,extraction_method,tags)

                terms = content.split()
                for term in terms:
                    index[term].add(docno)
                    term_frequency[term][docno] += 1

        return index, term_frequency

    def get_doc_length(self, index, term_frequency):
        doc_length = defaultdict(int)
        for term, postings_list in index.items():
            for docno in postings_list:
                doc_length[docno] += term_frequency[term][docno]

        return doc_length
