from collections import defaultdict
from nltk.stem import PorterStemmer

class FileCleaning:
    def __init__(self, index, term_frequency):
        self.index = index
        self.term_frequency = term_frequency
    
    def remove_stopwords(self):
        stop_list = []
        with open('../resources/stop-words-english4.txt', 'r', encoding='utf-8') as stop_file:
            for line in stop_file:
                word = line.strip()
                stop_list.append(word)
        stop_list_length = len(stop_list)
        new_index = {term: postings for term, postings in self.index.items() if term not in stop_list}
        new_term_frequency = {term: freq for term, freq in self.term_frequency.items() if term not in stop_list}
        return new_index, new_term_frequency,stop_list_length
    

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
    