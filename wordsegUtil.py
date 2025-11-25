import collections
import math
from typing import Set, Callable, List, Iterable, Iterator, Tuple
import nltk

SENTENCE_BEGIN = '-BEGIN-'


def sliding(xs: List[str], windowSize: int) -> Iterator[str]:
    for i in range(1, len(xs) + 1):
        yield xs[max(0, i - windowSize):i]


def removeAll(s: str, chars: Iterable[str]) -> str:
    return ''.join([c for c in s if c not in chars])


def alphaOnly(s: str) -> str:
    s = s.replace('-', ' ')
    return ''.join([c for c in s if c.isalpha() or c == ' '])


def cleanLine(l: str) -> str:
    return alphaOnly(l.strip().lower())


def words(l: str) -> List[str]:
    return l.split()


############################################################
# Make an n-gram model of words in text from a corpus.

def makeLanguageModels(word_list: Iterable[str],) -> Tuple[Callable[[str], float], Callable[[str, str], float]]:
    """
    Params:
    * word_list: list of (cleaned) words in the corpus
    
    Returns:
    * unigramCost and bigramModel
    """
    # Use NLTK to count frequencies
    unigramCounts = nltk.FreqDist(word_list) # map a word to frequency
    bigramCounts = nltk.FreqDist(nltk.bigrams(word_list)) # map a pair to frequency
    bitotalCounts = nltk.ConditionalFreqDist(nltk.bigrams(word_list)) # map a word to count of bigrams starting with word
    
    totalCounts = len(word_list)
    VOCAB_SIZE = 600000
    LONG_WORD_THRESHOLD = 5
    LENGTH_DISCOUNT = 0.15

    def unigramCost(x: str) -> float:
        if x not in unigramCounts:
            length = max(LONG_WORD_THRESHOLD, len(x))
            return -(length * math.log(LENGTH_DISCOUNT) + math.log(1.0) - math.log(VOCAB_SIZE))
        else:
            return math.log(totalCounts) - math.log(unigramCounts[x])

    def bigramModel(a: str, b: str) -> float:
        return math.log(bitotalCounts[a].N() + VOCAB_SIZE) - math.log(bigramCounts[(a, b)] + 1)

    return unigramCost, bigramModel


def logSumExp(x: float, y: float) -> float:
    lo = min(x, y)
    hi = max(x, y)
    return math.log(1.0 + math.exp(lo - hi)) + hi


def smoothUnigramAndBigram(unigramCost: Callable[[str], float], bigramModel: Callable[[str, str], float], a: float):
    """Coefficient `a` is Bernoulli weight favoring unigram"""

    # Want: -log( a * exp(-u) + (1-a) * exp(-b) )
    #     = -log( exp(log(a) - u) + exp(log(1-a) - b) )
    #     = -logSumExp( log(a) - u, log(1-a) - b )

    def smoothModel(w1: str, w2: str) -> float:
        u = unigramCost(w2)
        b = bigramModel(w1, w2)
        return -logSumExp(math.log(a) - u, math.log(1 - a) - b)

    return smoothModel


############################################################
# Make a map for inverse lookup of words without vowels -> possible
# full words

def makeInverseRemovalDictionary(word_list: Iterable[str], removeChars: Iterable[str]) -> Callable[[str], Set[str]]:
    """
    Params:
    * word_list: list of (cleaned) words in the corpus
    
    Returns:
    * a mapping from a word to valid filled words
    """
    wordsRemovedToFull = collections.defaultdict(set)

    for word in word_list:
        wordsRemovedToFull[removeAll(word, removeChars)].add(word)

    wordsRemovedToFull = dict(wordsRemovedToFull)

    def possibleFills(short: str) -> Set[str]:
        return wordsRemovedToFull.get(short, set())

    return possibleFills
