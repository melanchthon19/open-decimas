#!/usr/bin/env python3
# http://www.rimar2000.com.ar/

import pandas as pd
import re
import sys

vowels_strong = {'a':'F', 'e':'F', 'o':'F',}
vowels_weak = {'i':'D', 'u':'D', 'ü':'D'}
vowels_accented = {'á':'A', 'é':'A', 'í':'A', 'ó':'A', 'ú':'A'}
consonants = {'m':'C', 'n':'C', 'ñ':'C',
              'p':'C', 't':'C', 'k':'C', 'b':'C', 'd':'C', 'g':'C',
              'C':'C',
              'f':'C', 's':'C', 'L':'C', 'x':'C',
              'l':'C', 'r':'C', 'R':'C'}

vowels = list(vowels_strong.keys()) + list(vowels_weak.keys()) + list(vowels_accented.keys())
alphabet = vowels + list(consonants.keys())
phonemes_dict = {**vowels_strong, **vowels_weak, **vowels_accented, **consonants}

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
# sinalefa: dos vocales de palabras contiguas se diptonguean. (e.g. cie-lo-y-mar --> cie-loy-mar)
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
        # findall retrieves a list of characters only
        phonemes = ''.join(re.findall('[^\W]*', word.lower()))

        for rule in self.char2phone.keys():  # certain rules must be applied first
            for char in self.char2phone[rule]:
                if char in phonemes:
                    # modifying the word on the fly
                    phonemes = re.sub(char, self.char2phone[rule][char], phonemes)

        return phonemes

    def phonemes2structure(self, phonemes):
        structure = [phonemes_dict[phone] for phone in phonemes if phone in alphabet]

        return structure

    def syllables_per_word(self, structure):
        # not being used anymore
        # a copy of structure is being passed
        for i in range(len(structure) - 1):
            try:
                if structure[i] == structure[i+1]:
                    structure.pop(i)
            except IndexError:
                # add catch block to handle out-of-language words
                break
        structure = ''.join(structure)
        number_syllables = structure.count('V')

        return number_syllables

    def syllables_per_sentence(self, sentence_structure):
        sentence_structure = ''.join([s for word_structure in sentence_structure for s in word_structure])
        sentence_structure = re.sub(r'([FD]{3})', r'\1C\1', sentence_structure)  # adding extra consonant
        vowels = re.split('C', sentence_structure)

        number_syllables = len([v for v in vowels if v])

        return number_syllables

    def text2structure(self):
        if self.text_raw == None:
            raise AttributeError('pass a txt file to read first')

        for sentence in range(len(self.text_raw)):
            if self.text_raw[sentence] == []:
                continue

            sentence_phonemes = []
            sentence_structure = []
            sentence_syllables = []

            for i, word in enumerate(self.text_raw[sentence]):
                phonemes = self.word2phonemes(word)
                sentence_phonemes.append(phonemes)

                structure = self.phonemes2structure(phonemes)
                sentence_structure.append(structure)

            number_syllables = self.syllables_per_sentence(sentence_structure[:])  # passing a copy of the list
            last_word = (sentence_phonemes[-1], sentence_structure[-1])

            sentence_syllables.append(number_syllables + self.metric_rule(last_word))

            self.text_phoneme.append(sentence_phonemes)
            self.text_structure.append(sentence_structure)
            self.text_syllables.append(sentence_syllables)

        return

    def acentuacion(self, phonemes, structure):
        # add if monosílabo

        if 'A' in structure:
            pos = structure.index('A')
            if (structure[-1] == 'A') or (structure[-2] == 'A' and phonemes[-1] in ['n','s']):
                return 'aguda'
            elif structure[pos:].count('D') + structure[pos:].count('F') >= 2:
                return 'esdrujula'
            else:
                return 'grave'

        else:
            if phonemes[-1] in (vowels + ['n','s']):
                return 'grave'
            else:
                return 'aguda'

    def monosilabo(self, structure):
        rough_count_syllables = ''.join(structure).split('C')
        rough_count_syllables = [c for c in rough_count_syllables if c]
        if len(rough_count_syllables) == 1:
            return True

    def metric_rule(self, last_word):
        phonemes, structure = last_word
        #print(last_word)
        accent = self.acentuacion(phonemes, structure)

        if self.monosilabo(structure):
            return +1

        if accent == 'aguda':
            return +1
        elif accent == 'grave':
            return 0
        else:  # accent == 'esdrujula':
            return -1

    def read_txt(self, file):
        with open(file, 'r') as f:
            text = f.readlines()
        # add further pre-processing to get rid of empty lines and non-alphabetic characters.
        self.text_raw = [line.lower().strip().split() for line in text]

        return

    def print_structure(self, n):
        if n == -1:
            n = len(self.text_structure) - 1
        for i in range(n):
            try:
                print(' '.join(self.text_phoneme[i]), self.text_syllables[i])

            except IndexError:
                print(f'given index greater than number of lines in the text:\n\
                number of lines: {len(self.text_structure)} -- index: {n}')

        return


#phonetizer1 = Phonetizer(vowels, consonants, char2phone)
#phonetizer1.read_txt('cuento1.txt')
#phonetizer1.text2structure()
#phonetizer1.print_structure(3)

phonetizer2 = Phonetizer(vowels, consonants, char2phone)
phonetizer2.read_txt('decima1.txt')
phonetizer2.text2structure()

phonetizer3 = Phonetizer(vowels, consonants, char2phone)
phonetizer3.read_txt('decima2.txt')
phonetizer3.text2structure()
phonetizer3.print_structure(-1)
