#!/usr/bin/env python3

import re
import phonetics
import silabeador


class Rimador():
    def __init__(self, ph, verbose=0):
        self.rima_consonante = False
        self.rima_asonante = False
        self.decima_structure = {0:'A',1:'B', 2:'B', 3:'A', 4:'A', 5:'C', 6:'C', 7:'D', 8:'D', 9:'C'}
        self.decima_rhyme = {'A': False, 'B': False, 'C': False, 'D': False}

        self.abba_structure = {0: 'A', 1: 'B', 2: 'B', 3: 'A'}
        self.abba_rhyme = {'A': False, 'B': False}

        self.silabeador = silabeador.Silabeador(verbose, **ph)
        self.ph = ph

    def is_rima_consonante(self, w1, w2):
        # return True if after the last accented vowel, the repeated sounds are consonants and vowels
        # otherwise False
        w1_rhyme = self.get_rhyme_word(w1)
        w2_rhyme = self.get_rhyme_word(w2)

        if w1_rhyme == w2_rhyme:
            return True
        else:
            return False

    def get_rhyme_word(self, word):
        self.silabeador.count_syllables_word(word)

        # this lines should be part of Acentuador class
        monosilabo = self.silabeador.is_monosilabo(self.silabeador.last_word['word_syllables'])
        accent = self.silabeador.acentuacion(self.silabeador.last_word['phonemes'],\
                                             self.silabeador.last_word['structure'],\
                                             monosilabo)
        self.silabeador.last_word['monosilabo'] = monosilabo
        self.silabeador.last_word['accent'] = accent

        word_rhyme = self.get_segment_accented(self.silabeador.last_word)

        return word_rhyme

    def get_segment_accented(self, last_word):
        if last_word['accent'] == 'none':  # not very clean. to fix also in silabeador class
            return last_word['phonemes']

        elif last_word['accent'] == 'aguda':
            return self.rhyme_only(last_word['word_syllables'].split('-')[-1])

        elif last_word['accent'] == 'grave':
            return self.rhyme_only(last_word['word_syllables'].split('-')[-2:])

        elif last_word['accent'] == 'esdrujula':
            return self.rhyme_only(last_word['word_syllables'].split('-')[-3:])

        else:
            raise AttributeError()

    def rhyme_only(self, segment_accented):
        # segment from accented vowel, without previous consonants
        pattern = re.compile(f'.*?({self.ph["vowels"]}.*)')
        try:
            rhyme_only = re.match(pattern, segment_accented)
        except TypeError:
            rhyme_only = re.match(pattern, '-'.join(segment_accented))

        return rhyme_only.group(1)

    def is_rima_asonante(self, w1, w2):
        # return True if after the last accented vowel, the repeated sounds are vowels
        # otherwise False
        w1_rhyme = self.get_rhyme_word(w1)
        w2_rhyme = self.get_rhyme_word(w2)

        w1_rhyme = ''.join([char for char in w1_rhyme if char not in self.ph['consonants']])
        w2_rhyme = ''.join([char for char in w2_rhyme if char not in self.ph['consonants']])

        if w1_rhyme == w2_rhyme:
            return True
        else:
            return False

    def is_any_rhyme(self, w1, w2):
        if self.is_rima_asonante(w1, w2):
            return True
        elif self.is_rima_consonante(w1, w2):
            return True
        else:
            return False

    def is_ABBA(self, verse_number, word):
        if not self.abba_rhyme[self.abba_structure[verse_number]]:
            print(f'not previous rhyme in {self.abba_rhyme[self.abba_structure[verse_number]]}')
            self.abba_rhyme[self.abba_structure[verse_number]] = (word, self.get_rhyme_word(word))
            return True

        else:
            if self.is_any_rhyme(self.abba_rhyme[self.abba_structure[verse_number]][0], word):
                print(f'there is rhyme between: {self.abba_rhyme[self.abba_structure[verse_number]][0]} {word}')
                return True
            else:
                print(f'there is no rhyme between: {self.abba_rhyme[self.abba_structure[verse_number]][0]} {word}')
                return False


    def is_abba_rhyme(self, rhyme_char, compared_word):
        if not self.abba_rhyme[self.abba_structure[rhyme_char]]:
            self.abba_rhyme[self.abba_structure[rhyme_char]] = compared_word

            return True

        else:
            if self.is_any_rhyme(self.abba_rhyme[self.abba_structure[rhyme_char]], compared_word):
                print(self.abba_rhyme[self.abba_structure[rhyme_char]], compared_word)
                return True
            else:
                return False

    def is_decima_rhyme(self, rhyme_char, compared_word):
        if not self.decima_rhyme[self.decima_structure[rhyme_char]]:
            self.decima_rhyme[self.decima_structure[rhyme_char]] = compared_word

            return True

        else:
            if self.is_any_rhyme(self.decima_rhyme[self.decima_structure[rhyme_char]], compared_word):
                print(self.decima_rhyme[self.decima_structure[rhyme_char]], compared_word)
                return True
            else:
                return False


if __name__ == '__main__':
    ph = phonetics.phonetics
    rimador = Rimador(ph, verbose=0)
    print(rimador.is_rima_asonante('camión', 'martillo'))
    print(rimador.is_rima_asonante('camión', 'canción'))
    print(rimador.is_rima_asonante('camión', 'cansión'))
    print(rimador.is_rima_asonante('cuchillo', 'martillo'))
    print(rimador.is_rima_asonante('abro', 'cuajo'))
    print(rimador.is_rima_asonante('abro', 'zapato'))
