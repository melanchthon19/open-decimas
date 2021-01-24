#!/usr/bin/env python3

import spacy
import statistics
import math
import pandas as pd
import pickle

# spanish billion word corpus and embeddings
# https://github.com/crscardellino/sbwce

class Vocabulary():
    def __init__(self, file):
        self.nlp = spacy.load("es_core_news_sm")

        self.vocabulary = {}
        self.word_POS = {}
        self.sentence_POS = {}
        self.POS2word = {}
        self.read_file(file)
        self.mean_POS_length = self.get_mean_POS_length()

    def read_file(self, file):
        with open(file_txt, 'r') as file:
            for i, line in enumerate(file):
                # creating vocabulary
                self.get_vocabulary(line)

                # creating POS
                sentence = self.nlp(line.lower().strip())
                self.get_word_POS(sentence)

                # creating sentence POS
                self.get_sentence_POS(i, sentence)

                # creating POS2word
                self.get_POS2word(sentence)

    def get_vocabulary(self, line):
        for word in line.split():
            word = word.lower()
            try:
                self.vocabulary[word] += 1
            except KeyError:
                self.vocabulary[word] = 1

    def get_word_POS(self, sentence):
        for word in sentence:
            try:
                self.word_POS[(word.text, word.pos_)] += 1
            except KeyError:
                self.word_POS[(word.text, word.pos_)] = 1

    def get_sentence_POS(self, i, sentence):
        current_sentence_POS = []
        for word in sentence:
            current_sentence_POS.append(word.pos_)
        self.sentence_POS[i] = (sentence, current_sentence_POS)

    def get_POS2word(self, sentence):
        for word in sentence:
            try:
                self.POS2word[word.pos_].add(word.text)
            except KeyError:
                self.POS2word[word.pos_] = {word.text}

    def get_mean_POS_length(self):
        lengths = [len(self.sentence_POS[i][1]) for i in range(len(self.sentence_POS))]
        #print(sum(lengths)/len(lengths))
        m = statistics.mean(lengths)
        #print(m)  # 5.21...
        m = math.ceil(m)  # rounding up

        return m


#file_txt = 'sbwce.clean.small.txt'
file_txt = 'decimas_data_small.txt'

vocabulary = Vocabulary(file_txt)

#vocabulary.vocabulary = dict(sorted(vocabulary.vocabulary.items(), key=lambda x: x[1], reverse=True))
#word_POS = dict(sorted(vocabulary.word_POS.items(), key=lambda x: x[0][0], reverse=True))
#print(vocabulary.POS2word)


# POS tag frequencies
raw_count = pd.DataFrame(0, columns=range(int(vocabulary.mean_POS_length)), index=vocabulary.POS2word)
postag_freq = pd.DataFrame(0, columns=range(int(vocabulary.mean_POS_length)), index=vocabulary.POS2word)
position_freq = pd.DataFrame(0, columns=range(int(vocabulary.mean_POS_length)), index=vocabulary.POS2word)

for sentence in vocabulary.sentence_POS:
    seq = vocabulary.sentence_POS[sentence][1]
    for position in range(len(seq)):
        POS = seq[position]
        try:
            raw_count.loc[POS, position] += 1
        except KeyError:
            break
print('raw count\n', raw_count)

for index, row in raw_count.iterrows():
    total = sum(raw_count.loc[index])
    for col in range(len(row)):
        count = raw_count.loc[index, col]
        postag_freq.loc[index, col] = count / total * 100  # percentage
    row_sum = round(postag_freq.loc[index].sum())
    if row_sum != 100.0:
        raise ValueError(f'row {index} sums up to {row_sum}. it should be 100.0')
print('POS tag\n', postag_freq)

for col_name, column in raw_count.iteritems():
    total = sum(column)
    for row in range(len(column)):
        count = raw_count.iloc[row, col_name]
        position_freq.iloc[row, col_name] = count / total * 100
    col_sum = round(position_freq[col_name].sum())
    if col_sum != 100.0:
        raise ValueError(f'row {index} sums up to {col_sum}. it should be 100.0')
print('position\n', position_freq)

# uncomment these lines to save files
"""
raw_count.to_json('raw_count.json')
postag_freq.to_json('postag_freq.json')
position_freq.to_json('position_freq.json')

picklefile = open('vocabulary.pk', 'wb')
pickle.dump(vocabulary, picklefile)
picklefile.close()
"""
