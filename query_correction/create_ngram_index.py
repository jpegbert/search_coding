
files = ['test.txt']

k = 3
ngram_mask = dict()
ngram_index = dict()
for filename in files:
    with open(filename, encoding="utf-8") as f:
        for line in f:
            info = line.strip().split('\t')
            query = ['_' + info[0] + '_', '_' + info[1] + '_']
            for q in query:
                for i in range(len(q) - k + 1):
                    kgram = q[i: i+k]
                    if kgram not in ngram_index:
                        ngram_index[kgram] = 0
                    ngram_index[kgram] += 1

                    mask_gram = kgram[:-1] + ''
                    if mask_gram not in ngram_mask:
                        ngram_mask[mask_gram] = set()
                    ngram_mask[mask_gram].add(kgram)


with open("ngram.data", 'w+') as f:
    for ngram, count in ngram_index.items():
        f.write("%s\t%s\n" % (ngram, count))

with open("ngram_mask.data", "w+") as f:
    for mask, cand in ngram_mask.items():
        attr = []
        for c in cand:
            attr.append(c + "" + str(ngram_index[c]))
        f.write("%s\t%s\n" % (mask, ''.join(attr)))
