from typing import Callable, List, Set

import shell
import util
import wordsegUtil


############################################################
# Problem 1b: Solve the segmentation problem under a unigram model

class SegmentationProblem(util.SearchProblem):
    def __init__(self, query: str, unigramCost: Callable[[str], float]):
        self.query = query
        self.unigramCost = unigramCost

    def startState(self):
        return 0

    def isEnd(self, state) -> bool:
        return state == len(self.query)

    def succAndCost(self, state):
        successors = []
        
        for i in range(state + 1, len(self.query) + 1):
            word = self.query[state:i]
            cost = self.unigramCost(word)
            successors.append((word, i, cost))
        
        return successors


def segmentWords(query: str, unigramCost: Callable[[str], float]) -> str:
    if len(query) == 0:
        return ''

    ucs = util.UniformCostSearch(verbose=0)
    ucs.solve(SegmentationProblem(query, unigramCost))

    if ucs.actions is None:
        return '' # cannot segment this query
    return ' '.join(ucs.actions) # minimum-cost path is the segmented words with lowest unigram cost


############################################################
# Problem 2b: Solve the vowel insertion problem under a bigram cost

class VowelInsertionProblem(util.SearchProblem):
    def __init__(self, queryWords: List[str], bigramCost: Callable[[str, str], float],
            possibleFills: Callable[[str], Set[str]]):
        self.queryWords = queryWords
        self.bigramCost = bigramCost
        self.possibleFills = possibleFills

    def startState(self):
        return (0, wordsegUtil.SENTENCE_BEGIN)

    def isEnd(self, state) -> bool:
        index, _ = state 
        return index == len(self.queryWords)

    def succAndCost(self, state):
        successors = []
        
        index, previous_word = state 
        current_word = self.queryWords[index]
        possible_words = self.possibleFills(current_word)
        
        if possible_words is None:
            possible_words.append(current_word)
        
        for word in possible_words:
            successors.append((word, (index + 1, word), self.bigramCost(previous_word, word)))
        
        return successors


def insertVowels(queryWords: List[str], bigramCost: Callable[[str, str], float],
        possibleFills: Callable[[str], Set[str]]) -> str:
    if len(queryWords) == 0:
        return ''

    ucs = util.UniformCostSearch(verbose=0)
    ucs.solve(VowelInsertionProblem(queryWords, bigramCost, possibleFills))

    if ucs.actions is None:
        return '' # cannot segment this query
    return ' '.join(ucs.actions) # minimum-cost path is the segmented words with lowest unigram cost


############################################################
# Problem 3b: Solve the joint segmentation-and-insertion problem

class JointSegmentationInsertionProblem(util.SearchProblem):
    def __init__(self, query: str, bigramCost: Callable[[str, str], float],
            possibleFills: Callable[[str], Set[str]]):
        self.query = query
        self.bigramCost = bigramCost
        self.possibleFills = possibleFills

    def startState(self):
        return (0, wordsegUtil.SENTENCE_BEGIN)

    def isEnd(self, state) -> bool:
        index, _ = state 
        return index == len(self.query)

    def succAndCost(self, state):
        successors = []
        
        index, previous_word = state 
        
        for end_index in range(index + 1, len(self.query) + 1):
            current_word = self.query[index:end_index]
            possible_words = self.possibleFills(current_word)
            
            if possible_words is None:
                continue 
            
            for word in possible_words:
                successors.append((word, (end_index, word), self.bigramCost(previous_word, word)))
        
        return successors


def segmentAndInsert(query: str, bigramCost: Callable[[str, str], float],
        possibleFills: Callable[[str], Set[str]]) -> str:
    if len(query) == 0:
        return ''

    ucs = util.UniformCostSearch(verbose=0)
    ucs.solve(JointSegmentationInsertionProblem(query, bigramCost, possibleFills))

    if ucs.actions is None:
        return '' # cannot segment this query
    return ' '.join(ucs.actions) # minimum-cost path is the segmented words with lowest bigram cost


############################################################

if __name__ == '__main__':
    shell.main()
