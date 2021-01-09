#!/usr/bin/env python3
# http://www.rimar2000.com.ar/

import pandas as pd
import re

vowels = ['a', 'á', 'e', 'é', 'i', 'í', 'o', 'ó', 'u', 'ú', 'ü']
vowels_dict = {1:'a', 2: 'e', 3: 'i', 4:'o', 5:'u',
           6:'á', 7: 'é', 8:'í', 9:'ó', 10:'ú',
           11:'ü'}
vowels_strongh = [1, 2, 4, 6, 7, 8, 9, 10]

consonants = ['m', 'n', 'ñ',
               'p', 't', 'k', 'b', 'd', 'g',
               'C',
               'f', 's', 'L', 'x',
               'l', 'r', 'R']

char2phone = {
       1:{
       'ci': 'si',
       'cí': 'sí',
       'ce': 'se',
       'cé': 'sé',
       'ch': 'C',
       'qu': 'k'},
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
        for rule in self.char2phone.keys():  # certain rules are applied first than others
            for char in self.char2phone[rule]:
                if char in phonemes:
                    # modifying the word on the fly
                    phonemes = re.sub(char, self.char2phone[rule][char], phonemes)

        return phonemes

    def phonemes2structure(self, phonemes):
        structure = ''
        for phone in phonemes:
            if phone in consonants:
                structure += 'C'
            if phone in vowels:
                structure += 'V'

        return structure

    def syllables_per_word(self, structure):
        structure = list(structure)
        for i in range(len(structure) - 1):
            try:
                if structure[i] == structure[i+1]:
                    structure.pop(i)
            except IndexError:
                break
        structure = ''.join(structure)
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
                if i == len
                phonemes = self.word2phonemes(word)
                sentence_phonemes.append(phonemes)

                structure = self.phonemes2structure(phonemes)
                sentence_structure.append(structure)

                number_syllables = self.syllables_per_word(structure)
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
phonetizer1.print_structure(3)

phonetizer2 = Phonetizer(vowels, consonants, char2phone)
phonetizer2.read_txt('decima1.txt')
phonetizer2.text2structure()
phonetizer2.print_structure(3)
