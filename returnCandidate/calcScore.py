from collections import Counter 
from confusionMatrix import get_edit_type, del_matrix, sub_matrix, trans_matrix, insert_matrix
from calcWordProb import calcWordProb
import math

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
        return float('-inf')
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
        num = sub_matrix[wrong_char][correct_char] + 1
        denom = cnt_char[correct_char] + 1
        return num / denom 
    
    elif op == 'trans':
        _, correct_char, wrong_char = edit_type
        num = trans_matrix[correct_char][wrong_char] + 1
        denom = cnt_pair[correct_char + wrong_char] + 1
        return num / denom
    return float('-inf')

def calcFinalScore(wrong_word, candidate_list, freq_map):
    max_score = float('-inf')
    best_candidate = []
    for word in candidate_list:
        word_prob = calcWordProb(word, freq_map)
        bayes_prob = math.log(calcProbGivenCorrectWord(word, wrong_word))
        curr_score = word_prob + bayes_prob 
        if curr_score > max_score:
            max_score = curr_score 
            best_candidate.append(word)
        elif curr_score == max_score:
            best_candidate.append(word)
    return best_candidate
vocab = {"actress": 10, "across": 100}
print(calcFinalScore("acress", ["actress", "across"], vocab))

