from collections import defaultdict
from math import log10, sqrt
from nltk.stem import PorterStemmer

class Algorithms:
    def __init__(self):
            ...

    def calculate_weight(self, df, tf, n):
        if tf > 0:
            wtf = (1 + log10(tf))
        else:
            wtf = 0
        if df > 0:
            wdf = log10(n / df)
        else:
            wdf = 0
        weight = wtf * wdf
        return weight

    def calculate_weight_bm25(self, df, tf, n, k, b, avdl, dl):
        bm25df = log10((n - df + 0.5) / (df + 0.5))
        bm25tf = ((tf * (k + 1)) / ((k * ((1 - b) + (b * (dl / avdl)))) + tf))
        return bm25df * bm25tf

    def calculate_tf(self, term, metadata,docno):
        tf = metadata.get("indexation", [{}])[0]["term_frequency"].get(term, {}).get(docno)
        print(f"term frequency of {term} is {tf} in docno {docno}")
        return tf
    
    def calculate_df(self, term, data_result):
        df = sum(1 for result in data_result if any(term in metadata["indexation"][0]["index"] for metadata in result["metadata"]))
        print(f"document frequency of the term {term} is {df}")
        return df
        

    def SmartLtn(self, data_result):
        smart_ltn_dict = defaultdict(lambda: {"docno": "", "hierarchies": defaultdict(dict)})

        n = len(data_result)
        for result in data_result:
            docno = result.get("docno", "")
            hierarchies_dict = defaultdict(dict)

            # Calculate document frequency for terms across the entire collection
            doc_df_dict = {}  # Dictionary to store document frequency for the entire collection
            for metadata in result.get("metadata", []):
                content = metadata.get("content", "")
                terms = content.split()

                for term in terms:
                    doc_df_dict.setdefault(term, 0)
                    doc_df_dict[term] += 1

            for metadata in result.get("metadata", []):
                hierarchies = metadata.get("hierarchies", "")
                content = metadata.get("content", "")
                terms = content.split()

                for term in terms:
                    df = self.calculate_df(term, data_result)
                    tf = self.calculate_tf(term, metadata, docno)
                    weight = self.calculate_weight(df, tf, n)

                    hierarchies_dict[hierarchies][term] = weight

            smart_ltn_dict[docno]["docno"] = docno
            smart_ltn_dict[docno]["hierarchies"] = dict(hierarchies_dict)

        smart_ltn_dict = dict(smart_ltn_dict)
        return smart_ltn_dict



    def calculate_SmartLtc_weight(self, tf, somme):
        weight = tf / sqrt(somme)
        return weight

    def somme_carre(self, smart_ltn_dict):
        sums = defaultdict(float)
        for term, dictio in smart_ltn_dict.items():
            for docno in dictio:
                sums[docno] += (smart_ltn_dict[term][docno] ** 2)

        sums = dict(sorted(sums.items()))
        return sums

    def SmartLtc(self, data_result):
        smart_ltn_dict = self.SmartLtn(data_result)
        smart_ltc_dict = defaultdict(lambda: defaultdict(float))
        s = self.somme_carre(smart_ltn_dict)

        for term, dictio in smart_ltn_dict.items():
            for docno in dictio:
                tf = smart_ltn_dict[term][docno]
                if s[docno] > 0:
                    weight = self.calculate_SmartLtc_weight(tf, s[docno])
                else:
                    weight = 0
                smart_ltc_dict[term][docno] = weight

        return smart_ltc_dict

    def BM25_df(self, term, data_result):
        df = sum(1 for result in data_result if term in result["metadata"][0]["indexation"][0]["index"])
        return df

    def BM25_tf(self, term, data_result):
        tf = data_result["metadata"][0]["indexation"][0]["term_frequency"].get(term, {}).get(data_result["docno"], 0)
        return tf

    def BM25_weighting(self, data_result, k, b):
        BM25_result = defaultdict(lambda: defaultdict(float))
        n = len(data_result)
        total_doc_length = 0
        for result in data_result:
            total_doc_length += len(result["metadata"][0]["content"].split())
        avdl = total_doc_length / n

        for result in data_result:
            docno = result["docno"]
            dl = len(result["metadata"][0]["content"].split())

            for metadata in result.get("metadata", []):
                content = metadata.get("content", "")
                terms = content.split()

                for term in terms:
                    df = self.BM25_df(term, data_result)
                    tf = self.BM25_tf(term, data_result)
                    weight = self.calculate_weight_bm25(df, tf, n, k, b, avdl, dl)
                    BM25_result[term][docno] = weight

        return BM25_result, avdl

        
    
    

    def evaluate_query(self, query, smart, stem_d, stop_list):
        eval_query = defaultdict(lambda: defaultdict(float))
        doc_scorring = defaultdict(float)
        query_words = query.split()
        stm_l = []

        for word in query_words:
            if word in stop_list:
                query_words.remove(word)

        if stem_d != "nostem":
            stemm = PorterStemmer()
            for word in query_words:
                stemmed_word = stemm.stem(word)
                stm_l.append(stemmed_word)
            query_words = stm_l.copy()

        for word in query_words:
            eval_query[word] = smart[word]
        for word, dictio in eval_query.items():
            for docno in dictio:
                doc_scorring[docno] += eval_query[word][docno]
        doc_scorring = dict(sorted(doc_scorring.items(), key=lambda item: item[1], reverse=True))
        return doc_scorring