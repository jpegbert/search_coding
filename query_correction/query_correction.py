#!/usr/bin/env python
import pypinyin
import editdistance
import random

ngram_file = "ngram.data"
mask_ngram_file = "ngram_mask.data"

K = 3
beam_size = 5
ngram_index = dict()
with open(ngram_file) as f:
    for line in f:
        info = line.strip().split('\t')
        ngram_index[info[0]] = int(info[1])

ngram_mask = dict()
with open(mask_ngram_file) as f:
    for line in f:
        info = line.strip().split('\t')
        if info[0] not in ngram_mask:
            ngram_mask[info[0]] = []

        cands = info[1].split('')
        for cand in cands:
            cand_info = cand.split('')
            item = dict()
            item["ngram"] = cand_info[0]
            item["count"] = int(cand_info[1])
            ngram_mask[info[0]].append(item)

def pinyin(text):
    py = pypinyin.pinyin(text, style=pypinyin.Style.TONE3)
    return ''.join([x[0] for x in py])

def rewrite_ngram(ngrams):
    candidates = []
    print("ngrams:", ngrams)
    for ngram in ngrams:
        print("ngram:", ngram)
        if ngram in ngram_index:
            print("has ngram:", ngram)
            candidates.append(ngram)
            continue
        else:
            new_ngram = ngram[:-1] + ''
            if new_ngram in ngram_mask:
                ngram_pinyin = pinyin(ngram)
                for mngrams in ngram_mask[new_ngram]:
                    cand_pinyin = pinyin(mngrams["ngram"])
                    mngrams["distance"] = editdistance.eval(ngram_pinyin, cand_pinyin)
                cands = sorted(ngram_mask[new_ngram], key = lambda k : k["distance"])
                best_distance = cands[0]["distance"]
                for c in cands:
                    if c["distance"] == best_distance:
                        candidates.append(c["ngram"])
                        print("rewrite [%s] to [%s]" % (ngram, c["ngram"]))
            else:
                print("replace new ngram [%s] failed" % new_ngram)
                candidates.append(ngram)
                continue
    # shuffle, get beam size cands
    random.shuffle(candidates)
    print("candidates:", candidates)
    return candidates[:beam_size]

def query_correct(query):
    q = '_' + query + '_'
    index = 0
    query_cands = set()
    query_cands.add(q[:K-1])
    complete_cands = set()
    while query_cands:
        ngrams = []
        for cands in query_cands:
            if index + 2 < len(q):
                ngrams.append(cands[-2:] + q[index + 2])
            else:
                ngrams.append(cands[-2:] + '_')
        new_ngrams = rewrite_ngram(ngrams)
        new_query_cands = set()
        for cands in query_cands:
            for gram in new_ngrams:
                if gram[-1] == '_':
                    complete_cands.add(cands + gram[-1])
                    continue
                if cands[-2:] == gram[:2]:
                    new_query_cands.add(cands + gram[-1])
        query_cands = new_query_cands
        index += 1

    best_distance = 1000
    best_cand = ""
    for cands in complete_cands:
        distance = editdistance.eval(q, cands)
        if distance < best_distance:
            best_cand = cands
            best_distance = distance

    return best_cand[1:-1]

if __name__ == '__main__':
    query = '宾馆的Wafi怎么链接'
    #query = '你知道吗'
    print("query:", query)
    new_query = query_correct(query)
    print("new query:", new_query)
