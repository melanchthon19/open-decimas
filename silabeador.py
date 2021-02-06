#!/usr/bin/env python3
# http://www.rimar2000.com.ar/

import pandas as pd
import re
#import regex
import sys
import phonetics
import preprocess


class Silabeador():
    def __init__(self, verbose=False, **ph):
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
        self.syllables = []
        self.last_word = {'word': None,\
                          'phonemes': None,\
                          'structure': None,\
                          'monosilabo': None,\
                          'accent': None,\
                          'rithm': None}

    def count_syllables_text(self, text):
        syllables_text = []
        for line in text:
            syllables_text.append(self.count_syllables_sentence(line))

    def count_syllables_sentence(self, sentence):
        '''
        function that takes a sentence and counts the number of metric syllables
        input: string
        output: number of syllables (TODO: add string divided by each syllable)
        '''
        self.sentence = sentence.split()
        #print(self.sentence)
        self.phonemes = [self.word2phonemes(word) for word in self.sentence]
        print(self.phonemes)
        self.structure = [self.phonemes2structure(word) for word in self.phonemes]
        #print(self.structure)
        #self.get_last_word()  # metric rules are considered when counting syllables in a sentence
        #self.syllables = self.count_syllables(self.structure[:]) + self.metric_rule()
        self.syllables = [self.divide_word_syllables(word) for word in self.structure]
        print(self.syllables)

        if self.verbose:# and self.syllables != 8:  # add second condition for debugging purposes
            print('sentence', self.sentence)
            print('phonemes', self.phonemes)
            print('structure', self.structure)
            print('number of metric syllables', self.syllables)
            print('last word:', self.last_word['word'])
            print('last word accent:', self.last_word['accent'])
            print('is last word monosilabo:', self.last_word['monosilabo'])

        return self.syllables  # amount of syllables in the sentence

    def sentence2phonemes(self, sentence):
        # not being used. replaced by word2phonemes
        # findall retrieves a list of characters only
        phonemes = ''.join(re.findall('[^\W]*', self.sentence))  # this step should be done in preprocessing

        for rule in self.char2phone.keys():  # certain rules must be applied first
            for char in self.char2phone[rule]:
                if char in phonemes:
                    # modifying the word on the fly
                    phonemes = re.sub(char, self.char2phone[rule][char], phonemes)

        return phonemes

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

    def divide_word_syllables(self, word):
        sequence = ''.join(word)
        pattern = re.compile(r"""(CDDC(?![FAD]))?
                                 (CDAC(?![FAD]))?
                                 (CDD)?
                                 (CDFC(?![AFD]))?
                                 (CDF)?
                                 (DFC)?
                                 (CCF)?
                                 (CFT)?
                                 (CFC(?![AFD]))?
                                 (CF)?
                                 (DF)?
                                 (TF)?
                                 (TA)?
                                 (FC(?![FAD]))?
                                 (CD(?![AFD]))?
                                 (DC(?=[CT]))?
                                 (CA)?
                                 (F(?=C[FAD])?)?
                                 (A)?
                                 (D)?""", re.VERBOSE)
        match = re.findall(pattern, sequence)
        syllables = '-'.join([syllable for group in match for syllable in group if syllable])

        return syllables

    def reduce_double_syllables(self, word):
        word = [char for char in word]
        for char in range(len(word)):
            if ''.join(word[char:char+2]) in self.double_consonants:
                word[char] = 'T'
                word.pop(char+1)

        return ''.join(word)

    def count_syllables(self, sentence_structure):
        # TODO:
        # apply: 1) sinalefa, 2) diéresis, 3) sinéresis
        # sinéresis: dos vocales que no forman diptongo, forman diptongo. (e.g. gor-je-ar --> gor-jear)
        # diéresis: se separan dos vocales que forman diptongo. (e.g. sua-ve --> su-a-ve)
        # sinalefa: dos vocales de palabras contiguas se diptonguean. (e.g. cie-lo-y-mar --> cie-loy-mar)
        #for word_structure in sentence_structure:
        #number_syllables = re.findall(r'[(FD)(DF)(F)A]', structure)

        #self.sinalefa(sentence_structure)
        structure = ''.join([s for word_structure in sentence_structure for s in word_structure])
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
        input: self (uses information from dictionary last_word)
        output: int [+1, 0, -1]
        '''
        structure = self.last_word['structure']
        phonemes = self.last_word['phonemes']

        monosilabo = self.is_monosilabo(structure)
        accent = self.acentuacion(phonemes, structure, monosilabo)

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

    #def count_word_syllables(self, structure):
    #    return len([vowel for vowel in ''.join(structure).split('C') if vowel])

    def is_monosilabo(self, structure):
        '''
        checks if structure is a monosilabo.
        input: structure of a word
        output: boolean
        '''
        #if self.count_word_syllables(structure) == 1:
        #    return True
        #else:
        #    return False
        pass
    def count_syllables_word(self, word):
        self.word = word
        self.phonemes = self.word2phonemes(self.word)
        self.structure = self.phonemes2structure(self.phonemes)
        structure = ''.join([s for s in self.structure])
        structure = re.sub(r'([FD]{3})', r'\1C\1', structure)  # adding extra consonant

        vowels = re.split('C', structure)
        self_syllables = len([v for v in vowels if v])
        #self.syllables = self.count_word_syllables(self.structure[:])

        if self.verbose:# and self.syllables != 8:  # add second condition for debugging purposes
            print('word', self.word)
            print('phonemes', self.phonemes)
            print('structure', self.structure)
            print('number of metric syllables', self.syllables)
            print()

        return self.syllables  # amount of syllables in the word

    def get_last_word(self):
        self.last_word['word'] = self.sentence[-1]
        self.last_word['phonemes'] = self.phonemes[-1]
        self.last_word['structure'] = self.structure[-1]


if __name__ == '__main__':

    # ph is a dictionary with information regarding vowels, alphabet, char2phone rules, etc.
    ph = phonetics.phonetics
    text = preprocess.read_txt('data/decima2.txt')

    silabeador = Silabeador(**ph)
    #silabeador.count_syllables_sentence(text[0])
    silabeador.count_syllables_text(text)

    #words = ['tendrá', 'tarde', 'temprano', 'antes', 'fue', 'fuimos', 'considerablemente', 'año', 'mañío', 'injobulisomante', 'atardecía', 'compañía', 'aéreo']
    #for word in words:
    #    silabeador.count_syllables_word(word)


    syllabe_patterns = [re.compile(r'(CDDC(?![FAD]))?'),
                       re.compile(r'(CDD)?'),
                       re.compile(r'(CDF)?'),
                       re.compile(r'(DFC)?'),
                       re.compile(r'(CCF)?'),
                       re.compile(r'(CFT)?'),
                       re.compile(r'(CFC(?=[CT\W$]))?'),
                       re.compile(r'(CF)?'),
                       re.compile(r'(DF)?'),
                       re.compile(r'(TF)?'),
                       re.compile(r'(FC(?=C))?'),
                       re.compile(r'(CD)?'),
                       re.compile(r'(CA)?'),
                       re.compile(r'(F)?'),
                           re.compile(r'(A)?')]
