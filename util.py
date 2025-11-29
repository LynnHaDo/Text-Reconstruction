import heapq
from typing import Callable, Iterable, Set, Tuple, List
import pickle
import nltk
from nltk.corpus import webtext, brown
from constants import CORPUS_DIR, BROWN_CORPUS_FILENAME, WEBTEXT_CORPUS_FILENAME, DEFAULT_CORPUS_NAME
import os

CORPUS = None

def set_up_corpus(corpus_name: str):
    """
    Set up corpus given the name
    
    :param corpus_name: Name of corpus (brown or webtext) from nltk
    :type corpus_name: str
    """
    # Define the corpus path
    if corpus_name == 'webtext':
        corpus_filename = os.path.join(CORPUS_DIR, WEBTEXT_CORPUS_FILENAME)
    else:
        corpus_filename = os.path.join(CORPUS_DIR, BROWN_CORPUS_FILENAME)
        
    # Check if it exists
    if os.path.exists(corpus_filename):
        print(f"Loading cached corpus from {corpus_filename}...")
        with open(corpus_filename, 'rb') as f:
            raw_words = list(pickle.load(f))
            CORPUS = [w.lower() for w in raw_words if w.isalpha()]
            return CORPUS
        
    print(f"Corpus is not found in {corpus_filename}. Donwloading {corpus_name} from NLTK...")
    nltk.download(corpus_name)
    
    if corpus_name == "webtext":
        raw_words = list(webtext.words())
    else:
        raw_words = list(brown.words())
    
    # Save it so that we don't need to download it next time
    os.makedirs(CORPUS_DIR, exist_ok=True)
    with open(corpus_filename, 'wb') as f:
        pickle.dump(raw_words, f)
        CORPUS = [w.lower() for w in raw_words if w.isalpha()]
    
    return CORPUS

############################################################
# Abstract interfaces for search problems and search algorithms.

class SearchProblem:
    # Return the start state.
    def startState(self): raise NotImplementedError("Override me")

    # Return whether |state| is an end state or not.
    def isEnd(self, state) -> bool: raise NotImplementedError("Override me")

    # Return a list of (action, newState, cost) tuples corresponding to edges
    # coming out of |state|.
    def succAndCost(self, state): raise NotImplementedError("Override me")


class SearchAlgorithm:
    # First, call solve on the desired SearchProblem |problem|.
    # Then it should set two things:
    # - self.actions: list of actions that takes one from the start state to an end
    #                 state; if no action sequence exists, set it to None.
    # - self.totalCost: the sum of the costs along the path or None if no valid
    #                   action sequence exists.
    def solve(self, problem: SearchProblem): raise NotImplementedError("Override me")

############################################################
# Uniform cost search algorithm (Dijkstra's algorithm).

class UniformCostSearch(SearchAlgorithm):
    def __init__(self, verbose: int = 0):
        self.verbose = verbose

    def solve(self, problem: SearchProblem):
        # If a path exists, set |actions| and |totalCost| accordingly.
        # Otherwise, leave them as None.
        self.actions = None
        self.totalCost = None
        self.numStatesExplored = 0

        # Initialize data structures
        frontier = PriorityQueue()  # Explored states are maintained by the frontier.
        backpointers = {}  # map state to (action, previous state)

        # Add the start state
        startState = problem.startState()
        frontier.update(startState, 0)

        while True:
            # Remove the state from the queue with the lowest pastCost
            # (priority).
            state, pastCost = frontier.removeMin()
            if state == None: break
            self.numStatesExplored += 1
            if self.verbose >= 2:
                print(("Exploring %s with pastCost %s" % (state, pastCost)))

            # Check if we've reached an end state; if so, extract solution.
            if problem.isEnd(state):
                self.actions = []
                while state != startState:
                    action, prevState = backpointers[state]
                    self.actions.append(action)
                    state = prevState
                self.actions.reverse()
                self.totalCost = pastCost
                if self.verbose >= 1:
                    print(("numStatesExplored = %d" % self.numStatesExplored))
                    print(("totalCost = %s" % self.totalCost))
                    print(("actions = %s" % self.actions))
                return

            # Expand from |state| to new successor states,
            # updating the frontier with each newState.
            for action, newState, cost in problem.succAndCost(state):
                if self.verbose >= 3:
                    print(("  Action %s => %s with cost %s + %s" % (action, newState, pastCost, cost)))
                if frontier.update(newState, pastCost + cost):
                    # Found better way to go to |newState|, update backpointer.
                    backpointers[newState] = (action, state)
        if self.verbose >= 1:
            print("No path found")


