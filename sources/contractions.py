# -*- coding: utf-8 -*-
import re

"""
List of popular contractions
"""

# https://github.com/dipanjanS/practical-machine-learning-with-python/blob/master/bonus%20content/nlp%20proven%20approach/contractions.py

CONTRACTION_MAP = {
    "ain't": "is not",
    "aren't": "are not",
    "can't": "cannot",
    "can't've": "cannot have",
    "'cause": "because",
    "could've": "could have",
    "couldn't": "could not",
    "couldn't've": "could not have",
    "didn't": "did not",
    "doesn't": "does not",
    "don't": "do not",
    "hadn't": "had not",
    "hadn't've": "had not have",
    "hasn't": "has not",
    "haven't": "have not",
    "he'd": "he would",
    "he'd've": "he would have",
    "he'll": "he will",
    "he'll've": "he he will have",
    "he's": "he is",
    "here's": "here is",
    "how'd": "how did",
    "how'd'y": "how do you",
    "how'll": "how will",
    "how's": "how is",
    "I'd": "I would",
    "I'd've": "I would have",
    "I'll": "I will",
    "I'll've": "I will have",
    "I'm": "I am",
    "I've": "I have",
    "i'd": "i would",
    "i'd've": "i would have",
    "i'll": "i will",
    "i'll've": "i will have",
    "i'm": "i am",
    "i've": "i have",
    "isn't": "is not",
    "it'd": "it would",
    "it'd've": "it would have",
    "it'll": "it will",
    "it'll've": "it will have",
    "it's": "it is",
    "let's": "let us",
    "ma'am": "madam",
    "mayn't": "may not",
    "might've": "might have",
    "mightn't": "might not",
    "mightn't've": "might not have",
    "must've": "must have",
    "mustn't": "must not",
    "mustn't've": "must not have",
    "needn't": "need not",
    "needn't've": "need not have",
    "o'clock": "of the clock",
    "oughtn't": "ought not",
    "oughtn't've": "ought not have",
    "shan't": "shall not",
    "sha'n't": "shall not",
    "shan't've": "shall not have",
    "she'd": "she would",
    "she'd've": "she would have",
    "she'll": "she will",
    "she'll've": "she will have",
    "she's": "she is",
    "should've": "should have",
    "shouldn't": "should not",
    "shouldn't've": "should not have",
    "so've": "so have",
    "so's": "so as",
    "that'd": "that would",
    "that'd've": "that would have",
    "that's": "that is",
    "there'd": "there would",
    "there'd've": "there would have",
    "there's": "there is",
    "they'd": "they would",
    "they'd've": "they would have",
    "they'll": "they will",
    "they'll've": "they will have",
    "they're": "they are",
    "they've": "they have",
    "to've": "to have",
    "wasn't": "was not",
    "we'd": "we would",
    "we'd've": "we would have",
    "we'll": "we will",
    "we'll've": "we will have",
    "we're": "we are",
    "we've": "we have",
    "weren't": "were not",
    "what'll": "what will",
    "what'll've": "what will have",
    "what're": "what are",
    "what's": "what is",
    "what've": "what have",
    "when's": "when is",
    "when've": "when have",
    "where'd": "where did",
    "where's": "where is",
    "where've": "where have",
    "who'll": "who will",
    "who'll've": "who will have",
    "who's": "who is",
    "who've": "who have",
    "why's": "why is",
    "why've": "why have",
    "will've": "will have",
    "won't": "will not",
    "won't've": "will not have",
    "would've": "would have",
    "wouldn't": "would not",
    "wouldn't've": "would not have",
    "y'all": "you all",
    "y'all'd": "you all would",
    "y'all'd've": "you all would have",
    "y'all're": "you all are",
    "y'all've": "you all have",
    "you'd": "you would",
    "you'd've": "you would have",
    "you'll": "you will",
    "you'll've": "you will have",
    "you're": "you are",
    "you've": "you have"
}

CONTRACTION_MAP_MULTIPLE = {
    "ain't he": "is he not", "ain't she": "is she not", "ain't it": "is it not",
    "aren't you": "are you not", "aren't they": "are they not",
    "can't he": "can he not", "can't she": "can she not", "can't it": "can it not",
    "can't you": "can you not", "can't they": "can they not",
    "couldn't he": "could he not", "couldn't she": "could she not", "couldn't it": "could it not",
    "couldn't you": "could you not", "couldn't they": "could they not",
    "doesn't he": "does he not", "doesn't she": "does she not", "doesn't it": "does it not",
    "don't you": "do you not", "don't they": "do they not",
    "didn't he": "did he not", "didn't she": "did she not", "didn't it": "did it not",
    "didn't you": "did you not", "didn't they": "did they not",
    "hasn't he": "has he not", "hasn't she": "has she not", "hasn't it": "has it not",
    "haven't you": "have you not", "haven't they": "haven they not",
    "hadn't he": "had he not", "hadn't she": "had she not", "hadn't it": "had it not",
    "hadn't you": "had you not", "hadn't they": "had they not",
    "isn't he": "is he not", "isn't she": "is she not", "isn't it": "is it not",
    "shouldn't he": "should he not", "shouldn't she": "should she not", "shouldn't it": "should it not",
    "shouldn't you": "should you not", "shouldn't they": "should they not",
    "wasn't he": "was he not", "wasn't she": "was she not", "wasn't it": "was it not",
    "weren't you": "were you not", "weren't they": "were they not",
    "won't he": "will he not", "won't she": "will she not", "won't it": "will it not",
    "won't you": "will you not", "won't they": "will they not",
    "wouldn't he": "would he not", "wouldn't she": "would she not", "wouldn't it": "would it not",
    "wouldn't you": "would you not", "wouldn't they": "would they not",
}

class Contractions:
    def __init__(self):
        self.contraction_mapping = CONTRACTION_MAP
        self.contraction_mapping_multiple = CONTRACTION_MAP_MULTIPLE

    def expand_contractions(self, text):
        # '|' : 'or' metacharacter in regex
        # create a regex set of all contraction keys
        contractions_pattern = re.compile('({})'.format('|'.join(self.contraction_mapping.keys())),
                                          flags=re.IGNORECASE|re.DOTALL)
        contractions_pattern_multiple = re.compile('({})'.format('|'.join(self.contraction_mapping_multiple.keys())),
                                          flags=re.IGNORECASE | re.DOTALL)

        # Perform for contraction single
        def expand_match(contraction):
            match = contraction.group(0)
            first_char = match[0]
            expanded_contraction = self.contraction_mapping.get(match)\
                                    if self.contraction_mapping.get(match)\
                                    else self.contraction_mapping.get(match.lower())
            expanded_contraction = first_char+expanded_contraction[1:]
            return expanded_contraction

        # Perform for contraction_mulitple:
        def expand_match_multiple(contraction):
            match = contraction.group(0)
            first_char = match[0]
            expanded_contraction = self.contraction_mapping_multiple.get(match) \
                                    if self.contraction_mapping_multiple.get(match) \
                                    else self.contraction_mapping_multiple.get(match.lower())
            expanded_contraction = first_char + expanded_contraction[1:]
            return expanded_contraction

        # First perform expansion for multiples
        expanded_text = contractions_pattern_multiple.sub(expand_match_multiple, text)

        # Then use result to perform for the singles
        expanded_text = contractions_pattern.sub(expand_match, expanded_text)
        # expanded_text = re.sub("'", "", expanded_text)
        return expanded_text



if __name__ == '__main__':
    con = Contractions()
    text = "I didn't really like it either. I mean...when are two new yorkers going to even go to Alabama?"
    exp = con.expand_contractions(text)
    print(exp)

