# -*- coding: utf-8 -*-

import re
import json
import heapq
from collections import defaultdict
from threading import Thread, Lock
from tkinter import *
from nltk.stem import PorterStemmer
import math
#import indexer
from time import time

indexer_in = {}  # {stem:[(doc, start, end), (doc, start, end), (doc, start, end)], stem:[...]}


def timer_func(func):
    def wrap_func(*args, **kwargs):
        t1 = time()
        result = func(*args, **kwargs)
        t2 = time()
        print('*' * 30)
        print(f'Function {func.__name__!r} executed in {(t2 - t1):.4f}s')
        return result

    return wrap_func


class Search:
    def __init__(self, indexf: str):
        # self.query = query
        self.index = indexf  # str type index file {stem : {urlid : （[position]， importantNum）}}
        self.url_dict = {}  # {id: url}
        self.url_dict2 = {}
        with open("url_dict.txt", 'r') as f:
            j = f.read()
            self.url_dict2 = eval(j)
            for key in self.url_dict2:
                self.url_dict[self.url_dict2[key]] = key

        self.stemmer = PorterStemmer()
        self.stopwords = {'during', 'out', 'very', 'having', 'with', 'they', 'own', 'an', 'be', 'some', 'for', 'do',
                          'ourselves', 'hers', 'between', 'yourself', 'but', 'again', 'there', 'about', 'once',
                          'its', 'yours', 'such', 'into', 'of', 'most', 'itself', 'other', 'off', 'is', 's', 'am', 'or',
                          'these', 'your', 'his', 'through', 'don', 'nor', 'me', 'were', 'her', 'more', 'himself',
                          'who', 'as', 'from', 'him', 'each', 'the', 'themselves', 'until', 'because', 'are', 'we',
                          'she', 'all', 'no', 'when', 'at', 'any', 'before', 'them', 'same', 'and', 'been', 'have',
                          'this', 'down', 'should', 'our', 'their', 'while', 'above', 'both', 'up', 'to', 'ours', 'had',
                          'in', 'will', 'on', 'does', 'yourselves', 'then', 'that', 'blow', 'what', 'over', 'why',
                          'too', 'only', 'myself', 'which', 'those', 'i', 'after', 'few', 'whom', 't', 'being', 'if',
                          'so', 'can', 'did', 'not', 'now', 'under', 'he', 'you', 'herself', 'has', 'just', 'where',
                          'theirs', 'my', 'against', 'a', 'by', 'doing', 'it', 'how', 'further', 'was', 'here', 'than'}

    """
    def search_indexer(self):

        word_index = [self.index.get(word) for word in self.token]  # return value of token in index [{url:freq},]

        if len(word_index) == 1:
            return word_index[0]
        elif len(word_index) >= 2:
            minlen = sorted(word_index, key=lambda x: len(x))
            d1 = minlen[0]
            common_urls = set(d1.keys())
            urls = defaultdict(int)

            for d in minlen[1:]:
                common_urls.intersection_update(set(d.keys()))

            for i in minlen:
                for j in common_urls:
                    if j in i:
                        urls[j] += i[j]  # url freq

            return urls

        else:
            return None

    """

    @timer_func
    def term_at_a_time(self, Query: str):
        terms_url_score = {}

        def ivl_to_dict(term):  # 将ivl_l中的ivl转换为{url:tf-idf score}
            single_url_score = defaultdict(float)

            # I'll need the inverteddict
            # print(inverteddict)
            try:
                ivl_l_e = {}
                pos = indexer_in[term]  # position
                for i in pos:
                    # print(i)
                    stem_info = '{'  # {stem -> {url-id -> ([position], important_number)}}
                    with open(i[0], 'r') as indexing:
                        start = i[1]
                        end = i[2]
                        char_num = end - start
                        if start < end:
                            indexing.seek(start)
                            info = indexing.read(char_num + 2)
                            stem_info += info
                    stem_info += '}'
                stem_info_dict = eval(stem_info)
                urls = stem_info_dict[term]
                # urls = { 25265: ([952], 0), 25269: ([362], 0), 25276: ([24046, 24058, 26748, 26761, 53529, 56004, 99154, 107522, 108136, 133944, 168379, 169822, 169830, 189711, 197440, 216624, 216633, 216642, 216649, 216658, 225510, 232637, 232650, 232662, 232692, 249896], 0)}
                for u in urls:
                    if u in ivl_l_e:
                        ivl_l_e[u][0] += len(urls[u][0])  # freq
                        ivl_l_e[u][1] += urls[u][1]  # important
                    else:
                        ivl_l_e[u] = [len(urls[u][0]), urls[u][1]]
                inverteddict = ivl_l_e
            except KeyError:
                return

            for id, frequency in inverteddict.items():
                url = self.url_dict[id]

                single_url_score[url] = single_url_score[url] + (1 + math.log10(frequency[0]) *
                                                                 math.log10(len(self.url_dict) /
                                                                            len(inverteddict.items()))) + frequency[1] / \
                                        frequency[0]
            lock.acquire()

            for key in single_url_score:
                if not (key in terms_url_score):
                    terms_url_score[key] = 0
                terms_url_score[key] += single_url_score[key]
            lock.release()
            # print('term:              ', terms_url_score)

        que = []
        query_to_words = re.split(r"[^a-zA-Z]+", Query.strip())
        term_lst = []
        for word in query_to_words:
            term_lst.append(self.stemmer.stem(word))

        Threads = []
        ivl_l = []
        for term in term_lst:
            Threads.append(Thread(target=ivl_to_dict, args=(term,)))

        for i in Threads: i.start()
        for i in Threads: i.join()
        return terms_url_score

    def rank(self, url_score):

        # print("I'll print url_score")
        # print(url_score)

        topurls = [k for k, v in sorted(url_score.items(), key=lambda item: item[1], reverse=True)]
        return topurls

    def start(self, Query: str):
        Tre = self.term_at_a_time(Query)
        res = []
        try:
            while True:
                res.append(heapq.heappop(Tre))
        except IndexError:
            pass
        return res


if __name__ == "__main__":

    lock = Lock()
    with open("indexer_in.txt", 'r') as f:
        j = f.read()
        indexer_in = eval(j)

    while True:
        query = input("Enter query (type _q to exit):")
        if query == '_q':
            break
        s = Search("index_in")  # index_in = index
        urls = s.term_at_a_time(query)
        url_list = s.rank(urls)
        if len(url_list) <= 10:
            for i in url_list:
                print(i)
        else:
            t = 0
            for i in range(t, len(url_list)):
                print(url_list[i])
                if i % 10 == 9:
                    if input("Press Enter for more results, or type _q to exit:") == '_q':
                        break
