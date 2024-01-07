from collections import defaultdict
from math import log10, sqrt
from nltk.stem import PorterStemmer

class Algorithms:
    def __init__(self):
            ...
    def SmartLtn(self,df, tf, n):
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

    def smart_ltn_weighting(self,index, term_frequency, n):
        smart_ltn_dict = defaultdict(lambda: defaultdict(float))
        for term, postings_list in index.items():
            df = len(postings_list)
            for docno in postings_list:
                tf = term_frequency[term][docno]
                weight = self.SmartLtn(df, tf, n)
                smart_ltn_dict[term][docno] = weight
        return smart_ltn_dict

    def SmartLtc(self,tf, somme):
        weight = tf / sqrt(somme)
        return weight

    def somme_carre(self,smart_ltn_dict):
        sums = defaultdict(float)
        for term, dictio in smart_ltn_dict.items():
            for docno in dictio:
                sums[docno] += (smart_ltn_dict[term][docno] ** 2)

        sums = dict(sorted(sums.items()))
        return sums

    def smart_ltc_weighting(self,smart_ltn_dict):
        smart_ltc_dict = defaultdict(lambda: defaultdict(float))
        s = self.somme_carre(smart_ltn_dict)
        for term, dictio in smart_ltn_dict.items():
            for docno in dictio:
                tf = smart_ltn_dict[term][docno]
                if s[docno] > 0:
                    weight = self.SmartLtc(tf, s[docno])
                else:
                    weight = 0
                smart_ltc_dict[term][docno] = weight
        return smart_ltc_dict

    def BM25_df(self,df, n):
        bm25df = log10((n - df + 0.5) / (df + 0.5))
        return bm25df

    def BM25_tf(self,tf, k, b, dl, avdl):
        bm25tf = ((tf * (k + 1)) / ((k * ((1 - b) + (b * (dl / avdl)))) + tf))
        return bm25tf

    def BM25_weighting(self,index, term_frequency, n, k, b, avdl, doc_length):
        BM25_dict = defaultdict(lambda: defaultdict(float))
        for term, postings_list in index.items():
            df = len(postings_list)
            bm25df = self.BM25_df(df, n)
            for docno in postings_list:
                tf = term_frequency[term][docno]
                dl = doc_length[docno]
                bm25tf = self.BM25_tf(tf, k, b, dl, avdl)
                weight = bm25df * bm25tf
                BM25_dict[term][docno] = weight
        return BM25_dict

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
