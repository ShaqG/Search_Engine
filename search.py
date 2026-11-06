# -*- coding: utf-8 -*-

import argparse
import re
from ast import literal_eval
import json
import heapq
from collections import defaultdict
from threading import Thread, Lock
from nltk.stem import PorterStemmer
import math
#import indexer

indexer_in = {}  # {stem:[(doc, start, end), (doc, start, end), (doc, start, end)], stem:[...]}


class Search:
    def __init__(self, indexf: str):
        # self.query = query
        self.index = indexf  # str type index file {stem : {urlid : （[position]， importantNum）}}
        self.url_dict = {}  # {id: url}
        self.url_dict2 = {}
        with open("url_dict.txt", 'r') as f:
            j = f.read()
            self.url_dict2 = literal_eval(j)
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

    def term_at_a_time(self, Query: str):
        terms_url_score = {}

        def ivl_to_dict(term):  # 将ivl_l中的ivl转换为{url:tf-idf score}
            single_url_score = defaultdict(float)

            inverteddict = {}
            for shard, start, end in indexer_in.get(term, ()):
                if start >= end:
                    continue
                with open(shard, 'r') as indexing:
                    indexing.seek(start)
                    stem_info = indexing.read(end - start + 2)

                postings = literal_eval('{' + stem_info + '}')[term]
                for doc_id, (positions, importance) in postings.items():
                    counts = inverteddict.setdefault(doc_id, [0, 0])
                    counts[0] += len(positions)
                    counts[1] += importance

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


def print_results(urls, interactive):
    if not urls:
        print("No results found.")
        return

    label = "result" if len(urls) == 1 else "results"
    print(f"{len(urls)} {label}")
    for rank, url in enumerate(urls, start=1):
        print(f"{rank}. {url}")
        if interactive and rank % 10 == 0 and rank < len(urls):
            if input("Press Enter for more, or type _q to return to search: ").strip() == "_q":
                break


def main():
    global indexer_in, lock
    parser = argparse.ArgumentParser(description="Search a local HTML index.")
    parser.add_argument("--query", help="Run one query and print all ranked results.")
    args = parser.parse_args()
    if args.query is not None and not args.query.strip():
        parser.error("--query must contain text")

    lock = Lock()
    try:
        with open("indexer_in.txt", "r") as index_file:
            indexer_in = literal_eval(index_file.read())
        search = Search("index_in")
    except FileNotFoundError as error:
        parser.exit(1, f"Missing {error.filename}. Run indexer.py and index_of_index.py first.\n")

    if args.query is not None:
        print_results(search.rank(search.term_at_a_time(args.query)), interactive=False)
        return

    try:
        while True:
            query = input("Search (type _q to exit): ").strip()
            if query == "_q":
                break
            if query:
                print_results(search.rank(search.term_at_a_time(query)), interactive=True)
    except (EOFError, KeyboardInterrupt):
        print()


if __name__ == "__main__":
    main()
