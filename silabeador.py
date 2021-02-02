#!/usr/bin/env python3
# http://www.rimar2000.com.ar/

import pandas as pd
import re
import sys
import phonetics

# sinéresis: dos vocales que no forman diptongo, forman diptongo. (e.g. gor-je-ar --> gor-jear)
# diéresis: se separan dos vocales que forman diptongo. (e.g. sua-ve --> su-a-ve)
# sinalefa: dos vocales de palabras contiguas se diptonguean. (e.g. cie-lo-y-mar --> cie-loy-mar)
# reglas de acentuación:
#   1) verso terminada en palabra aguda --> +1
#   2) verso terminada en palabra grave --> +0
#   3) verso terminada en palabra esdrújula --> -1


class Silabeador():
    def __init__(self, verbose=False, **ph):
        '''
        Silabeador class takes a sentence as input
        and gets its number of metric syllables.
        along with other relevant information throughout the process.
        '''
        self.verbose = verbose  # to print out the result of each function.
        # relevant phonetics information used to separate the sentence into metric syllables.
        self.vowels = ph['vowels']
        self.consonants = ph['consonants']
        self.alphabet = ph['alphabet']
        self.phonemes_dict = ph['phonemes_dict']
        self.char2phone = ph['char2phone']  # hierarchical rules to chage characters to phones
        # variables used within the class
        self.text_raw = []
        self.text_phoneme = []
        self.text_structure = []
        self.text_syllables = []

    def count_syllables(self, sentence):
        '''
        function that takes a sentence and count the number of metric syllables
        input: string
        output: number of syllables (TODO: add string divided by each syllable)
        '''
        phonemes = self.word2phonemes(word)
        structure = self.phonemes2structure(phonemes)
        last_word = (phonemes[-1], structure[-1])
        syllables = self.count(structure[:]) + self.metric_rule(last_word)

        return syllables  # amount of syllables in the sentence

    def count(self, structure):
        # TODO: re-think in a more robust way

        structure = ''.join([s for word_structure in structure for s in word_structure])
        structure = re.sub(r'([FD]{3})', r'\1C\1', structure)  # adding extra consonant
        vowels = re.split('C', structure)

        number_syllables = len([v for v in vowels if v])

        return number_syllables

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
        structure = [self.phonemes_dict[phone] for phone in phonemes if phone in self.alphabet]

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

    def text2structure(self):
        # not being used --> being segmented and refactored
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
            if phonemes[-1] in (self.vowels + ['n','s']):
                return 'grave'
            else:
                return 'aguda'

    def monosilabo(self, structure):
        '''
        checks if structure is a monosilabo.
        input: structure of a word
        output: boolean
        '''
        rough_count_syllables = ''.join(structure).split('C')
        rough_count_syllables = [c for c in rough_count_syllables if c]
        if len(rough_count_syllables) == 1:
            return True
        else:
            return False

    def metric_rule(self, last_word):
        '''
        applies metric rule:
        +1 if last word is aguda
        +0 if last word is grave
        -1 if last word is esdrujula
        input: last word as a tuple of its phonemes and structure
        output: int [+1, 0, -1]
        '''
        phonemes, structure = last_word
        accent = self.acentuacion(phonemes, structure)

        if self.monosilabo(structure):
            return +1

        if accent == 'aguda':
            return +1
        elif accent == 'grave':
            return 0
        else:  # accent == 'esdrujula':
            return -1


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

    def check_eight_syllables(self, verso):
        # TODO: refactor this code
        sentence_phonemes = []
        sentence_structure = []
        for word in verso:
            phonemes = self.word2phonemes(word)
            sentence_phonemes.append(phonemes)
            structure = self.phonemes2structure(phonemes)
            sentence_structure.append(structure)
        number_syllables = self.syllables_per_sentence(sentence_structure[:])  # passing a copy of the list
        last_word = (sentence_phonemes[-1], sentence_structure[-1])
        total_number = number_syllables + self.metric_rule(last_word)
        print(total_number)
        if total_number == 8:
            return 'match'
        elif total_number > 8:
            return 'greater'
        else:
            return 'fewer'


if __name__ == '__main__':

    # ph is a dictionary with information regarding vowels, alphabet, char2phone rules, etc.
    ph = phonetics.phonetics
    text = preprocess.read_txt('decima2.txt'))

    silabeador = Silabeador(**ph)
    silabeador.count_syllables(text[0])
    #silabeador.text2structure()
    silabeador.print_structure(-1)
