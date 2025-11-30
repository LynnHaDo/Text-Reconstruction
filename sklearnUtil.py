import os
import pickle
from typing import Callable, List, Set
import nltk
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import OneHotEncoder
from constants import ENCODER_FILENAME, MLP_CLASSIFIER_MODEL_FILENAME, MODELS_DIR, VOCAB_TO_IDX_FILENAME
import numpy as np

MODEL_FIT_PATH = f"{MODELS_DIR}/{MLP_CLASSIFIER_MODEL_FILENAME}"
VOCAB_TO_IDX_PATH = f"{MODELS_DIR}/{VOCAB_TO_IDX_FILENAME}"
ENCODER_PATH = f"{MODELS_DIR}/{ENCODER_FILENAME}"

def is_model_present():
    return os.path.exists(MODEL_FIT_PATH) and \
           os.path.exists(VOCAB_TO_IDX_PATH) and \
           os.path.exists(ENCODER_PATH)

class NeuralTrainer:
    def __init__(self, corpus: List[str]):
        """
        Sets up mapping from vocab -> index
        
        :param self: a neural trainer object
        :param corpus: list of words available
        :type corpus: List[str]
        """
        self.vocab = list(set(corpus)) # unique words
        self.word_to_idx = {word: i for i, word in enumerate(self.vocab)}
        self.trigrams = list(nltk.ngrams(corpus, 3)) # context (2 words) -> target (1 word)
    
    def _prepare_data(self):
        """
        Prepare X and y to input to Scikit-learn model.
        """
        inputs = []
        targets = []
        
        for w1, w2, w3 in self.trigrams:
            inputs.append([self.word_to_idx[w1], self.word_to_idx[w2]])
            targets.append(self.word_to_idx[w3])
        
        return inputs, targets
    
    def _save_models(self, model_fit: MLPClassifier, vocab_to_idx: dict, encoder: OneHotEncoder):
        os.makedirs(MODELS_DIR, exist_ok=True)
        with open(MODEL_FIT_PATH, 'wb') as f:
            pickle.dump(model_fit, f)
        with open(VOCAB_TO_IDX_PATH, 'wb') as f:
            pickle.dump(vocab_to_idx, f)
        with open(ENCODER_PATH, 'wb') as f:
            pickle.dump(encoder, f)
    
    def train(self):
        """
        Train an MLP model and save models. Run ONCE.
        
        :param self: Description
        """
        inputs, targets = self._prepare_data()
        encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=True) 
        # Learn the vocab structure and transform inputs into sparse matrix
        encoded_inputs = encoder.fit_transform(inputs)
        
        classifier = MLPClassifier(hidden_layer_sizes=(128,),
                                   learning_rate='adaptive',
                                   early_stopping=True,
                                   max_iter=200,
                                   verbose=True)
        classifier.fit(encoded_inputs, targets)

        self._save_models(classifier, self.word_to_idx, encoder)
        
class NeuralScorer:
    def __init__(self):
        print("Loading Scikit-Learn Model...")
        if not is_model_present():
            raise FileNotFoundError("Run NeuralTrainer.train() first to generate model fit first!")
        
        with open(MODEL_FIT_PATH, 'rb') as f:
            self.model_fit = pickle.load(f)
        with open(VOCAB_TO_IDX_PATH, 'rb') as f:
            self.word_to_idx = pickle.load(f)
        with open(ENCODER_PATH, 'rb') as f:
            self.encoder = pickle.load(f)
        
        self.vocab_size = len(self.word_to_idx)
    
    def get_candidate_costs(self, 
                            previous_word: str, 
                            previous_previous_word: str,
                            candidates: Set[str],
                            bigramCost: Callable[[str, str], float]) -> List[tuple[str, float]]:
        """
        Get the cost of potential next words based on previous word.
        
        :param self: Description
        :param previous_word: previous word
        :type previous_word: str
        :param previous_previous_word: the word before previous word
        :type previous_previous_word: str
        :param candidates: Set of candidates for next word to `previous_word`
        :type candidates: Set[str]
        :param bigramCost: function that outputs the cost for 2 consecutive words
        :type bigramCost: Callable[[str, str], float]
        :return: List of candidate -> cost tuples
        :rtype: List[tuple[str, float]]
        """
        prev_idx = self.word_to_idx.get(previous_word)
        prev_prev_idx = self.word_to_idx.get(previous_previous_word)
        
        if prev_idx is None or prev_prev_idx is None: 
            # Word is not found in corpus. Defaults to bigram cost
            return [(w, bigramCost(previous_word, w)) for w in candidates]
        
        encoded_input = self.encoder.transform([[prev_prev_idx, prev_idx]]) # transform index into one-hot vector
        all_log_probs = self.model_fit.predict_log_proba(encoded_input)[0]
        
        results = []
        
        for word in candidates:
            candidate_idx = self.word_to_idx.get(word)
            
            if candidate_idx is not None:
                try:
                    output_idx = np.searchsorted(self.model_fit.classes_, candidate_idx)
                    if output_idx < len(self.model_fit.classes_) and self.model_fit.classes_[output_idx] == candidate_idx:
                        log_prob = all_log_probs[output_idx]
                        cost = -log_prob
                    else:
                        cost = 15 # Word in trie but neural network didn't learn it
                except:
                    cost = 15 
            else:
                cost = 20
            results.append((word, cost))
        
        return results