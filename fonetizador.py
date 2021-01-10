#!/usr/bin/env python3
# http://www.rimar2000.com.ar/

import pandas as pd
import re
import sys

vowels_strong = {'a':'F', 'á':'F', 'e':'F', 'é':'F', 'í':'F', 'o':'F', 'ó':'F', 'ú':'F'}
vowels_weak = {'i':'D', 'u':'D', 'ü':'D'}
consonants = {'m':'C', 'n':'C', 'ñ':'C',
              'p':'C', 't':'C', 'k':'C', 'b':'C', 'd':'C', 'g':'C',
              'C':'C',
              'f':'C', 's':'C', 'L':'C', 'x':'C',
              'l':'C', 'r':'C', 'R':'C'}
vowels = list(vowels_strong.keys()) + list(vowels_weak.keys())
alphabet = list(vowels_strong.keys()) + list(vowels_weak.keys()) + list(consonants.keys())
phonemes_dict = {**vowels_strong, **vowels_weak, **consonants}

char2phone = {
       1:{
       'ci': 'si',
       'cí': 'sí',
       'ce': 'se',
       'cé': 'sé',
       'ch': 'C',
       'qu': 'k',
       'gui': 'gi',
       'gue': 'ge'},
       2:{
       'c': 'k',
       'll': 'L',
       'rr': 'R',
       'j': 'x',
       'h': '',
       'z': 's',
       'v': 'b',
       'y': 'i'}
       }

# sinéresis: dos vocales que no forman diptongo, forman diptongo. (e.g. gor-je-ar --> gor-jear)
# diéresis: se separan dos vocales que forman diptongo. (e.g. sua-ve --> su-a-ve)
# sinalefa: dos vocales de palabras contiguas se diptonguean. (e.g. es-ta-ba-e-cha-do --> es-ta-bae-cha-do)
# reglas de acentuación:
#   1) verso terminada en palabra aguda --> +1
#   2) verso terminada en palabra grave --> +0
#   3) verso terminada en palabra esdrújula --> -1

class Phonetizer():
    def __init__(self, vowels, consonants, char2phone):
        self.vowels = vowels
        self.consonants = consonants
        self.char2phone = char2phone  # hierarchical rules to chage characters to phones
        self.text_raw = []
        self.text_phoneme = []
        self.text_structure = []
        self.text_syllables = []

    def word2phonemes(self, word):
        phonemes = word.lower()
        for rule in self.char2phone.keys():  # certain rules must be applied first
            for char in self.char2phone[rule]:
                if char in phonemes:
                    # modifying the word on the fly
                    phonemes = re.sub(char, self.char2phone[rule][char], phonemes)

        return phonemes

    def phonemes2structure(self, phonemes):
        structure = [phonemes_dict[phone] for phone in phonemes if phone in alphabet]
        print(phonemes, structure)
        return structure

    def syllables_per_word(self, structure):
        # a copy of structure is being passed
        for i in range(len(structure) - 1):
            try:
                if structure[i] == structure[i+1]:
                    structure.pop(i)
            except IndexError:
                # add catch block to handle out-of-language words
                break
        structure = ''.join(structure)
        print(structure)
        number_syllables = structure.count('V')

        return number_syllables

    def text2structure(self):
        if self.text_raw == None:
            raise AttributeError('pass a txt file to read first')
        for sentence in range(len(self.text_raw)):
            sentence_structure = []
            sentence_phonemes = []
            sentence_syllables = []

            for i, word in enumerate(self.text_raw[sentence]):
                phonemes = self.word2phonemes(word)
                sentence_phonemes.append(phonemes)

                structure = self.phonemes2structure(phonemes)
                sentence_structure.append(structure)

                number_syllables = self.syllables_per_word(structure[:])
                sentence_syllables.append(number_syllables)

            self.text_phoneme.append(sentence_phonemes)
            self.text_structure.append(sentence_structure)
            self.text_syllables.append(sentence_syllables)

        return

    def read_txt(self, file):
        with open(file, 'r') as f:
            text = f.readlines()
        # add further preprocessing to get rid of empty lines
        self.text_raw = [line.strip().split() for line in text]

        return

    def print_structure(self, n):
        for i in range(n):
            try:
                print(list(zip(self.text_raw[i], \
                               self.text_phoneme[i], \
                               self.text_structure[i], \
                               self.text_syllables[i])), \
                               sum([number for number in self.text_syllables[i]]))
            except IndexError:
                print(f'given index greater than number of lines in the text:\
                number of lines: {len(self.text_structure)} -- index: {n}')

        return


phonetizer1 = Phonetizer(vowels, consonants, char2phone)
phonetizer1.read_txt('cuento1.txt')
phonetizer1.text2structure()
#phonetizer1.print_structure(3)

phonetizer2 = Phonetizer(vowels, consonants, char2phone)
phonetizer2.read_txt('decima1.txt')
phonetizer2.text2structure()
#phonetizer2.print_structure(3)
