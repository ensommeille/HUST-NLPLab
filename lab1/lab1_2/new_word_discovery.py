from collections import defaultdict
import math
import re
from data_u import get_texts_for_new_word_discovery, word2id

# 加载停用词表
def load_stopwords(file_path):
    stopwords = set()
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            stopwords.add(line.strip())
    return stopwords

def build_word2id(texts):
    word2id = {}
    for text in texts:
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', '', text)
        for word in text.split():
            if word not in word2id:
                word2id[word] = len(word2id)
    return word2id

def entropy(neighbors):
    total = sum(neighbors.values())
    if total == 0:
        return 0
    return -sum([count / total * math.log2(count / total) for count in neighbors.values()])

def cohesion(ngram, char_freq, ngram_freq):
    if len(ngram) == 1:
        return 1
    min_cohesion = float('inf')
    for i in range(1, len(ngram)):
        left = ngram[:i]
        right = ngram[i:]
        p_left = ngram_freq[left] / sum(ngram_freq.values())
        p_right = ngram_freq[right] / sum(ngram_freq.values())
        p_ngram = ngram_freq[ngram] / sum(ngram_freq.values())
        if p_left * p_right == 0:
            continue
        cur_cohesion = p_ngram / (p_left * p_right)
        min_cohesion = min(min_cohesion, cur_cohesion)
    return min_cohesion

def is_composed_of_new_words(ngram, new_words):
    for i in range(1, len(ngram)):
        left = ngram[:i]
        right = ngram[i:]
        if left in new_words and right in new_words:
            return True
    return False

def find_new_words(texts, min_freq=200, min_cohesion=2.0, min_entropy=1.0, min_len=2, max_len=4, stopwords=set()):
    texts = [text.lower().strip() for text in texts]
    texts = [re.sub(r'[^\w\s]', '', text) for text in texts]
    stopwords = load_stopwords('data/stopwords.txt')
    print(stopwords)

    # 统计词频
    char_freq = defaultdict(int)
    ngram_freq = defaultdict(int)
    left_neighbors = defaultdict(lambda: defaultdict(int))
    right_neighbors = defaultdict(lambda: defaultdict(int))

    for text in texts:
        for i in range(len(text)):
            char_freq[text[i]] += 1
            for length in range(min_len, min(max_len + 1, len(text) - i + 1)):
                ngram = text[i:i + length]
                ngram_freq[ngram] += 1
                if i > 0:
                    left_neighbors[ngram][text[i - 1]] += 1
                if i + length < len(text):
                    right_neighbors[ngram][text[i + length]] += 1

    # 复制 ngram_freq 进行遍历
    ngram_freq_copy = ngram_freq.copy()

    print(1)
    # 计算凝聚度和左右邻接熵
    new_words = []
    for ngram, freq in ngram_freq_copy.items():
        if freq < min_freq:
            continue
        if ngram in word2id:
            continue
        if is_composed_of_new_words(ngram, new_words):
            continue
        # 过滤包含停用词的 ngram
        if any(stopword in ngram for stopword in stopwords):
            continue
        coh = cohesion(ngram, char_freq, ngram_freq)
        left_ent = entropy(left_neighbors[ngram])
        right_ent = entropy(right_neighbors[ngram])
        if coh > min_cohesion and min(left_ent, right_ent) > min_entropy:
            new_words.append(ngram)
            print(ngram, freq, coh, left_ent, right_ent)

    return new_words

if __name__ == "__main__":
    texts = get_texts_for_new_word_discovery()
    # 加载停用词表
    print("加载停用词表...")
    stopwords = load_stopwords('data/stopwords.txt')  # 请确保 stopwords.txt 文件存在
    new_words = find_new_words(texts, stopwords=stopwords)
    print("发现的新词:", new_words)