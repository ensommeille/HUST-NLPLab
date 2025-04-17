class Tokenizer(object):
    def __init__(self, words, max_len):
        self.words = words
        self.max_len = max_len

    def fmm_split(self, text):
        '''
        正向最大匹配分词算法
        :param text: 待分词字符串
        :return: 分词结果，以list形式存放，每个元素为分出的词
        '''
        result = []
        while text:
            # 取出前max_len个字符
            word = text[:self.max_len]
            # 如果前max_len个字符不在词典中，则逐渐缩小长度，直到找到一个在词典中的词
            while word not in self.words and len(word) > 0:
                word = word[:-1]
            if word:
                result.append(word)
                text = text[len(word):]
            else:
                result.append(text[0])
                text = text[1:]
        return result

    def rmm_split(self, text):
        '''
        逆向最大匹配分词算法
        :param text: 待分词字符串
        :return: 分词结果，以list形式存放，每个元素为分出的词
        '''
        result = []
        while text:
            # 取出后max_len个字符
            word = text[-self.max_len:]
            # 如果后max_len个字符不在词典中，则逐渐缩小长度，直到找到一个在词典中的词
            while word not in self.words and len(word) > 0:
                word = word[1:]
            if word:
                result.append(word)
                text = text[:-len(word)]
            else:
                result.append(text[-1])
                text = text[:-1]
        return result[::-1]

    def count_single_char(self, result):
        """
        统计分词结果中单个字符的数量
        """
        return sum(len(word) == 1 for word in result)

    def bimm_split(self, text):
        '''
        双向最大匹配分词算法
        :param text: 待分词字符串
        :return: 分词结果，以list形式存放，每个元素为分出的词
        '''
        fmm_result = self.fmm_split(text)
        rmm_result = self.rmm_split(text)
        # 计算两个结果的词数
        fmm_len = len(fmm_result)
        rmm_len = len(rmm_result)

        # 如果正反向分词结果词数不同，取分词数量少的那个
        if fmm_len < rmm_len:
            result = fmm_result
        elif fmm_len > rmm_len:
            result = rmm_result
        else:
            # 如果分词结果词数相同
            if fmm_result == rmm_result:
                # 分词结果相同，没有歧义，返回任意一个
                result = fmm_result
            else:
                # 分词结果不同，返回其中单字数量较少的那个
                fmm_single_count = self.count_single_char(fmm_result)
                rmm_single_count = self.count_single_char(rmm_result)
                if fmm_single_count < rmm_single_count:
                    result = fmm_result
                else:
                    result = rmm_result
        return result


def load_dict(path):
    tmp = set()
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            word = line.strip().split(' ')[0]
            tmp.add(word)
    return tmp


if __name__ == '__main__':
    words = load_dict('dict.txt')
    max_len = max(map(len, [word for word in words]))

    # test
    tokenizer = Tokenizer(words, max_len)
    texts = [
        '研究生命的起源',
        '无线电法国别研究',
        '人要是行，干一行行一行，一行行行行行，行行行干哪行都行。'
    ]
    for text in texts:
        # 前向最大匹配
        print('前向最大匹配:', '/'.join(tokenizer.fmm_split(text)))
        # 后向最大匹配
        print('后向最大匹配:', '/'.join(tokenizer.rmm_split(text)))
        # 双向最大匹配
        print('双向最大匹配:', '/'.join(tokenizer.bimm_split(text)))
        print('')
