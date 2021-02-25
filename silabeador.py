#!/usr/bin/env python3
# http://www.rimar2000.com.ar/

import pandas as pd
import re
import sys
import phonetics
import preprocess


class Silabeador():
    def __init__(self, verbose=1, **ph):
        '''
        Silabeador class counts metric syllables in a text.
        Its main function is count_syllables_sentence(sentence)
        along with other relevant information throughout the process.
        '''
        self.verbose = verbose  # to print out the result of each function.
        # verbose == 1: prints out the sentence and syllable's number retrieved.
        # verbose == 2: prints out the result of every function.

        # relevant phonetics information used to separate the sentence into metric syllables.
        self.vowels = ph['vowels']
        self.consonants = ph['consonants']
        self.alphabet = ph['alphabet']
        self.phonemes_dict = ph['phonemes_dict']
        self.char2phone = ph['char2phone']  # hierarchical rules to chage characters to phones
        self.punctuation = ph['punctuation']
        self.double_consonants = ph['double_consonants']

        # variables used within each count_syllables_sentence call
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
                          'accent': None}

        self.sinalefa = False  # bool to count using sinalefa

    def count_syllables_text(self, text):
        syllables_text = []
        for line in text:
            syllables_text.append(self.count_syllables_sentence(line))

    def count_syllables_sentence(self, sentence, debug=False):
        '''
        main function that takes a sentence as input and counts the number of metric syllables
        input: string
        output: number of syllables
        '''
        self.sentence = sentence.split()
        # converting characters to phonemes (i.e. 'cazar' --> 'kasar')
        self.phonemes = [self.word2phonemes(word) for word in self.sentence]
        # converting phonemes to structure (i.e. 'kasar' --> 'CFCFC')
        self.structure = [self.phonemes2structure(word) for word in self.phonemes]

        # dividing the structure in syllables (i.e. 'CFCFC' --> CF-CFC)
        self.structure_syllables = [self.divide_structure_syllables(word_structure) for word_structure in self.structure]
        # dividing the word in syllables according to how the structure was previously divided (i.e. 'cazar' --> 'ca-zar')
        self.word_syllables = [self.add_separator(structure, word) for structure, word in zip(self.structure_syllables, self.phonemes)]
        # metric rules are considered when counting syllables in a sentence
        self.last_word = self.get_last_word()

        if self.sinalefa:  # applying sinalefa (i.e. 'vuel-ta-y-me-dia' --> 'vuel-tay-me-dia')
            self.word_syllables = self.apply_sinalefa()

        self.number_syllables = self.count(self.word_syllables, self.metric_rule(self.last_word))

        if debug and self.number_syllables != 8:
            print(sentence)

        if self.verbose == 1:
            print(f'{" ".join(self.sentence)} --> {self.word_syllables} [{self.number_syllables}]')

        elif self.verbose == 2:# and self.number_syllables != 8:  # add second condition for debugging purposes
            print('\nsentence', sentence)
            print('phonemes', self.phonemes)
            print('structure', self.structure)
            print('structure syllables', self.structure_syllables)
            print('word syllables', self.word_syllables)
            print('number of metric syllables', self.number_syllables)

        elif self.verbose == 3:
            print('last word:', self.last_word['word'])
            print('last word structure', self.last_word['structure'])
            print('last word phonemes', self.last_word['phonemes'])
            print('last word syllables', self.last_word['word_syllables'])
            print('last word accent:', self.last_word['accent'])
            print('is last word monosilabo:', self.last_word['monosilabo'])

        return self.number_syllables  # amount of metric syllables in the sentence

    def count_syllables_word(self, word):
        self.sentence = word.split()
        # converting characters to phonemes (i.e. 'cazar' --> 'kasar')
        self.phonemes = [self.word2phonemes(word) for word in self.sentence]
        # converting phonemes to structure (i.e. 'kasar' --> 'CFCFC')
        self.structure = [self.phonemes2structure(word) for word in self.phonemes]

        # dividing the structure in syllables (i.e. 'CFCFC' --> CF-CFC)
        self.structure_syllables = [self.divide_structure_syllables(word_structure) for word_structure in self.structure]
        # dividing the word in syllables according to how the structure was previously divided (i.e. 'cazar' --> 'ca-zar')
        self.word_syllables = [self.add_separator(structure, word) for structure, word in zip(self.structure_syllables, self.phonemes)]
        # metric rules are considered when counting syllables in a sentence
        self.last_word = self.get_last_word()

        return self.last_word

    def apply_sinalefa(self):
        """
        function that applies sinalefa over word_syllables.
        it checks if two contiguous syllables have a vowel and it merges them
        in the same syllable.
        """
        syllables_sinalefa = []
        index = 0
        while index < len(self.word_syllables):
            try:
                # checking if there is sinalefa
                if self.are_vowels(syllables_sinalefa[-1][-1], self.word_syllables[index][0]):
                    merged_syllables = ''.join([syllables_sinalefa[-1], self.word_syllables[index]])
                    # replacing the last syllable with the merged syllable
                    syllables_sinalefa.pop(-1)
                    syllables_sinalefa.append(merged_syllables)
                else:
                    syllables_sinalefa.append(self.word_syllables[index])
            except IndexError:
                # we reached the last word
                syllables_sinalefa.append(self.word_syllables[index])
            finally:
                index += 1

        return '-'.join(syllables_sinalefa)

    def are_vowels(self, c1, c2):
        """
        function that compares if two characters are vowels.
        it returns true if so, otherwise false.
        """
        pattern = re.compile(f"[{''.join(self.vowels)}]")
        if re.match(pattern, c1) and re.match(pattern, c2):
            return True
        else:
            return False

    def word2phonemes(self, word):
        """
        function that takes a word and translates it to phonemes
        following the rules from char2phone dictionary
        """
        # findall retrieves a list of characters only
        phonemes = ''.join(re.findall('[^\W]*', word))  # TODO: deal with punctuation in the middle of sentence
        for rule in self.char2phone.keys():  # certain rules must be applied first
            for char in self.char2phone[rule]:
                if char in phonemes:
                    # modifying the word on the fly
                    phonemes = re.sub(char, self.char2phone[rule][char], phonemes)
        return phonemes

    def phonemes2structure(self, phonemes):
        """
        function that takes a sequence of phonemes and translates it to its structure
        following the mapping in phonemes_dict dictionary.
        double consonants are mapped to just one structure character 'T'
        """
        #print(phonemes)
        phonemes_reduced = self.reduce_double_syllables(phonemes)
        structure = [self.phonemes_dict[phone] if phone in self.alphabet else phone for phone in phonemes_reduced]
        #print(structure)
        return structure

    def divide_structure_syllables(self, word_structure, debug=False):
        sequence = ''.join(word_structure)
        pattern = re.compile(r"""(CDDC(?![AFD]))?
                                 (CDAC(?![AFD]))?
                                 (CFDC)?
                                 (CDD)?
                                 (CDFC(?![AFD]))?
                                 (CDF)?
                                 (CDA)?
                                 (TF)?
                                 (CDC(?![AFD]))?
                                 (DFC)?
                                 (CCF)?
                                 (CFC(?![AFD]))?
                                 (CAC(?![AFD]))?
                                 (TFC(?![AFD]))?
                                 (CFT(?![AFD]))?
                                 (CFC(?![AFD]))?
                                 (TDF)?
                                 (CF)?
                                 (DF)?
                                 (TD)?
                                 (DT)?
                                 (TAC)?
                                 (TA)?
                                 (FC(?![AFD]))?
                                 (FC(?![AFD]))?
                                 (FD)?
                                 (CD(?![AFD]))?
                                 (DC(?=[CT]))?
                                 (CA(?![AFD]))?
                                 (F(?=C[AFD])?)?
                                 (A)?
                                 (D)?
                                 """, flags=re.VERBOSE)
        match = re.findall(pattern, sequence)
        structure_syllables = '-'.join([syllable for group in match for syllable in group if syllable])
        if debug:
            print('word structure', word_structure)
            print('sequence', sequence)
            print('match', match)
            print('structure syllable', structure_syllables)
        return structure_syllables

    def reduce_double_syllables(self, word):
        # TODO: add some exceptions
        word = [char for char in word]
        for char in range(len(word)):
            if ''.join(word[char:char+2]) in self.double_consonants:
                # add a more elegant exception here if double consonants 'ns' is followed by vowels or not.
                # examples to fix: constitución (working), funsión (not working)
                if re.search(r'nsi', ''.join(word)):
                    continue
                word[char] = 'T'
                word.pop(char+1)

        return ''.join(word)

    def add_separator(self, structure, word, debug=False):
        """
        function that adds a hyphen to separate the word's syllables.
        it takes a separated structure (i.e. F-F-CF) and its word ('aora')
        and it inserts the hyphens ('aora' --> 'a-o-ra').
        Special cases are structure T which stands for double consonants (i.e. 'ns', 'tr')
        thus these cases are mapped to two characters.
        """
        word_segmented = list(word)
        char = 0
        forward = 0
        while char < len(structure) - 1:
            if structure[char] == '-':
                word_segmented.insert(char + forward, '-')
            elif structure[char] == 'T':
                forward += 1  # moving one forward because T is mapped to two characters
            char += 1

        if debug:
            print(structure, word, word_segmented, ''.join(word_segmented))

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

    def acentuacion(self, phonemes, structure, monosilabo=False):
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
                return 'none'  # ???
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
    #text = preprocess.read_txt('cases.txt')
    #text = preprocess.read_txt('data/decimas_data_small.txt')

    silabeador = Silabeador(**ph, verbose=2)
    silabeador.sinalefa = True  # counting using sinalefa
    #silabeador.count_syllables_sentence(text[11])
    silabeador.count_syllables_text(text)
    silabeador.count_syllables_sentence('funsión')
    #silabeador.divide_structure_syllables(['C', 'D', 'T', 'D', 'A', 'C'], debug=True)
    #silabeador.add_separator('CF-CA-F', 'maría', debug=True)

    # sinéresis: dos vocales que no forman diptongo, forman diptongo. (e.g. gor-je-ar --> gor-jear)
    # diéresis: se separan dos vocales que forman diptongo. (e.g. sua-ve --> su-a-ve)
    # sinalefa: dos vocales de palabras contiguas se diptonguean. (e.g. cie-lo-y-mar --> cie-loy-mar)
