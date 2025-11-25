from collections import Counter 
from confusionMatrix import get_edit_type, del_matrix, sub_matrix, trans_matrix, insert_matrix
import math
import sys
import os

# Add project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wordsegUtil import makeLanguageModels
import nltk
from nltk.corpus import webtext

# Download on first run
nltk.download("webtext")

# Load corpus and clean it:
CORPUS = [w.lower() for w in webtext.words() if w.isalpha()]


cnt_char = Counter()
cnt_pair = Counter()
def calcDenom(pair_words):
    for correct_word, _ in pair_words:
        for char in correct_word:
            cnt_char[char] += 1
        for i in range(len(correct_word) - 1):
            pair = correct_word[i:i + 2]
            cnt_pair[pair] += 1

def calcProbGivenCorrectWord(correct_word, wrong_word):
    edit_type = get_edit_type(correct_word, wrong_word)
    if edit_type is None:
        return 0.0
    op = edit_type[0]
    
    if op == 'del':
        _, deleted_char, correct_char = edit_type 
        num = del_matrix[correct_char][deleted_char] + 1
        denom = cnt_pair[correct_char + deleted_char] + 1
        return num / denom 
    
    elif op == 'insert':
        _, inserted_char, correct_char = edit_type
        num = insert_matrix[correct_char][inserted_char] + 1
        denom = cnt_char[correct_char] + 1
        return num / denom 
    
    elif op == 'sub':
        _, correct_char, wrong_char = edit_type
        num = sub_matrix[correct_char][wrong_char] + 1
        denom = cnt_char[correct_char] + 1
        return num / denom 
    
    elif op == 'trans':
        _, correct_char, wrong_char = edit_type
        num = trans_matrix[correct_char][wrong_char] + 1
        denom = cnt_pair[correct_char + wrong_char] + 1
        return num / denom
    return 0.0

unigramCost, bigramCost, freq_map = makeLanguageModels(CORPUS)

def calcFinalScore(sentence, wrong_word, candidate_list, freq_map):
    words = sentence.split()
    idx = words.index(wrong_word)
    prev_word = words[idx - 1] if idx > 0 else ""
    next_word = words[idx + 1] if idx < len(words) - 1 else ""
    best_candidate = [] 
    max_score = float('-inf')
    lambda_mix = 0.5
    for word in candidate_list:
        # print(word, get_edit_type(word, wrong_word))
        # word_prob = calcWordProb(word, freq_map)
        em_prob = calcProbGivenCorrectWord(word, wrong_word)

        bayes_prob = math.log(em_prob) if em_prob > 0 else -1e9
        prev_prob = -bigramCost(prev_word, word) if prev_word else 0
        left_lm = lambda_mix * (-unigramCost(word)) + (1 - lambda_mix) * prev_prob
        right_prob = -bigramCost(word, next_word) if next_word else 0
        right_lm = lambda_mix * (-unigramCost(next_word)) + (1 - lambda_mix) * right_prob
        # print("====", word, "====")
        # print("left_lm  =", prev_prob)
        # print("left_lm  =", left_lm)

        # print("right_lm =", right_prob)
        # print("right_lm =", right_lm)

        # print("error_lm =", bayes_prob)
        # score =  prev_prob + right_prob
        score = right_lm + left_lm + bayes_prob
        # print("curr_score, word", score, word)
        if score > max_score:
            max_score = score 
            best_candidate = word

    return best_candidate
sentence = "She picked a frash apple from the tree"
print(calcFinalScore(sentence, "frash",
                     [
'flash', 'fresh', 'brash', 'crash', 'rash', 'trash'

                         ], 
                     freq_map))
