#!/usr/bin/env python3

# this file contains information about spanish phonetics
# that is needed for the Phonetizer class.

vowels_strong = {'a':'F', 'e':'F', 'o':'F',}
vowels_weak = {'i':'D', 'u':'D', 'ü':'D'}
vowels_accented = {'á':'A', 'é':'A', 'í':'A', 'ó':'A', 'ú':'A'}
consonants = {'m':'C', 'n':'C', 'ñ':'C',
              'p':'C', 't':'C', 'k':'C', 'b':'C', 'd':'C', 'g':'C',
              'C':'C',
              'f':'C', 's':'C', 'L':'C', 'x':'C',
              'l':'C', 'r':'C', 'R':'C'}
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

vowels = list(vowels_strong.keys()) + list(vowels_weak.keys()) + list(vowels_accented.keys())
alphabet = vowels + list(consonants.keys())
phonemes_dict = {**vowels_strong, **vowels_weak, **vowels_accented, **consonants}

phonetics = {'alphabet': alphabet,
             'vowels': vowels,
             #'vowels_strong': vowels_strong,
             #'vowels_weak': vowels_weak,
             #'vowels_accented': vowels_accented,
             'consonants': consonants,
             'char2phone': char2phone,
             'phonemes_dict': phonemes_dict,
             }
