"""
Build 4 confusion matrices:
- delete
- insert 
- substitute
- transposition 
using from this link of corpora of misspellings: https://titan.dcs.bbk.ac.uk/~ROGER/missp.dat
"""
from collections import defaultdict
import re

def parse_birkbeck(path="missp.dat"):
    """
    - return list of tuples (correct word, misspell)
    """
    pair_words = []
    correct_word = None 
    with open(path, "r") as f:
        for line in f:
            word = line.strip()
            if not word:
                continue 
            if word.startswith("$"):
                correct_word = word[1:]
            else:
                wrong_word = word 
                pair_words.append((correct_word, wrong_word))
    return pair_words 


def get_edit_type(correct_word, wrong_word):
    """
    Return the edit type: 
    - "del", deleted_char, left_correct_char
    - "ins", inserted_char, left_correct_char
    - "sub", correct_char, wrong_char
    - "trans", first_char, second_char
    """
    m, n = len(correct_word), len(wrong_word)
    # edge case: skip all > 1-edit distance words
    if abs(m - n) > 1:
        return None
    
    # remove punctuation
    correct_word = re.sub(r'[^a-z]', '', correct_word.lower())
    wrong_word   = re.sub(r'[^a-z]', '', wrong_word.lower())

    correct_ptr = wrong_ptr = 0
    while correct_ptr < m and wrong_ptr < n and correct_word[correct_ptr] == wrong_word[wrong_ptr]:
        correct_ptr += 1
        wrong_ptr += 1
    # edge case: correct words
    if correct_ptr == m and wrong_ptr == n:
        return None
    
    # del type 
    if m == n + 1:
        deleted_char = correct_word[correct_ptr]
        left_correct_char = correct_word[correct_ptr - 1] if correct_ptr > 0 else '^'
        return ("del", deleted_char, left_correct_char)
    
    # insert type 
    if m == n - 1:
        inserted_char = wrong_word[wrong_ptr]
        left_correct_char = correct_word[correct_ptr - 1] if correct_ptr > 0 else '^'
        return ("insert", inserted_char, left_correct_char)
    
    # transposition or substitution 
    if m == n:
        # transpose (swap)
        if correct_ptr + 1 < m and wrong_ptr + 1 < n:
            if correct_word[correct_ptr] == wrong_word[wrong_ptr + 1] and correct_word[correct_ptr + 1] == wrong_word[wrong_ptr]:
                return ("trans", correct_word[correct_ptr], correct_word[correct_ptr + 1])
        # substitue 
        return ("sub", correct_word[correct_ptr], wrong_word[wrong_ptr])
    return None

del_matrix = defaultdict(lambda: defaultdict(int))
trans_matrix = defaultdict(lambda: defaultdict(int))
insert_matrix = defaultdict(lambda: defaultdict(int)) 
sub_matrix = defaultdict(lambda: defaultdict(int))

def build_confusion_matrix(correct_word, wrong_word):
    """
    - build 4 confusion matrices for 4 edit types
    """
    edit_type = get_edit_type(correct_word, wrong_word)
    
    if edit_type == None:
        return
    op = edit_type[0]
    if op == 'del':
        _, deleted_char, left_correct_char = edit_type 
        del_matrix[left_correct_char][deleted_char] += 1
    elif op == 'insert':
        _, inserted_char, left_correct_char = edit_type 
        insert_matrix[left_correct_char][inserted_char] += 1
    elif op == 'sub':
        _, correct_char, wrong_char = edit_type 
        sub_matrix[correct_char][wrong_char] += 1
    elif op == 'trans':
        _, correct_char, wrong_char = edit_type 
        trans_matrix[correct_char][wrong_char] += 1

pairs = parse_birkbeck("missp.dat")
for correct, wrong in pairs: 
    build_confusion_matrix(correct, wrong)