# Data structure for supporting uniform cost search.
class PriorityQueue:
    def __init__(self):
        self.DONE = -100000
        self.heap = []
        self.priorities = {}  # Map from state to priority

    # Insert |state| into the heap with priority |newPriority| if
    # |state| isn't in the heap or |newPriority| is smaller than the existing
    # priority.
    # Return whether the priority queue was updated.
    def update(self, state, newPriority: int) -> bool:
        oldPriority = self.priorities.get(state)
        if oldPriority == None or newPriority < oldPriority:
            self.priorities[state] = newPriority
            heapq.heappush(self.heap, (newPriority, state))
            return True
        return False

    # Returns (state with minimum priority, priority)
    # or (None, None) if the priority queue is empty.
    def removeMin(self):
        while len(self.heap) > 0:
            priority, state = heapq.heappop(self.heap)
            if self.priorities[state] == self.DONE:
                continue  # Outdated priority, skip
            self.priorities[state] = self.DONE
            return state, priority
        return None, None  # Nothing left...

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_word = False 
        self.cost = float('inf') # unigram cost for better speed

class AutocompleteTrie:
    def __init__(self):
        self.root = TrieNode()
    
    def insert(self, word: str, cost: float):
        """
        Insert a word into the trie
        
        :param self: autocomplete trie
        :param word: word to insert to
        :type word: str
        :param cost: unigram cost of the word
        :type cost: float
        """
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_word = True 
        node.cost = cost
    
    def search_prefix(self, prefix: str) -> Set[str]|None:
        """
        Retrieves all words starting with prefix
        
        :param self: autocomplete trie
        :param prefix: prefix to search for the remaining word
        :type prefix: str
        :return: set of all words starting with the prefix
        :rtype: Set[str]
        """
        node = self.root
        
        for char in prefix:
            if char not in node.children:
                return None
            node = node.children[char]
        
        # Now node is the last char
        words = set()
        self._dfs(node, prefix, words)
        return words
    
    def _dfs(self, node: TrieNode, path: str, results: Set[str]):
        """
        Performs dfs from the starting node
        
        :param self: autocomplete trie
        :param node: node to start search from
        :type node: TrieNode
        :param path: path/string traversed so far
        :type path: str
        :param results: set of strings found so far
        :type results: Set[str]
        """
        if node.is_word:
            results.add(path)
        
        for next_char in node.children:
            self._dfs(node.children[next_char], path + next_char, results)

def make_autocomplete_trie(word_list: Iterable[str], unigramCost: Callable[[str], float]) -> AutocompleteTrie:
    """
    Builds an autocomplete trie
    
    :param word_list: list of words in corpus
    :type word_list: Iterable[str]
    :param unigramCost: function that takes in word and returns unigram cost
    :type unigramCost: Callable[[str], float]
    :return: trie with all words in corpus
    :rtype: AutocompleteTrie
    """
    trie = AutocompleteTrie()
    print("Building autocomplete trie...")
    for word in word_list:
        if word.isalpha():
            trie.insert(word.lower(), unigramCost(word.lower()))
    return trie

############################################################
# Simple examples of search problems to test your code for Problem 1.

# A simple search problem on the number line:
# Start at 0, want to go to 10, costs 1 to move left, 2 to move right.
class NumberLineSearchProblem:
    def startState(self) -> int: return 0

    def isEnd(self, state: int) -> bool: return state == 10

    def succAndCost(self, state: int) -> List[Tuple[str, int, int]]:
        return [('West', state - 1, 1), ('East', state + 1, 2)]


# A simple search problem on a square grid:
# Start at init position, want to go to (0, 0)
# cost 2 to move up/left, 1 to move down/right
class GridSearchProblem(SearchProblem):
    def __init__(self, size: int, x: int, y: int):
        self.size, self.start = size, (x, y)

    def startState(self) -> Tuple[int, int]:
        return self.start

    def isEnd(self, state: Tuple[int, int]) -> bool:
        return state == (0, 0)

    def succAndCost(self, state: Tuple[int, int]) -> List[Tuple[str, Tuple[int, int], int]]:
        x, y = state
        results = []
        if x - 1 >= 0: results.append(('North', (x - 1, y), 2))
        if x + 1 < self.size: results.append(('South', (x + 1, y), 1))
        if y - 1 >= 0: results.append(('West', (x, y - 1), 2))
        if y + 1 < self.size: results.append(('East', (x, y + 1), 1))
        return results

