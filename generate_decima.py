#!/usr/bin/env python3

import spacy
import pickle
import json
import pandas as pd
from vocabulary import Vocabulary
import fonetizador
import random


#create pos chain of most likely sequence.
#according to chain, pick up a word for each pos.
vocabulary = pickle.load(open('vocabulary.pk', 'rb'))
print(vocabulary)

position_freq = pd.read_json('position_freq.json')
postag_freq = pd.read_json('postag_freq.json')
print(postag_freq)

postags = random.choices(population=list(vocabulary.POS2word.keys()),\
                     weights=position_freq[0],\
                     k=vocabulary.mean_POS_length)

def change_last_word(verso, pos):
    print(verso)
    while phonetizer.check_eight_syllables(' '.join(verso)) != 'match':
        verso[-1] = random.choices(population=list(vocabulary.POS2word[pos]), k=1)
    #print(verso)
phonetizer = fonetizador.Phonetizer(fonetizador.vowels, fonetizador.consonants, fonetizador.char2phone)
print(phonetizer)
verso = []
eight_syllables = False
#while not eight_syllables:
for pos in range(len(postags)):
    verso.extend(random.choices(population=list(vocabulary.POS2word[postags[pos]]), k=1))
    print(' '.join(verso))
    phonetizer.count_again()
    phonetizer.text_raw = [' '.join(verso)]
    print(phonetizer.text_raw)
    phonetizer.text2structure()
    print(phonetizer.text_syllables)
        #number_syllables = phonetizer.check_eight_syllables(' '.join(verso))
        #print(number_syllables)
        #if number_syllables == 'match':
    #        eight_syllables = True
        #elif number_syllables == 'greater':
        #    change_last_word(verso, postags[pos])
        #else:
        #    continue

print(list(zip(postags, verso)))
