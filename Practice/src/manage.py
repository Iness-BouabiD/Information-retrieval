import os

class Manage:
    def __init__(self):
        ...

    def index_txt(self, index, term_frequency):
        with open('index_collection.txt', 'w') as file:
            for term, postings_list in index.items():
                df = len(postings_list)
                file.write(f"{df}=df({term})\n")
                for word in postings_list:
                    file.write(f"{term_frequency[term][word]} {word}\n")

    def index_txt_smart_ltn(self, index, term_frequency, run_index):
        with open(f'index_collection_smart_ltn_{run_index}.txt', 'w') as file:
            for term, postings_list in index.items():
                df = len(postings_list)
                file.write(f"{df}=df({term})\n")
                for word in postings_list:
                    file.write(f"{term_frequency[term][word]} {word}\n")

    def index_txt_no_stop_words_stem(self, index, term_frequency):
        with open('index_collection_no_stop_words_stem.txt', 'w') as file:
            for term, postings_list in index.items():
                df = len(postings_list)
                file.write(f"{df}=df({term})\n")
                for word in postings_list:
                    file.write(f"{term_frequency[term][word]} {word}\n")

    def index_txt_smart_ltc(self, index, term_frequency, run_index):
        with open(f'index_collection_smart_ltc_{run_index}.txt', 'w') as file:
            for term, postings_list in index.items():
                df = len(postings_list)
                file.write(f"{df}=df({term})\n")
                for word in postings_list:
                    file.write(f"{term_frequency[term][word]} {word}\n")

    def index_txt_BM25(self, index, term_frequency, run_index):
        with open(f'index_collection_BM25_{run_index}.txt', 'w') as file:
            for term, postings_list in index.items():
                df = len(postings_list)
                file.write(f"{df}=df({term})\n")
                for word in postings_list:
                    file.write(f"{term_frequency[term][word]} {word}\n")

    def export_file(self, doc_list, query_id, run_id, weighting_function, granularity, stop, stem, parameters):
        if list is None:
            exit
        if parameters != 'noparameters':
            parm = ''
            for key, value in parameters.items():
                parm += f"_{key}{value}"
        else:
            parm = '_' + parameters
        file_granularity = granularity.split("/")[0]
        
        with open(f'../results/InessAliMohammedFatiha_{run_id}_{weighting_function}_{file_granularity}_{stop}_{stem}{parm}.txt', 'a') as file:
            for i in range(0, len(doc_list)):
                # Include dynamic granularity information in the output line
                file.write(f"{query_id} Q0 {doc_list[i][0]} {i+1} {doc_list[i][1]} InessAliMohammedFatiha /{granularity}\n")


    def get_run_counter(self):
        counter_file_path = '../resources/run_counter.txt'
        if not os.path.exists(counter_file_path):
            with open(counter_file_path, 'w') as counter_file:
                counter_file.write('1')
            return 1
        with open(counter_file_path, 'r') as counter_file:
            counter = int(counter_file.read())
            counter += 1

        return counter

    def update_counter(self, new_counter: int):
        counter_file_path = '../resources/run_counter.txt'
        with open(counter_file_path, 'w') as counter_file:
            counter_file.write(str(new_counter))
