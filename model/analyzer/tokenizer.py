import nltk
import re


class Tokenizable():
    def __init__(self, stemmer):
        self.stemmer = stemmer
        self.totalvocab_stemmed = list()
        self.totalvocab_tokenized = list()

    def tokenize_and_stem(self, text):
        tokens = [word for sent in nltk.sent_tokenize(text)
                  for word in nltk.word_tokenize(sent)]
        filtered_tokens = []
        for token in tokens:
            if re.search('[a-zA-Z]', token):
                filtered_tokens.append(token)
        stems = [self.stemmer.stem(t) for t in filtered_tokens]
        return stems

    @staticmethod
    def tokenize_only(text):
        tokens = [word.lower() for sent in nltk.sent_tokenize(text)
                  for word in nltk.word_tokenize(sent)]
        filtered_tokens = []
        for token in tokens:
            if re.search('[a-zA-Z]', token):
                filtered_tokens.append(token)
        return filtered_tokens
