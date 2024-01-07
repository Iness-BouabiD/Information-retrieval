from collections import defaultdict
from preProcessing import Preprocessor
from fileCleaning import FileCleaning
from manage import Manage
from algorithms import Algorithms

class MainApp:
    def __init__(self, folder_path,extract_method):
        self.extraction_method = extraction_method
        self.folder_path = folder_path
        self.preprocessor = Preprocessor(self.folder_path)
        self.index, self.term_frequency = self.preprocessor.preprocess_files(self.extraction_method)
        self.cleaner = FileCleaning(self.index, self.term_frequency)
        self.stop_d = ""
        self.stem_d = ""
        self.manage = Manage()
        self.algorithms = Algorithms()
        self.doc_lengths = self.preprocessor.get_doc_length(self.index, self.term_frequency)

    def process_result_stop_words(self):
        cleaner = FileCleaning(self.index, self.term_frequency)
        index_without_stopwords, term_frequency_without_stopwords,nbr_stopList = cleaner.remove_stopwords()
        self.index, self.term_frequency = index_without_stopwords, term_frequency_without_stopwords
        self.stop_d = f"stop{nbr_stopList}"

    def process_result_stem(self):
        cleaner_stemming = FileCleaning(self.index, self.term_frequency)
        index_and_stemming, term_frequency_and_stemming = cleaner_stemming.perform_stemming()
        self.index, self.term_frequency = index_and_stemming, term_frequency_and_stemming
        self.stem_d = "porter"

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

    def calculate_smart_ltn_weights(self):
        return self.algorithms.smart_ltn_weighting(self.index, self.term_frequency, len(self.doc_lengths))

    def calculate_smart_ltc_weights(self, smart_ltn_weights):
        return self.algorithms.smart_ltc_weighting(smart_ltn_weights)

    def calculate_BM25_weights(self, k, b, avdl, dl):
        return self.algorithms.BM25_weighting(self.index, self.term_frequency, len(self.doc_lengths), k, b, avdl, dl)

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
        n = len(self.doc_lengths)
        while True:
            run_index = self.manage.get_run_counter()

            stop_des = int(input("Do you want to remove the stop words:\n1. Yes\n2. No\n"))
            if stop_des == 1:
                self.process_result_stop_words()
            else:
                self.stop_d = "nostop"

            stem_des = int(input("Do you want to stem the tokens:\n1. Yes\n2. No\n"))
            if stem_des == 1:
                self.process_result_stem()
            else:
                self.stem_d = "nostem"

            avdl = sum(self.doc_lengths.values()) / n
            dl = self.doc_lengths

            all_querys = self.load_queries()

            for run in range(1, 5):
                if run == 1:
                    print("smart ltn")
                    smart_ltn = self.calculate_smart_ltn_weights()
                    self.query_processing("ltn", smart_ltn, all_querys, run_index)

                elif run == 2:
                    smart_ltn = self.calculate_smart_ltn_weights()
                    smart_ltc = self.calculate_smart_ltc_weights(smart_ltn)
                    self.query_processing("ltc", smart_ltc, all_querys, run_index)

                elif run == 3:
                    print(f"{run}")
                    k = float(input("Enter the value of k: "))
                    b = float(input("Enter the value of b: "))
                    BM25 = self.calculate_BM25_weights(k, b, avdl, dl)
                    self.query_processing("BM25", BM25, all_querys, run_index, {"k": k, "b": b})

                self.update_counter(run_index)

            run_again = input("Do you want to run again? (yes/no): ").lower()
            if run_again != "yes":
                break



if __name__ == "__main__":
    folder_path = "../resources/XML-Coll-withSem/XML-Coll-withSem/"

    def extract_method_choice():
        return input("Choose extraction method:\n1. Whole document\n2. Extract from specific tags\n").lower()

    print(folder_path)
    extraction_method_choice = extract_method_choice()
    if extraction_method_choice =="1":
        extraction_method ="whole_document"
    elif extraction_method_choice == "2":
        extraction_method = "tags"
    else :
        print("Invalid choice. Choose 1 or 2")
    
    print(extraction_method)
    app = MainApp(folder_path,extraction_method)
            
    app.run()
