#!/usr/bin/env python3

import time
import re
import random
import numpy as np
from string import punctuation
import torch
from transformers import BertForMaskedLM, BertTokenizer

import silabeador
import escritor
import phonetics
import rimador

class Payador():
    def __init__(self, ph, verbose=0):
        # Initializing Silabeador class to count generated syllables
        self.silabeador = silabeador.Silabeador(verbose, **ph)
        self.silabeador.sinalefa = True  # counting using sinalefa

        # Initializing Escritor class to generate sentences.
        # This class intializes BETO model.
        self.escritor = escritor.Escritor()
        self.escritor.min_words_line = 3
        self.escritor.max_words_line = 6

        # Initializing Rimador class to generate decimas.
        self.rimador = rimador.Rimador(ph, verbose)
        
        # Initializing inner variables
        self.previous_octosilabo = False  # used as a given context for Escritor class
        self.decima = []

    def generate_octosilabo(self, rhyme=False):
        octosilabo = False
        if rhyme: with_rhyme = False
        else: with_rhyme = True

        while not (octosilabo and with_rhyme):
            line = self.escritor.generate_text(N=1, given_context=self.previous_octosilabo)[-1]

            # checking number of syllables
            number_syllables = self.silabeador.count_syllables_sentence(line)
            if number_syllables == 8:
                octosilabo = True
            else:
                continue

            # checking rhyme
            if rhyme == 'ABBA':
                print(len(self.decima), line.split()[-1])
                if self.rimador.is_abba_rhyme(len(self.decima), line.split()[-1]):
                    with_rhyme = True

            if rhyme == 'decima':
                if self.rimador.is_decima_rhyme(len(self.decima), line.split()[-1]):
                    with_rhyme = True

            time.sleep(1)

        return line

    def generate_octosilabo_N(self, N):
        n = 0
        octosilabo_N = []
        while n < N:
            new_octosilabo = self.generate_octosilabo()
            octosilabo_N.append(new_octosilabo)
            self.previous_octosilabo = new_octosilabo
            n += 1

        return octosilabo_N

    def generate_decima(self):
        n = 1
        while n <= 10:  # decimas are ten verses long
            new_verse = self.generate_octosilabo(rhyme='decima')
            self.decima.append(new_verse)
            self.previous_octosilabo = new_verse
            n += 1
        print(self.rimador.decima_rhyme)
        return self.decima

    def print_decima(self, decima):
        print('DECIMA')
        for i, line in enumerate(decima):
            print(line)


if __name__ == '__main__':

    ph = phonetics.phonetics
    payador = Payador(ph, verbose=0)  # instantiates Payador class and Silabeador class within it

    #octosilabo = payador.generate_octosilabo()
    #print(octosilabo)

    #octosilabo_N = payador.generate_octosilabo_N(N=4)
    #payador.print_decima(octosilabo_N)

    decima = payador.generate_decima()
    payador.print_decima(decima)
