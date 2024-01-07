from collections import defaultdict
from nltk.stem import PorterStemmer

class FileCleaning:
    def __init__(self, result_data):
        self.result_data = result_data

            
    def remove_stop_words(self):
        print(self.result_data)
        print("--------REMOVE STOP WORDS------------------")

        stop_list = []
        with open('../resources/stop-words-english4.txt', 'r', encoding='utf-8') as stop_file:
            for line in stop_file:
                word = line.strip()
                stop_list.append(word)

        new_result_data = []
        for result in self.result_data:
            new_result = {"docno": result["docno"], "metadata": []}
            local_index = defaultdict(set)
            local_term_frequency = defaultdict(lambda: defaultdict(int))

            for metadata in result.get("metadata", []):
                content = metadata.get("content", "")
                terms = content.split()

                # Remove stop words from the content
                filtered_terms = [term for term in terms if term.lower() not in stop_list]
                metadata["content"] = ' '.join(filtered_terms)

                # Update the indexation dictionary
                indexation = {"index": {}, "term_frequency": defaultdict(int)}
                for term in filtered_terms:
                    local_index[term].add(result["docno"])
                    local_term_frequency[term][result["docno"]] += 1

                # Update the overall indexation
                indexation["index"] = dict(local_index)
                indexation["term_frequency"] = dict(local_term_frequency)
                metadata["indexation"] = [indexation]  # Only one entry for indexation
                new_result["metadata"].append(metadata)

            new_result_data.append(new_result)

        print(new_result_data)
        print("--------REMOVE STOP WORDS------------------")
        return new_result_data
                


"""
    def perform_stemming(self):
        stemmer = PorterStemmer()
        new_index = defaultdict(set)
        new_term_frequency = defaultdict(lambda: defaultdict(int))
        for term, document_list in self.index.items():
            stemmed_term = stemmer.stem(term)
            for docno in document_list:
                new_index[stemmed_term].add(docno)
                new_term_frequency[stemmed_term][docno] += self.term_frequency[term][docno]
        return new_index, new_term_frequency
"""