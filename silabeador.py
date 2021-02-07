#!/usr/bin/env python3
# http://www.rimar2000.com.ar/

import pandas as pd
import re
#import regex
import sys
import phonetics
import preprocess

# TODO:
# apply: 1) sinalefa, 2) diéresis, 3) sinéresis
# sinéresis: dos vocales que no forman diptongo, forman diptongo. (e.g. gor-je-ar --> gor-jear)
# diéresis: se separan dos vocales que forman diptongo. (e.g. sua-ve --> su-a-ve)
# sinalefa: dos vocales de palabras contiguas se diptonguean. (e.g. cie-lo-y-mar --> cie-loy-mar)

class Silabeador():
    def __init__(self, verbose=1, **ph):
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
        self.punctuation = ph['punctuation']
        self.double_consonants = ph['double_consonants']

        # variables used within each count_syllables call
        self.sentence = []
        self.phonemes = []
        self.structure = []
        self.structure_syllables = []
        self.word_syllables = []
        self.number_syllables = 0
        self.last_word = {'word': None,\
                          'phonemes': None,\
                          'structure': None,\
                          'word_syllables': None,\
                          'monosilabo': None,\
                          'accent': None,\
                          'rithm': None}

        self.sinalefa = False  # bools to activate (True) sinalefa

    def count_syllables_text(self, text):
        syllables_text = []
        for line in text:
            syllables_text.append(self.count_syllables_sentence(line))

    def count_syllables_sentence(self, sentence):
        '''
        function that takes a sentence and counts the number of metric syllables
        input: string
        output: number of syllables
        '''
        self.sentence = sentence.split()

        self.phonemes = [self.word2phonemes(word) for word in self.sentence]
        self.structure = [self.phonemes2structure(word) for word in self.phonemes]

        self.structure_syllables = [self.divide_structure_syllables(word) for word in self.structure]
        self.word_syllables = [self.add_separator(structure, word) for structure, word in zip(self.structure_syllables, self.phonemes)]
        self.last_word = self.get_last_word()  # metric rules are considered when counting syllables in a sentence

        if self.sinalefa:
            self.word_syllables = self.apply_sinalefa()

        self.number_syllables = self.count(self.word_syllables, self.metric_rule(self.last_word))

        if self.verbose == 1:
            print(sentence, self.word_syllables, self.number_syllables)

        elif self.verbose == 2:# and self.number_syllables != 8:  # add second condition for debugging purposes
            print('sentence', self.sentence)
            print('phonemes', self.phonemes)
            print('structure', self.structure)
            print('structure syllables', self.structure_syllables)
            print('word syllables', self.word_syllables)
            print('last word:', self.last_word['word'])
            print('last word structure', self.last_word['structure'])
            print('last word phonemes', self.last_word['phonemes'])
            print('last word syllables', self.last_word['word_syllables'])
            print('last word accent:', self.last_word['accent'])
            print('is last word monosilabo:', self.last_word['monosilabo'])
            print('number of metric syllables', self.number_syllables)

        return self.number_syllables  # amount of syllables in the sentence

    def apply_sinalefa(self):
        # applying hard sinalefa
        all_syllables = self.get_all_syllables()
        index = 0
        traversed = False
        while not traversed:
            try:
                if self.is_sinalefa(all_syllables[index][-1], all_syllables[index + 1][0]):
                    all_syllables[index] = self.merge_words(all_syllables, index, index+1)
                    all_syllables.pop(index+1)
                else:
                    index += 1
                    if index == len(all_syllables):
                        traversed = True
            except IndexError:
                break

        return '-'.join(all_syllables)

    def merge_words(self, all_syllables, index1, index2):
        merged = all_syllables[index1] + all_syllables[index2]
        return merged

    def get_all_syllables(self):
        all_syllables = []
        for word in self.word_syllables:
            if len(word.split('-')) > 1:
                all_syllables.extend(word.split('-'))
            else:
                all_syllables.append(word)

        return all_syllables

    def is_sinalefa(self, c1, c2):
        pattern = re.compile(f"[{''.join(self.vowels)}]")
        if re.match(pattern, c1) and re.match(pattern, c2):
            return True
        else:
            return False

    def word2phonemes(self, word):
        # findall retrieves a list of characters only
        phonemes = ''.join(re.findall('[^\W]*', word))  # TODO: deal with punctuation in the middle of sentence
        for rule in self.char2phone.keys():  # certain rules must be applied first
            for char in self.char2phone[rule]:
                if char in phonemes:
                    # modifying the word on the fly
                    phonemes = re.sub(char, self.char2phone[rule][char], phonemes)
        return phonemes

    def phonemes2structure(self, phonemes):
        phonemes_reduced = self.reduce_double_syllables(phonemes)
        structure = [self.phonemes_dict[phone] if phone in self.alphabet else phone for phone in phonemes_reduced]
        return structure

    def divide_structure_syllables(self, word):
        sequence = ''.join(word)
        pattern = re.compile(r"""(CDDC(?![FAD]))?
                                 (CDAC(?![FAD]))?
                                 (CDD)?
                                 (CDFC(?![AFD]))?
                                 (CDF)?
                                 (CDC(?![AFD]))?
                                 (DFC)?
                                 (CCF)?
                                 (TFC(?![AFD]))?
                                 (CFT(?![AFD]))?
                                 (CFC(?![AFD]))?
                                 (TDF)?
                                 (CF)?
                                 (DF)?
                                 (TF)?
                                 (TD)?
                                 (TAC)?
                                 (TA)?
                                 (FC(?![FAD]))?
                                 (CD(?![AFD]))?
                                 (DC(?=[CT]))?
                                 (CA)?
                                 (F(?=C[FAD])?)?
                                 (A)?
                                 (D)?""", re.VERBOSE)
        match = re.findall(pattern, sequence)
        structure_syllables = '-'.join([syllable for group in match for syllable in group if syllable])

        return structure_syllables

    def reduce_double_syllables(self, word):
        word = [char for char in word]
        for char in range(len(word)):
            if ''.join(word[char:char+2]) in self.double_consonants:
                word[char] = 'T'
                word.pop(char+1)

        return ''.join(word)

    def add_separator(self, structure, word):
        word_segmented = list(word)
        char = 0
        forward = 0

        while char < len(word_segmented) - 1:
            if structure[char] == '-':
                word_segmented.insert(char + forward, '-')
            elif structure[char] == 'T':
                forward += 1  # moving one forward because T is mapped to two characters
            char += 1

        return ''.join(word_segmented)


    def metric_rule(self, last_word):
        '''
        applies metric rule:
        +1 if last word is aguda
        +0 if last word is grave
        -1 if last word is esdrujula
        input: self (uses information from dictionary last_word)
        output: int [+1, 0, -1]
        '''

        monosilabo = self.is_monosilabo(last_word['word_syllables'])
        accent = self.acentuacion(last_word['phonemes'], last_word['structure'], monosilabo)

        self.last_word['monosilabo'] = monosilabo
        self.last_word['accent'] = accent

        if monosilabo:
            return +1
        if accent == 'aguda':
            return +1
        elif accent == 'grave':
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

    def is_monosilabo(self, word_syllables):
        '''
        checks if structure is a monosilabo.
        input: structure of a word
        output: boolean
        '''
        if len(word_syllables.split('-')) > 1:
            return False
        else:
            return True

    def get_last_word(self):
        last_word = {'word':self.sentence[-1],\
                     'phonemes': self.phonemes[-1],\
                     'structure': self.structure[-1],\
                     'word_syllables': self.word_syllables[-1]}

        return last_word

    def count(self, word_syllables, last_word_count):
        number_syllables = len(word_syllables.split('-'))
        total_syllables = number_syllables + last_word_count

        return total_syllables

if __name__ == '__main__':

    # ph is a dictionary with information regarding vowels, alphabet, char2phone rules, etc.
    ph = phonetics.phonetics
    text = preprocess.read_txt('data/decima2.txt')

    silabeador = Silabeador(**ph)
    silabeador.sinalefa = True  # counting using sinalefa
    silabeador.count_syllables_sentence(text[1])
    silabeador.count_syllables_text(text)

    #def merge_words(self, sentence):
    #    sentence_merged = re.sub(r' ', '', sentence)  # removing white spaces
    #    punctuation_pattern = re.compile(f"[{''.join(self.punctuation)}]")
    #    merged_words = re.split(punctuation_pattern, sentence_merged)

    #    return merged_words
