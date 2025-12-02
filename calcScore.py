import sys
import os

from constants import DEFAULT_CORPUS_NAME

# Add project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from candidateGeneratorUtil import CandidateGeneratorUtil
from wordsegUtil import makeLanguageModels
from confusionMatrix import ConfusionMatrix
from cntWordCorpus import CountWordCorpus
from errorModel import ErrorModel
from calcWordProb import calcWordProb
import math

class AutoCorrect:
    def __init__(self, corpus_words, misspell_path="missp.dat"):
        self.unigramCost, self.bigramCost, self.freq_map, _ = makeLanguageModels(corpus_words)
        self.confusion_matrix = ConfusionMatrix()
        self.confusion_matrix.build_confusion_matrix(misspell_path)

        self.corpus_cnt = CountWordCorpus(corpus_words)
        self.corpus_cnt.update_cnt()

        self.error_model = ErrorModel(self.confusion_matrix, self.corpus_cnt)

    def calc_score(self, sentence, wrong_word, candidate):
        words = sentence.split()
        idx = words.index(wrong_word)
        prev_word = words[idx - 1] if idx > 0 else ""
        next_word = words[idx + 1] if idx < len(words) - 1 else ""

        em_prob = self.error_model.calcProbGivenCorrectWord(candidate, wrong_word)
        candidate_prob = calcWordProb(candidate, self.freq_map)
        candidate_log = math.log(candidate_prob) if candidate_prob > 0 else 0

        bayes_prob = math.log(em_prob) if em_prob > 0 else -1e9
        prev_prob = -self.bigramCost(prev_word, candidate) if prev_word else 0
        right_prob = -self.bigramCost(candidate, next_word) if next_word else 0

        return right_prob + prev_prob + bayes_prob + candidate_log
    
    def correct(self, sentence, wrong_word, candidate_list):
        best_candidate = None 
        max_score = float('-inf')
        for word in candidate_list:
            score = self.calc_score(sentence, wrong_word, word)
            if score > max_score:
                max_score = score
                best_candidate = word 
        return best_candidate
