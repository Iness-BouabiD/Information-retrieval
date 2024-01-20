from collections import defaultdict
from nltk.stem import PorterStemmer

class FileCleaning:
    def __init__(self, result_data):
        self.result_data = result_data

    
    def get_stop_list(self):
        stop_list = []
        with open('../resources/stop-words-english4.txt', 'r', encoding='utf-8') as stop_file:
            for line in stop_file:
                word = line.strip()
                stop_list.append(word)
        return stop_list

    def get_stop_list_lenght(self):
        return len(self.get_stop_list())

            
    def stop_words_and_stemming(self, stop = False, stem = False):
        if stop == True :
            print("Removing stop words ...")
        elif stem == True:
            print("Stemming the words ...")
        else:
            print("Preprocessing")

        stop_list = self.get_stop_list()

        new_result_data = []
        for result in self.result_data:
            new_result = {"docno": result["docno"], "metadata": []}
            local_index = defaultdict(set)
            local_term_frequency = defaultdict(lambda: defaultdict(int))

            for metadata in result.get("metadata", []):
                content = metadata.get("content", "")
                terms = content.split()
                stemmer = PorterStemmer()

                if stop == True and stem ==False :
                    filtered_terms = [term for term in terms if term.lower() not in stop_list]
                elif stem == True and stop ==False:
                    filtered_terms = [stemmer.stem(term) for term in terms]
                elif stop == True and stem == True:
                    filtered_stop = [term for term in terms if term.lower() not in stop_list]
                    filtered_terms = [stemmer.stem(term) for term in filtered_stop]
                elif stop==False  and stem ==False:
                    return self.result_data
             
                metadata["content"] = ' '.join(filtered_terms)

                indexation = {"index": {}, "term_frequency": defaultdict(int)}
                for term in filtered_terms:
                    local_index[term].add(result["docno"])
                    local_term_frequency[term][result["docno"]] += 1

                indexation["index"] = dict(local_index)
                indexation["term_frequency"] = dict(local_term_frequency)
                metadata["indexation"] = [indexation] 
                new_result["metadata"].append(metadata)

            new_result_data.append(new_result)

      
        return new_result_data
                
