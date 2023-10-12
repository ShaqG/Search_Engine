doc_list = ['dict1.txt', 'dict2.txt', 'dict3.txt']

s = ""
dic = {}


def findit(start, ch):
    while (start < len(s)):
        if (ord(s[start]) == ord(ch)):
            return start
        start += 1
    return -1


def doit(doc_name):
    result = []
    # dic = {}
    global dic
    file = open(doc_name, 'r')
    global s
    s = file.readline()
    file.close()
    current = 1
    while (findit(current, '{') != -1):
        # print(current)
        p1 = findit(current, '\'')
        p2 = findit(p1 + 1, '\'')
        stem = s[(p1 + 1):(p2)]
        start = p1
        end = findit(start, '}')
        end -= 1
        if not stem in dic:
            dic[stem] = []
        dic[stem].append((doc_name, start, end))
        current = end + 3
    # return dic


if __name__ == "__main__":
    for i in doc_list:
        doit(i)
    file = open("indexer_in.txt", "w")
    file.write(str(dic))
    file.close()