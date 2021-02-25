#!/usr/bin/env python3

import re
import random
import numpy as np
from string import punctuation
import torch
from transformers import BertForMaskedLM, BertTokenizer

import silabeador
import escritor
import phonetics


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

    def generate_octosilabo(self):
        octosilabo = False
        while not octosilabo:
            line = self.escritor.generate_text(N=1)[-1]

            # checking number of syllables
            number_syllables = self.silabeador.count_syllables_sentence(line)
            if number_syllables == 8:
                octosilabo = True

                return line

    def generate_octosilabo_N(self, N):
        n = 0
        octosilabo_N = []
        while n < N:
            octosilabo_N.append(self.generate_octosilabo())
            n += 1

        return octosilabo_N

    def print_decima(self, decima):
        print('DECIMA')
        for i, line in enumerate(decima):
            print(line)


if __name__ == '__main__':

    ph = phonetics.phonetics
    payador = Payador(ph, verbose=0)  # instantiates Payador class and Silabeador class within it
    octosilabo = payador.generate_octosilabo()
    print(octosilabo)
    twelve_octosilabo = payador.generate_octosilabo_N(N=12)
    payador.print_decima(twelve_octosilabo)
