from collections import defaultdict

class CountWordCorpus:
    def __init__(self, corpus_words):
        self.corpus_words = corpus_words
        self.cnt_char = defaultdict(int)
        self.cnt_pair = defaultdict(int)
        self.update_cnt()
    
    def update_cnt(self):
        for word in self.corpus_words:
            for char in word:
                self.cnt_char[char] += 1
            
            for i in range(len(word) - 1):
                pair = word[i:i + 2]
                self.cnt_pair[pair] += 1