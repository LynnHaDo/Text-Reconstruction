class ErrorModel:
    def __init__(self, confusion_matrix, corpus_cnt):
        self.confusion_matrix = confusion_matrix
        self.cnt_pair = corpus_cnt.cnt_pair
        self.cnt_char = corpus_cnt.cnt_char
    
    def calcProbGivenCorrectWord(self, correct_word, wrong_word):
        edit_type = self.confusion_matrix.get_edit_type(correct_word, wrong_word)
        if edit_type is None:
            return 0.0
        op = edit_type[0]
        
        if op == 'del':
            _, deleted_char, correct_char = edit_type 
            num = self.confusion_matrix.del_matrix[correct_char][deleted_char] + 1
            denom = self.cnt_pair[correct_char + deleted_char] + 1
            return num / denom 
        
        elif op == 'insert':
            _, inserted_char, correct_char = edit_type
            num = self.confusion_matrix.insert_matrix[correct_char][inserted_char] + 1
            denom = self.cnt_char[correct_char] + 1
            return num / denom 
        
        elif op == 'sub':
            _, correct_char, wrong_char = edit_type
            num = self.confusion_matrix.sub_matrix[correct_char][wrong_char] + 1
            denom = self.cnt_char[correct_char] + 1
            return num / denom 
        
        elif op == 'trans':
            _, correct_char, wrong_char = edit_type
            num = self.confusion_matrix.trans_matrix[correct_char][wrong_char] + 1
            denom = self.cnt_pair[correct_char + wrong_char] + 1
            return num / denom
        return 0.0