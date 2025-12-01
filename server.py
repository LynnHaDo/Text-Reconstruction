from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import solvers
import wordsegUtil
from constants import DEFAULT_CORPUS_NAME, AUTOCORRECT_ENDPOINT, AUTOCOMPLETE_ENDPOINT
from util import set_up_corpus, make_autocomplete_trie
from candidateGeneratorUtil import CandidateGeneratorUtil
from calcScore import AutoCorrect
from sklearnUtil import NeuralScorer, NeuralTrainer, is_model_present

app = Flask(__name__)
CORS(app)

# Loaded models
unigramCost = None
bigramCost = None
possibleFills = None
sklearnCandidateScorer = None

# Initializing models and corpus
print("Initializing server and loading models...")
CORPUS = set_up_corpus(DEFAULT_CORPUS_NAME)
unigramCost, bigramCost, _ = wordsegUtil.makeLanguageModels(CORPUS)
possibleFills = wordsegUtil.makeInverseRemovalDictionary(CORPUS, 'aeiou')
print("Models Loaded! Server is ready.")

print("Loading autocorrect...")
auto_correct = AutoCorrect(CORPUS, "missp.dat")
candidate_generator = CandidateGeneratorUtil(DEFAULT_CORPUS_NAME)
print("Auto correct is ready")

print("Loading autocomplete trie...")
autocomplete_trie = make_autocomplete_trie(CORPUS, unigramCost)
print("Autocomplete trie is ready!")

print("Checking if scikit-learn classifier model is trained...")
if not is_model_present():
    print("Scikit-learn classifier model is not found. Training process starts...")
    trainer = NeuralTrainer(CORPUS)
    trainer.train()
print("Scikit-learn model is ready!")
sklearnCandidateScorer = NeuralScorer()


# API endpoints
@app.route(AUTOCORRECT_ENDPOINT, methods=['POST'])
def autocorrect_text():
    data = request.json
    text = data.get('text', '') # selected word to fix
    mode = data.get('mode', 'both') # seg, ins, or both
    sentence = data.get('sentence', "")
    if not text:
        return jsonify({'error': 'No text provided.'}), 400
    
    # Clean the text
    cleanedText = wordsegUtil.cleanLine(text)
    result = ""
    
    match mode:
        case 'seg':
            parts = wordsegUtil.words(cleanedText)
            # Apply segmentWords to each part
            result = ' '.join(solvers.segmentWords(part, unigramCost) for part in parts)
        case 'ins':
            ws = [wordsegUtil.removeAll(w, 'aeiou') for w in wordsegUtil.words(cleanedText)]
            result = solvers.insertVowels(ws, bigramCost, possibleFills)
        case 'autocorrect':
            candidate_list = candidate_generator.generate_one_distance_candidates(cleanedText)
            result = auto_correct.correct(sentence, cleanedText, candidate_list)
        case _: # default to both
            smoothCost = wordsegUtil.smoothUnigramAndBigram(unigramCost, bigramCost, 0.2)
            parts = [wordsegUtil.removeAll(w, 'aeiou') for w in wordsegUtil.words(cleanedText)]
            # Apply segmentAndInsert
            result = ' '.join(
                solvers.segmentAndInsert(part, smoothCost, possibleFills)
                for part in parts
            )
    
    return jsonify({'original': text, 'corrected': result})

@app.route(AUTOCOMPLETE_ENDPOINT, methods=['POST'])
def autocomplete_text():
    data = request.json
    text = data.get('text', '') # incomplete sentence
    
    if not text:
        return jsonify({'suggestions': []})
    
    # Clean the text
    cleanedText = wordsegUtil.cleanLine(text)
    # Tokenize 
    tokens = wordsegUtil.words(cleanedText)
    
    # There are 2 cases
    # (1) User finished a word. Predict the next word
    # (2) User has not finished the word. Complete the current word
    if text.endswith(' '):
        # Case 1
        prefix = ""
        previous_word = tokens[-1] if tokens else wordsegUtil.SENTENCE_BEGIN
        previous_previous_word = tokens[-2] if len(tokens) >= 2 else wordsegUtil.SENTENCE_BEGIN
    else:
        # Case 2
        prefix = tokens[-1]
        previous_word = tokens[-2] if len(tokens) > 1 else wordsegUtil.SENTENCE_BEGIN
        previous_previous_word = tokens[-3] if tokens and len(tokens) >= 3 else wordsegUtil.SENTENCE_BEGIN
    
    # Get suggestions
    # Solution 1: Use bigram cost model 
    # suggestions = solvers.autocomplete(prefix, previous_word, autocomplete_trie, bigramCost)
    
    # Solution 2: Use neural network
    suggestions = autocomplete_trie.search_prefix(prefix)
    ranked_suggestions = sklearnCandidateScorer.get_candidate_costs(previous_word, previous_previous_word, suggestions, bigramCost)
    ranked_suggestions.sort(key=lambda x: x[1])
    top_suggestions = [x[0] for x in ranked_suggestions[:5]]
    
    return jsonify({'suggestions': top_suggestions})

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port = port)