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


    def calculate_tf(self, term, metadata,docno):
        tf = metadata.get("indexation", [{}])[0]["term_frequency"].get(term, {}).get(docno)
        return tf
    
    def calculate_df(self, term, data_result):
        df = sum(1 for result in data_result if any(term in metadata.get("indexation", [{}])[0]["index"] for metadata in result["metadata"]))
        print(f"document frequency for term {term} is {df}")
        return df
        

    def SmartLtn(self, data_result):
        smart_ltn_dict = defaultdict(lambda: {"docno": "", "hierarchies": defaultdict(dict)})

        n = len(data_result)
        for result in data_result:
            docno = result.get("docno", "")
            hierarchies_dict = defaultdict(dict)

            doc_df_dict = {} 
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
        for docno, doc_dict in smart_ltn_dict.items():
            hierarchies_dict = doc_dict.get("hierarchies", {})
            for hierarchy, term_weights in hierarchies_dict.items():
                for term, weight in term_weights.items():
                    sums[docno] += (weight ** 2)

        sums = dict(sorted(sums.items()))
        return sums

    def SmartLtc(self, smart_ltn_dict, data_result):
        smart_ltc_dict = defaultdict(lambda: {"docno": "", "hierarchies": defaultdict(dict)})
        s = self.somme_carre(smart_ltn_dict)  # Calculate the sum of squares
        print(s)
        for result in data_result:
            docno = result.get("docno", "")
            hierarchies_dict = defaultdict(dict)

            for metadata in result.get("metadata", []):
                hierarchies = metadata.get("hierarchies", "")
                content = metadata.get("content", "")
                terms = content.split()
                for term in terms:
                    tf = self.calculate_tf(term, metadata, docno)
                    if docno in s:
                        if s[docno] > 0:
                            weight = self.calculate_SmartLtc_weight(tf, s[docno])
                        else:
                            weight = 0
                    else:
                        weight = 0
                    hierarchies_dict[hierarchies][term] = weight

            smart_ltc_dict[docno]["docno"] = docno
            smart_ltc_dict[docno]["hierarchies"] = dict(hierarchies_dict)

        print(smart_ltc_dict)
        return smart_ltc_dict





    """

    BM25 should be changed 
    ******************************************************************
    """
    def calculate_weight_bm25(self, df, tf, n, k, b, avdl, dl):
        bm25df = log10((n - df + 0.5) / (df + 0.5))
        bm25tf = ((tf * (k + 1)) / ((k * ((1 - b) + (b * (dl / avdl)))) + tf))
        return bm25df * bm25tf
    



    def BM25_weighting(self, data_result, k, b):
        BM25_result = defaultdict(lambda: {"docno": "", "hierarchies": defaultdict(dict)})
        n = len(data_result)
        #total_doc_length = sum(len(result["metadata"][0]["content"].split()) for result in data_result)
        #avdl = total_doc_length / n
        for result in data_result:
            
            docno = result["docno"]
            BM25_result[docno]["docno"] = docno
            BM25_result[docno]["hierarchies"] = defaultdict(dict)

            dl = len(result["metadata"][0]["content"].split())
            hierarchies_dict  = defaultdict(dict)
            for metadata in result.get("metadata", []):
                content = metadata.get("content", "")
                terms = content.split()

                for term in terms:
                    df = self.calculate_df(term, [result])
                    tf = self.calculate_tf(term, metadata, docno)
                    #weight = self.calculate_weight_bm25(df, tf, n, k, b, avdl, dl)
                    #BM25_result[docno]["hierarchies"][term] = weight
                
                    #hierarchies_dict[metadata["hierarchies"]][term] = weight

            #BM25_result[docno]["docno"] = docno
            #BM25_result[docno]["hierarchies"] = dict(hierarchies_dict)

        print(BM25_result)
        return BM25_result
    
    

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