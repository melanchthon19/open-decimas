#!/usr/bin/env python3
# http://www.rimar2000.com.ar/

import pandas as pd
import re
import sys
import phonetics
import preprocess

# sinéresis: dos vocales que no forman diptongo, forman diptongo. (e.g. gor-je-ar --> gor-jear)
# diéresis: se separan dos vocales que forman diptongo. (e.g. sua-ve --> su-a-ve)
# sinalefa: dos vocales de palabras contiguas se diptonguean. (e.g. cie-lo-y-mar --> cie-loy-mar)
# reglas de acentuación:
#   1) verso terminada en palabra aguda --> +1
#   2) verso terminada en palabra grave --> +0
#   3) verso terminada en palabra esdrújula --> -1


class Silabeador():
    def __init__(self, verbose=True, **ph):
        '''
        Silabeador class takes a sentence as input
        and gets its number of metric syllables.
        along with other relevant information throughout the process.
        Its main function is count_syllables()
        '''
        self.verbose = verbose  # to print out the result of each function.

        # relevant phonetics information used to separate the sentence into metric syllables.
        self.vowels = ph['vowels']
        self.consonants = ph['consonants']
        self.alphabet = ph['alphabet']
        self.phonemes_dict = ph['phonemes_dict']
        self.char2phone = ph['char2phone']  # hierarchical rules to chage characters to phones

        # variables used within the class
        self.sentence = []
        self.phonemes = []
        self.structure = []
        self.syllables = []
        self.last_word = {}

    def count_syllables_text(self, text):
        syllables_text = []
        for line in text:
            syllables_text.append(self.count_syllables(line))

    def count_syllables(self, sentence):
        '''
        function that takes a sentence and count the number of metric syllables
        input: string
        output: number of syllables (TODO: add string divided by each syllable)
        '''
        self.sentence = sentence
        self.phonemes = [self.word2phonemes(word) for word in self.sentence]
        self.structure = self.phonemes2structure(self.phonemes)
        self.get_last_word()
        self.syllables = self.count(self.structure[:]) + self.metric_rule()

        if self.verbose:
            print('sentence', self.sentence)
            print('phonemes', self.phonemes)
            print('structure', self.structure)
            print('number of metric syllables', self.syllables)
            print('last word:', self.last_word['word'])
            print('last word accent:', self.last_word['accent'])
            print('is last word monosilabo:', self.last_word['monosilabo'])

        return self.syllables  # amount of syllables in the sentence

    def sentence2phonemes(self, sentence):
        # findall retrieves a list of characters only
        phonemes = ''.join(re.findall('[^\W]*', self.sentence))

        for rule in self.char2phone.keys():  # certain rules must be applied first
            for char in self.char2phone[rule]:
                if char in phonemes:
                    # modifying the word on the fly
                    phonemes = re.sub(char, self.char2phone[rule][char], phonemes)

        return phonemes

    def word2phonemes(self, word):
        # findall retrieves a list of characters only

        phonemes = ''.join(re.findall('[^\W]*', word))

        for rule in self.char2phone.keys():  # certain rules must be applied first
            for char in self.char2phone[rule]:
                if char in phonemes:
                    # modifying the word on the fly
                    phonemes = re.sub(char, self.char2phone[rule][char], phonemes)

        return phonemes

    def phonemes2structure(self, phonemes):
        structure = []
        for word in phonemes:
            structure.append([self.phonemes_dict[phone] for phone in word if phone in self.alphabet])

        return structure

    def count(self, structure):
        # TODO: re-think in a more robust way

        structure = ''.join([s for word_structure in structure for s in word_structure])
        structure = re.sub(r'([FD]{3})', r'\1C\1', structure)  # adding extra consonant
        vowels = re.split('C', structure)

        number_syllables = len([v for v in vowels if v])

        return number_syllables

    def metric_rule(self):
        '''
        applies metric rule:
        +1 if last word is aguda
        +0 if last word is grave
        -1 if last word is esdrujula
        input: last word as a tuple of its phonemes and structure
        output: int [+1, 0, -1]
        '''
        self.last_word['monosilabo'] = self.is_monosilabo(self.last_word['structure'])
        self.last_word['accent'] = self.acentuacion(self.last_word['phonemes'],\
                                                    self.last_word['structure'],\
                                                    self.last_word['monosilabo'])

        if self.last_word['monosilabo']:
            return +1
        if self.last_word['accent'] == 'aguda':
            return +1
        elif self.last_word['accent'] == 'grave':
            return 0
        else:  # accent == 'esdrujula':
            return -1

    def acentuacion(self, phonemes, structure, monosilabo):
        '''
        checks if the word is aguda, grave or esdrujula.
        input: word as a tuple of its phonemes and structure.
        output: string ['aguda', 'grave', 'esdrujula']
        '''
        if 'A' in structure:
            pos = structure.index('A')
            if (structure[-1] == 'A') or (structure[-2] == 'A' and phonemes[-1] in ['n','s']):
                return 'aguda'
            elif structure[pos:].count('D') + structure[pos:].count('F') >= 2:
                return 'esdrujula'
            else:
                return 'grave'

        else:
            if monosilabo:
                return 'none'
            elif phonemes[-1] in (self.vowels + ['n','s']):
                return 'grave'
            else:
                return 'aguda'

    def is_monosilabo(self, structure):
        '''
        checks if structure is a monosilabo.
        input: structure of a word
        output: boolean
        '''
        print(structure)
        number_of_vowels = len([vowel for vowel in ''.join(structure).split('C') if vowel])
        print(number_of_vowels)
        if number_of_vowels == 1:
            return True
        else:
            return False

    def get_last_word(self):
        print(self.sentence[-1])
        self.last_word['word'] = self.sentence[-1]
        self.last_word['phonemes'] = self.phonemes[-1]
        self.last_word['structure'] = self.structure[-1]

if __name__ == '__main__':

    # ph is a dictionary with information regarding vowels, alphabet, char2phone rules, etc.
    ph = phonetics.phonetics
    text = preprocess.read_txt('data/decima2.txt')

    silabeador = Silabeador(**ph)
    silabeador.count_syllables(text[0])
    silabeador.count_syllables_text(text)
