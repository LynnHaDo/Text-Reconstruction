from typing import Set
from util import set_up_corpus

LOWER_CASE_RANGE = range(97, 123)

class CandidateGeneratorUtil:
    def __init__(self, corpus_name = "brown"):
        self.corpus_name = corpus_name
        self.word_set = set(set_up_corpus(self.corpus_name))
        
    def generate_one_distance_candidates(self, candidate: str) -> Set[str]:
        """
        Generate all possible 1-edit-distance words to the candidate (lower case). Possible operations:
        * Substitution: replace one letter with another
        * Deletion: remove one letter
        * Insertion: add 1 letter
        * Transposition: swap 2 adjacent letters
        
        Params:
        * candidate: an invalid word
        
        Returns:
        * Set of valid candidates
        """
        
        if len(candidate) == 0:
            return set()
        
        successors = set()
        successors.update(self._generate_substitute_candidates(candidate))
        successors.update(self._generate_deletion_candidates(candidate))
        successors.update(self._generate_insertion_candidates(candidate))
        successors.update(self._generate_transposition_candidates(candidate))
        successors = {word for word in successors if word in self.word_set}
        return successors
        
    def _generate_substitute_candidates(self, candidate):
        candidates = set()
        
        for i in range(len(candidate)):
            possibilities = [candidate[:i] + chr(x) + candidate[i+1:] for x in LOWER_CASE_RANGE if x != ord(candidate[i])]
            candidates.update(possibilities)

        return candidates

    def _generate_deletion_candidates(self, candidate):
        candidates = set()
        
        for i in range(len(candidate)):
            new_word = candidate[:i] + candidate[i+1:]
            candidates.add(new_word)

        return candidates
    
    def _generate_insertion_candidates(self, candidate):
        candidates = set()
        
        for i in range(len(candidate) + 1):
            possibilities = [candidate[:i] + chr(x) + candidate[i:] for x in LOWER_CASE_RANGE]
            candidates.update(possibilities)

        return candidates
    
    def _generate_transposition_candidates(self, candidate):
        candidates = set()
        
        for i in range(1, len(candidate)):
            new_word = candidate[:i-1] + candidate[i] + candidate[i-1] + candidate[i+1:]
            candidates.add(new_word)

        return candidates
        
if __name__ == "__main__":
    generator = CandidateGeneratorUtil()
    # print(generator.generate_one_distance_candidates("jewlery"))