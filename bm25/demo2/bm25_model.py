import numpy as np
from collections import Counter


class BM25_Model(object):
    def __init__(self, documents_list, k1=2, k2=1, b=0.5):
        self.documents_list = documents_list # 需要输入的文本列表,内部每个文本需要事先分好词
        self.documents_number = len(documents_list) # 文本总个数
        # 所有文本的平均长度
        self.avg_documents_len = sum([len(document) for document in documents_list]) / self.documents_number
        self.f = [] # 用于存储每个文本中每个词的出现的次数
        self.idf = {} # 用于存储每个词汇的权重值
        self.k1 = k1 # 一般取2
        self.k2 = k2 # 一般取1
        self.b = b # 一般取0.75
        self.init()

    def init(self):
        """
        求解文本集合中的f和idf变量
        """
        df = {}
        for document in self.documents_list:
            temp = {}
            for word in document:
                temp[word] = temp.get(word, 0) + 1
            self.f.append(temp)
            for key in temp.keys():
                df[key] = df.get(key, 0) + 1
        for key, value in df.items():
            self.idf[key] = np.log((self.documents_number - value + 0.5) / (value + 0.5))

    def get_score(self, index, query):
        """
        获取一个文本与文本列表中一个文本的bm25相似度值
        """
        score = 0.0
        document_len = len(self.f[index])
        qf = Counter(query)
        for q in query:
            if q not in self.f[index]:
                continue
            score += self.idf[q] * (self.f[index][q] * (self.k1 + 1) / (
                        self.f[index][q] + self.k1 * (1 - self.b + self.b * document_len / self.avg_documents_len))) * (
                                 qf[q] * (self.k2 + 1) / (qf[q] + self.k2))

        return score

    def get_documents_score(self, query):
        """
        获取一个文本与文本列表中所有文本的bm25相似度值
        """
        score_list = []
        for i in range(self.documents_number):
            score_list.append(self.get_score(i, query))
        return score_list
