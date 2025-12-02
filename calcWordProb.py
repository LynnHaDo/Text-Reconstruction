"""
Calculate P(candidate): the prob that word candidate appears in the normal text
P(candidate) = freq(candidate) + 1 / (N + V)
N: sum of all freq 
V: number of unique words
"""
import math
def calcWordProb(word, freq_map):
    total_freq = sum(freq_map.values())
    num_words = len(freq_map)
    cnt_word = freq_map.get(word, 0)

    prob = (cnt_word + 1) / (total_freq + num_words)
    return math.log(prob)