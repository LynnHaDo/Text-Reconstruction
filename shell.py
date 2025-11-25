import argparse
import submission
import sys
import os
import wordsegUtil
import pickle
import nltk
from nltk.corpus import webtext, brown
from constants import CORPUS_DIR, BROWN_CORPUS_FILENAME, WEBTEXT_CORPUS_FILENAME, DEFAULT_CORPUS_NAME

CORPUS = None

def parseArgs():
    p = argparse.ArgumentParser()
    p.add_argument('--text-corpus', help='Text training corpus')
    p.add_argument('--model', help='Always use this model')
    return p.parse_args()


# REPL and main entry point
def repl(unigramCost, bigramCost, possibleFills, command=None):
    """REPL: read, evaluate, print, loop"""

    while True:
        sys.stdout.write('>> ')
        sys.stdout.flush()  # NOTE: added by Arjun basis things to fix doc
        line = sys.stdin.readline().strip()
        if not line:
            break

        if command is None:
            cmdAndLine = line.split(None, 1)
            cmd, line = cmdAndLine[0], ' '.join(cmdAndLine[1:])
        else:
            cmd = command
            line = line

        print('')

        if cmd == 'help':
            print('Usage: <command> [arg1, arg2, ...]')
            print('')
            print('Commands:')
            print(('\n'.join(a + '\t\t' + b for a, b in [
                ('help', 'This'),
                ('seg', 'Segment character sequences as in 1b'),
                ('ins', 'Insert vowels into words as in 2b'),
                ('both', 'Joint segment-and-insert as in 3b'),
                ('fills', 'Query possibleFills() to see possible vowel-fillings of a word'),
                ('ug', 'Query unigram cost function, treating input as a single word'),
                ('bg', 'Call bigram cost function on the last two words of the input'),
            ])))
            print('')
            print('Enter empty line to quit')

        elif cmd == 'seg':
            line = wordsegUtil.cleanLine(line)
            parts = wordsegUtil.words(line)
            print(('  Query (seg):', ' '.join(parts)))
            print('')
            print(('  ' + ' '.join(
                submission.segmentWords(part, unigramCost) for part in parts)))

        elif cmd == 'ins':
            line = wordsegUtil.cleanLine(line)
            ws = [wordsegUtil.removeAll(w, 'aeiou') for w in wordsegUtil.words(line)]
            print(('  Query (ins):', ' '.join(ws)))
            print('')
            print(('  ' + submission.insertVowels(ws, bigramCost, possibleFills)))

        elif cmd == 'both':
            line = wordsegUtil.cleanLine(line)
            smoothCost = wordsegUtil.smoothUnigramAndBigram(unigramCost, bigramCost, 0.2)
            parts = [wordsegUtil.removeAll(w, 'aeiou') for w in wordsegUtil.words(line)]
            print(('  Query (both):', ' '.join(parts)))
            print('')
            print(('  ' + ' '.join(
                submission.segmentAndInsert(part, smoothCost, possibleFills)
                for part in parts
            )))

        elif cmd == 'fills':
            line = wordsegUtil.cleanLine(line)
            print(('\n'.join(possibleFills(line))))

        elif cmd == 'ug':
            line = wordsegUtil.cleanLine(line)
            print((unigramCost(line)))

        elif cmd == 'bg':
            grams = tuple(wordsegUtil.words(line))
            prefix, ending = grams[-2], grams[-1]
            print((bigramCost(prefix, ending)))

        else:
            print(('Unrecognized command:', cmd))

        print('')

def set_up_corpus(corpus_name: str):
    if corpus_name == 'webtext':
        corpus_filename = os.path.join(CORPUS_DIR, WEBTEXT_CORPUS_FILENAME)
        raw_words = list(webtext.words())
    else:
        corpus_filename = os.path.join(CORPUS_DIR, BROWN_CORPUS_FILENAME)
        raw_words = list(brown.words())

    nltk.download(corpus_name)
    
    if not os.path.exists(corpus_filename):
        print(f"Saving to {corpus_filename}...")
        os.makedirs(CORPUS_DIR, exist_ok=True)
        with open(corpus_filename, 'wb') as f:
            pickle.dump(raw_words, f)

    with open(corpus_filename, 'rb') as f:
        raw_words = list(pickle.load(f))
        CORPUS = [w.lower() for w in raw_words if w.isalpha()]
    
    return CORPUS

def main():
    args = parseArgs()
    if args.model and args.model not in ['seg', 'ins', 'both']:
        print(('Unrecognized model:', args.model))
        sys.exit(1)

    corpus_name = args.text_corpus or DEFAULT_CORPUS_NAME
    set_up_corpus(corpus_name)

    sys.stdout.write('Training language cost functions [corpus: %s]... ' % corpus_name)
    sys.stdout.flush()

    unigramCost, bigramCost = wordsegUtil.makeLanguageModels(CORPUS)
    possibleFills = wordsegUtil.makeInverseRemovalDictionary(CORPUS, 'aeiou')

    print('Done!')
    print('')

    repl(unigramCost, bigramCost, possibleFills, command=args.model)