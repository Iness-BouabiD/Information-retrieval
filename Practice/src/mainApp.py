from collections import defaultdict
from preProcessing import Preprocessor
from fileCleaning import FileCleaning
from manage import Manage
from algorithms import Algorithms
import argparse
class MainApp:
    def __init__(self, folder_path,extract_method):
        self.extraction_method = extraction_method
        self.folder_path = folder_path
        self.preprocessor = Preprocessor(self.folder_path)
        self.result_data = self.preprocessor.preprocess_files(self.extraction_method) # case tags -> list
        self.cleaner = FileCleaning(self.result_data)
        self.nbr_stopList = None
        self.stop_d = ""
        self.stem_d = ""
        #self.manage = Manage()
        self.algorithms = Algorithms()
        #self.doc_lengths = self.preprocessor.get_doc_length(self.index, self.term_frequency)

        

    def calculate_vocabulary_size(self):
        return len(self.index)

    def load_queries(self):
        all_querys = defaultdict(str)
        with open('../resources/querys.txt', 'r') as allquerys:
            for query in allquerys:
                query_components = query.strip().split(maxsplit=1)
                query_id, query_text = query_components
                all_querys[query_id] = query_text
        return all_querys

    def calculate_smart_ltn_weights(self,result_data):
        return self.algorithms.SmartLtn(result_data)

    def calculate_smart_ltc_weights(self,smart_ltn_dict, result_data):
        return self.algorithms.SmartLtc(smart_ltn_dict,result_data)

    def calculate_BM25_weights(self,result_data,k,b):
        return self.algorithms.BM25_weighting(result_data,k,b)

    def query_processing(self, algorithm, weights, all_querys, run_index, params=None):
        stop_list = []
        with open('../resources/stop-words-english4.txt', 'r', encoding='utf-8') as stop_file:
            for line in stop_file:
                word = line.strip()
                stop_list.append(word)
        for query_id, query in all_querys.items():
            eval_result = self.algorithms.evaluate_query(query, weights, self.stem_d, stop_list)
            top_1500_docs = list(eval_result.items())[:1500]
            #Pas de tags
            self.manage.export_file(top_1500_docs, query_id, run_index, algorithm, "article", self.stop_d,
                                    self.stem_d, params if isinstance(params, dict) else 'noparameters')

    def update_counter(self, run_index):
        self.manage.update_counter(run_index)



    def run(self):
    #    parser = argparse.ArgumentParser(description="CoopCycle restaurants query program:")
    #    parser.add_argument("--stop", choice=["True","False"],action = "store_true", help="Removing stop words")
    #    parser.add_argument("--stem", choice=["True","False"], action="store_true", help="Stemming the words")
    #
    #    args = parser.parse_args()


        stop_des = int(input("Do you want to remove the stop words:\n1. Yes\n2. No\n"))
        if stop_des == 1:
            data_result = self.cleaner.stop_words_and_stemming(stop=True, stem=False)
        else:
            self.stop_d = "nostop"
        stem_des = int(input("Do you want to stem the tokens:\n1. Yes\n2. No\n"))
        if stem_des == 1:
            data_result = self.cleaner.stop_words_and_stemming(stop=False, stem=True)
        else:
            self.stem_d = "nostem"
            data_result = self.cleaner.stop_words_and_stemming(stop=False, stem= False)
        
      
        
        all_querys = self.load_queries()

        for run in range(1, 5):
            if run == 1:
                smart_ltn = self.calculate_smart_ltn_weights(data_result)
                
                smart_ltc = self.calculate_smart_ltc_weights(smart_ltn,data_result)
                #self.query_processing("ltc", smart_ltc, all_querys, run_index)
               
                print("*******************************************************************")      


                k = float(input("Enter the value of k: "))
                b = float(input("Enter the value of b: "))
                bm25= self.calculate_BM25_weights(data_result,k, b)
               
           

"""
                    self.query_processing("BM25", BM25, all_querys, run_index, {"k": k, "b": b})

                self.update_counter(run_index)

            run_again = input("Do you want to run again? (yes/no): ").lower()
            if run_again != "yes":
                break
"""


if __name__ == "__main__":
    folder_path = "../resources/test"

    def extract_method_choice():
        return input("Choose extraction method:\n1. Whole document\n2. Extract from specific tags\n").lower()


    extraction_method_choice = extract_method_choice()
    if extraction_method_choice =="1":
        extraction_method ="whole_document"
    elif extraction_method_choice == "2":
        extraction_method = "tags"
    else :
        print("Invalid choice. Choose 1 or 2")
    
    app = MainApp(folder_path,extraction_method)
            
    app.run()
