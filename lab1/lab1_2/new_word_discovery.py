from collections import defaultdict
import math
from data_u import get_texts_for_new_word_discovery


def find_new_words(texts, min_freq=5, min_mi=2.0):
    # 统计词频
    char_freq = defaultdict(int)
    bigram_freq = defaultdict(int)
    for text in texts:
        for i in range(len(text)):
            char_freq[text[i]] += 1
            if i < len(text) - 1:
                bigram_freq[text[i:i + 2]] += 1

    # 计算互信息
    new_words = []
    for bigram, freq in bigram_freq.items():
        if freq < min_freq:
            continue
        p_x = char_freq[bigram[0]] / sum(char_freq.values())
        p_y = char_freq[bigram[1]] / sum(char_freq.values())
        p_xy = freq / sum(bigram_freq.values())
        mi = math.log(p_xy / (p_x * p_y))
        if mi > min_mi:
            new_words.append(bigram)

    return new_words


if __name__ == "__main__":
    texts = get_texts_for_new_word_discovery()
    new_words = find_new_words(texts)
    print("发现的新词:", new_words)
