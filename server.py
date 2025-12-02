from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import submission
import wordsegUtil
from constants import DEFAULT_CORPUS_NAME, TEXT_PROCESSING_ENDPOINT
from shell import set_up_corpus
from candidateGeneratorUtil import CandidateGeneratorUtil
from calcScore import AutoCorrect

app = Flask(__name__)
CORS(app)

# Loaded models
unigramCost = None
bigramCost = None
possibleFills = None

# Initializing models and corpus
print("Initializing server and loading models...")
CORPUS = set_up_corpus(DEFAULT_CORPUS_NAME)
unigramCost, bigramCost, _ = wordsegUtil.makeLanguageModels(CORPUS)
possibleFills = wordsegUtil.makeInverseRemovalDictionary(CORPUS, 'aeiou')
print("Models Loaded! Server is ready.")

print("Loading autocorrect...")
auto_correct = AutoCorrect(CORPUS, "missp.dat")
print("Auto correct is ready")

candidate_generator = CandidateGeneratorUtil(DEFAULT_CORPUS_NAME)

# API endpoints
@app.route(TEXT_PROCESSING_ENDPOINT, methods=['POST'])
def process_text():
    data = request.json
    text = data.get('text', '')
    mode = data.get('mode', 'both') # seg, ins, or both
    sentence = data.get('sentence', "")
    if not text:
        return jsonify({'error': 'No text provided.'}), 400
    
    # Clean the text
    # user boi den
    cleanedText = wordsegUtil.cleanLine(text)
    
    result = ""
    
    match mode:
        case 'seg':
            parts = wordsegUtil.words(cleanedText)
            # Apply segmentWords to each part
            result = ' '.join(submission.segmentWords(part, unigramCost) for part in parts)
        case 'ins':
            ws = [wordsegUtil.removeAll(w, 'aeiou') for w in wordsegUtil.words(cleanedText)]
            result = submission.insertVowels(ws, bigramCost, possibleFills)
        case 'autocorrect':
            candidate_generator = CandidateGeneratorUtil(DEFAULT_CORPUS_NAME)
            candidate_list = candidate_generator.generate_one_distance_candidates(cleanedText)
            # change to different corpus if no word in candidate list 
            if not candidate_list:
                candidate_generator = CandidateGeneratorUtil("brown" if DEFAULT_CORPUS_NAME == 'webtext' else 'webtext') 
                candidate_list = candidate_generator.generate_one_distance_candidates(cleanedText)
                
            result = auto_correct.correct(sentence, cleanedText, candidate_list)

        case _: # default to both
            smoothCost = wordsegUtil.smoothUnigramAndBigram(unigramCost, bigramCost, 0.2)
            parts = [wordsegUtil.removeAll(w, 'aeiou') for w in wordsegUtil.words(cleanedText)]
            # Apply segmentAndInsert
            result = ' '.join(
                submission.segmentAndInsert(part, smoothCost, possibleFills)
                for part in parts
            )
    
    return jsonify({'original': text, 'corrected': result})

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port = port, debug=True)