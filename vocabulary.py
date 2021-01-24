#!/usr/bin/env python3

import spacy

# spanish billion word corpus and embeddings
# https://github.com/crscardellino/sbwce

class Vocabulary():
    def __init__(file):
        self.vocabulary = {}
        self.word_POS = {}
        self.sentence_POS = {}
        self.POS2word = {}
        self.read_file(file)

    def get_vocabulary(line):
        for word in line.split():
            word = word.lower()
            try:
                self.vocabulary[word] += 1
            except KeyError:
                self.vocabulary[word] = 1

    def get_word_POS(sentence):
        for word in sentence:
            try:
                self.word_POS[(word.text, word.pos_)] += 1
            except KeyError:
                self.word_POS[(word.text, word.pos_)] = 1

    def get_sentence_POS(i, sentence):
        current_sentence_POS = []
        for word in sentence:
            current_sentence_POS.append(word.pos_)
        self.sentence_POS[i] = (sentence, current_sentence_POS)

    def get_POS2word(sentence):
        for word in sentence:
            try:
                self.POS2word[word.pos_].add(word.text)
            except KeyError:
                self.POS2word[word.pos_] = {word.text}

    def read_file(file):
        with open(file_txt, 'r') as file:
            for i, line in enumerate(file):
                # creating vocabulary
                self.get_vocabulary(line)

                # creating POS
                sentence = nlp(line.lower())
                self.get_word_POS(sentence)

                # creating sentence POS
                self.get_sentence_POS(i, sentence)

                # creating POS2word
                self.get_POS2word(sentence)

#file_txt = 'sbwce.clean.small.txt'
file_txt = 'decimas_data_small.txt'

# some word statistics

nlp = spacy.load("es_core_news_sm")



vocabulary = dict(sorted(vocabulary.items(), key=lambda x: x[1], reverse=True))
#print(vocabulary)
#print(len(vocabulary))
word_POS = dict(sorted(word_POS.items(), key=lambda x: x[0][0], reverse=True))
#print(POS)
#print(len(word_POS))
#print(word_POS)
#print(sentence_POS)
print(type(POS2word))
for word in POS2word['NUM']:
    print(type(word))
    print(word)
print(POS2word)
