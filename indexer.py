import os
import json
import re
from random import randrange
from bs4 import BeautifulSoup
from collections import defaultdict
from nltk.stem import PorterStemmer
from floc_simhash import SimHash
from math import log2
from numpy import int64

cnt = 0
url_dict = {}
# stem_hash = {}
page_hash = {}
change1 = True
change2 = True
unique = {}


def get_url_id(x):
    global url_dict
    return url_dict[x]


def set_url_id(x, mycnt):
    global url_dict
    url_dict[x] = mycnt
    return mycnt


def stemmer(ps, x):
    if (len(x) < 2):
        return x
    x = ps.stem(x)
    if (x[0] == '\'') and (x[len(x) - 1] == '\''):
        return x[1:len(x) - 1]
    '''
    if not (x in stem_hash):
        y = randrange(1 << 30)
        while (y in stem_hash):
            y = randrange(1 << 30)
        stem_hash[x] = y
    '''
    return x


'''
# I say similarity >= 90 means too similar
def similar(p, n, cnt):
    if (n == 30):
        if (p in page_hash):
            print("!!!", p)
            return True
        else:
            return False
    ans = similar(p, n + 1, cnt)
    if (cnt < 3):
        ans |= similar(p ^ (1 << n), n + 1, cnt + 1)
    return ans
'''


# so 61/64 similarity?
def similar(p):
    for i in page_hash:
        t = i ^ p
        for j in range(3):
            if (t == 0):
                break
            t -= 1 << (int(log2(t)))
        if (t == 0):
            return True
    return False


def get_link_and_content():
    path = os.getcwd() + '\DEV'
    list_of_files = []
    num = 0
    cnt = 0
    for root, dirs, files in os.walk(path):
        for file in files:
            cnt += 1
            list_of_files.append(os.path.join(root, file))

    cnt = 0
    ans = []
    for file in list_of_files:
        cnt += 1
        # print(cnt)
        with open(file, 'r') as f:
            s = f.readline()
            json_dict = json.loads("\\n".join(s.split('\n')))
            ans.append((json_dict['url'], json_dict['content']))

    return ans


def get_word_content(lst):
    ps = PorterStemmer()
    # ps = 0
    dic = {}
    file = open("dict1.txt", "w")
    mycnt = 0
    for url in lst:
        mycnt += 1

        soup = BeautifulSoup(url[1], "html.parser")
        lis = re.split(r"[^a-zA-Z]+", soup.get_text().strip())
        # if it contains more than 10000 words, the user will not like it.
        url_id = set_url_id(url[0], mycnt)
        if (len(lis) > 10000):
            continue
        stemString = ""
        for i in range(len(lis)):
            word = lis[i]
            stem = stemmer(ps, word)
            stemString += stem + " "
            '''
            for j in range(30):
                p = stem_hash[stem] & (1 << j)
                if (p != 0):
                    bit[j] += 1
                else:
                    bit[j] -= 1
            '''
        '''
        p = 0
        for i in range(30):
            if (bit[i] > 0):
                p += 1 << i
        '''
        ss = SimHash(n_bits=64).hash(stemString)
        p = 0
        for i in range(len(ss) - 1):
            p += p * 16 + int(ss[i], 16)

        # if it is similar to others, just skip it
        if (similar(p)):
            continue

        print(mycnt)
        page_hash[p] = True
        unique[mycnt] = True
        # print(mycnt)
        # print(lis)
        for i in range(len(lis)):
            word = lis[i]
            stem = stemmer(ps, word)
            if not (stem in dic):
                dic[stem] = {}
            if not (url_id in dic[stem]):
                dic[stem][url_id] = ([], 0)
            dic[stem][url_id][0].append(i)

        important = ["b", "strong", "h1", "h2", "h3", "title"]
        for i in range(6):
            lis0 = soup.find_all(important[i])
            for j in range(len(lis0)):
                s = str(lis0[j])
                s2 = s[(len(important[i]) + 2): (len(s) - (len(important[i]) + 3))]
                lis = re.split(r"[^a-zA-Z]+", s2.strip())
                url_id = get_url_id(url[0])
                for k in range(len(lis)):
                    word = lis[k]
                    stem = stemmer(ps, word)
                    if not ((stem in dic)):
                        break
                    if not ((url_id in dic[stem])):
                        break
                    dic[stem][url_id] = ((dic[stem][url_id][0], dic[stem][url_id][1] + 1))

        global change1
        global change2
        if (mycnt >= len(lst) // 3 and change1):
            change1 = False
            file.write(str(dic))
            dic = {}
            file.close()
            file = open("dict2.txt", "w")
        if (mycnt >= len(lst) // 3 * 2 and change2):
            change2 = False
            file.write(str(dic))
            dic = {}
            file.close()
            file = open("dict3.txt", "w")
    file.write(str(dic))
    file.close()

    global url_dict
    file = open("url_dict.txt", "w")
    file.write(str(url_dict))
    file.close()

    # file = open("valid_dict.txt", "w")
    # file.write(str(unique))
    # file.close()


def get_pr(lst):
    # file = open("valid_dict.txt", "r")
    # unique = exec(file.readline())
    # file.close()
    global unique
    mycnt = 0
    links = {}
    links2 = {}
    for url in lst:
        mycnt += 1
        if not (mycnt in unique):
            continue
        soup = BeautifulSoup(url[1], "html.parser")
        links[mycnt] = 0
        for i in soup.find_all("a"):
            ss = str(i)
            if ss.find("href=\"") == -1:
                continue
            s = ss[ss.find("href=\"") + 6: ss.find("\">")]
            if not (s in url_dict):
                continue
            links[mycnt] += 1
            if get_url_id(s) not in links2:
                links2[get_url_id(s)] = []
            links2[get_url_id(s)].append(mycnt)

    pr = [1 / mycnt for i in range(mycnt + 1)]
    pr2 = [0 for i in range(mycnt + 1)]
    d = 0.85
    prcnt = 0
    while (1):
        for i in range(1, mycnt + 1):
            if not (i in unique):
                continue
            pr2[i] = 1 - d
            if not i in links2:
                continue
            prcnt += len(links2[i])
            for j in links2[i]:
                pr2[i] += pr[j] / links[j] * d

        bo = True
        for i in range(mycnt):
            if not (i in unique):
                continue
            if (pr2[i] - pr[i] > 1 / mycnt / 100):
                bo = False
                break
        if bo:
            break
        for i in range(mycnt + 1):
            pr[i] = pr2[i]
        if (prcnt > 1e9):
            break
    file = open("pr.txt", "w")
    file.write(str(pr2))
    file.close()


if __name__ == "__main__":
    lst = get_link_and_content()
    get_word_content(lst)
    get_pr(lst)