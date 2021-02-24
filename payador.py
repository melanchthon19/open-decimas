#!/usr/bin/env python3

import re
import random
import numpy as np
from string import punctuation
import torch
from transformers import BertForMaskedLM, BertTokenizer

import silabeador
import phonetics


class Payador():
    def __init__(self, ph, verbose=0):
        # Initialize Silabeador to count generated syllables
        self.silabeador = silabeador.Silabeador(verbose, **ph)
        self.silabeador.sinalefa = True  # counting using sinalefa

        # Initialize BETO
        self.tokenizer = BertTokenizer.from_pretrained("pytorch/", do_lower_case=False)
        self.model = BertForMaskedLM.from_pretrained("pytorch/")
        self.model.eval()

        self.pie_forzado = 'la casa'
        self.initial_sentence = self.beto_sentence()
        self.poem = []

        #with open('palabras_todas.txt', 'r') as file:
        #    palabras_todas = file.readlines()
        #    palabras_todas = [palabra.strip() for palabra in palabras_todas]


    def random_masks(self):
        return random.randint(3,6)

    def beto_sentence(self, sentence=False):
        if not sentence:  # creating initial sentence
            sentence = '[CLS] ' + self.pie_forzado + self.beto_added_sentence()

        else:  # formatting sentence
            sentence = '[CLS] ' + sentence + ' [SEP]'

        return sentence

    def beto_added_sentence(self):
        masks_to_add = self.random_masks() * '[MASK] '
        return ' ' + masks_to_add + '[SEP]'

    def generate_poem(self, N):
        n = 0
        previous_sentence = False

        while n < N:  # generating an N line's poem
            # using the previous sentence as context for the new sentence
            if previous_sentence:
                new_line = self.generate_sentence(actual_context)
                actual_context = self.beto_sentence(new_line) + self.beto_added_sentence()
                self.poem.append(new_line)

            else:  # there is no previous sentence
                first_line = self.generate_sentence(self.initial_sentence)
                self.poem.append(first_line.replace('[CLS] ', ''))
                previous_sentence = self.beto_sentence(first_line)
                actual_context = previous_sentence + self.beto_added_sentence()

            n += 1

        return self.poem

    def generate_decima(self, N):
        n = 0
        previous_sentence = False

        while n < N:  # generating an N line's poem
            # using the previous sentence as context for the new sentence
            if previous_sentence:
                new_line = self.generate_octosilabo(actual_context)
                actual_context = self.beto_sentence(new_line) + self.beto_added_sentence()
                self.poem.append(new_line)

            else:  # there is no previous sentence
                first_line = self.generate_octosilabo(self.initial_sentence)
                self.poem.append(first_line.replace('[CLS] ', ''))
                previous_sentence = self.beto_sentence(first_line)
                actual_context = previous_sentence + self.beto_added_sentence()

            n += 1

        return self.poem

    def filter_tokens(self, tokens):
        tokens = [token for token in tokens if token != '[UNK]']
        #tokens = [token for token in tokens if token not in punctuation]
        tokens = [token for token in tokens if token.count('#') == 0]
        tokens = [token for token in tokens if token.isalpha()]
        #tokens = [token for token in tokens if token in palabras_todas and len(token) > 1]

        if len([token for token in tokens if len(token) > 1]) > 0:
            tokens = [token for token in tokens if len(token) > 1]

        return tokens

    def retrieve_token(self, idxs, max_tokens):
        chosen = False
        while not chosen:
            try:
                # retrieving only the first max_tokens
                predicted_token = self.tokenizer.convert_ids_to_tokens(idxs[:max_tokens])
                #print('MASK:',predicted_token)

                # filtering retrieved tokens and choosing one token
                predicted_token_filtered = self.filter_tokens(predicted_token)
                chosen_word = random.choice(predicted_token_filtered)  # randomly choosing
                chosen = True

            except IndexError:
                max_tokens *= 2

        return chosen_word

    def generate_word(self, text, masked_indxs):
        # converting text to BERTO format
        tokens = self.tokenizer.tokenize(text)
        indexed_tokens = self.tokenizer.convert_tokens_to_ids(tokens)
        tokens_tensor = torch.tensor([indexed_tokens])

        # getting LM predictions for [MASK] index
        predictions = self.model(tokens_tensor)[0]
        focus_masked_indx = masked_indxs.pop(0)
        idxs = torch.argsort(predictions[0,focus_masked_indx], descending=True)

        # randomly choosing a word considering first max_tokens possible tokens
        max_tokens = 20
        chosen_word = self.retrieve_token(idxs, max_tokens)

        # assigning the new token
        new_text = text.split()
        new_text[focus_masked_indx] = chosen_word
        new_text = ' '.join(new_text)

        return new_text, masked_indxs

    def generate_sentence(self, sentence, using_score=False):
        # use score to decide if sentence is "good" or "bad" given the LM
        if using_score:
            score = 150  # setting a score threshold
            # if generated sentence is greater than threshold, create another one
            while score >= 150:
                sentence = self.fill_masked_indexes(sentence)
                # getting the sentence's score
                score = self.score_sentence(sentence)
                print(sentence, score)
        else:
            sentence = self.fill_masked_indexes(sentence)

        return sentence

    def generate_octosilabo(self, sentence):
        octosilabo = False
        while not octosilabo:
            line = self.fill_masked_indexes(sentence)

            # checking number of syllables
            line = self.clean_sentence(line)
            number_syllables = self.silabeador.count_syllables_sentence(line)
            if number_syllables == 8:
                print(sentence, line, number_syllables)
                octosilabo = True

        sentence = self.clean_sentence(sentence)

        return sentence

    def fill_masked_indexes(self, sentence):
        initial_sentence = sentence[:]
        masked_indxs = [index for index, word in enumerate(initial_sentence.split()) if re.match(r'\[MASK\]', word)]
        while masked_indxs:
            sentence, masked_indxs = self.generate_word(sentence, masked_indxs)

        return sentence

    def clean(self, poem=False, sentence=False):
        if poem: text = poem
        elif sentence: text = sentence

        text = text.replace('[CLS]', '')
        text = text.replace('[SEP]', '\n')
        text = [line.strip() for line in text.split('\n') if line]

        if poem: return text
        elif sentence: return text[-1]

    def clean_sentence(self, sentence):
        sentence = re.findall(r'(.*?) \[SEP\]', sentence)
        sentence = sentence[-1].strip()

        return sentence

    def print_poem(self, poem):
        print('POEMA')
        for i, line in enumerate(poem):
            #print(line, self.score_sentence(line))
            print(line)

    def score_sentence(self, sentence):
        # function adapted from:
        # https://www.scribendi.ai/comparing-bert-and-gpt-2-as-language-models-to-score-the-grammatical-correctness-of-a-sentence/
        tokenize_input = self.tokenizer.tokenize(sentence)
        tokenize_input = ["[CLS]"]+tokenize_input+["[SEP]"]
        tensor_input = torch.tensor([self.tokenizer.convert_tokens_to_ids(tokenize_input)])
        with torch.no_grad():
            loss = self.model(tensor_input, labels=tensor_input)[0]

        return np.exp(loss.detach().numpy())


if __name__ == '__main__':
    # BETO --> https://github.com/dccuchile/beto
    # How to use it --> https://colab.research.google.com/drive/1uRwg4UmPgYIqGYY4gW_Nsw9782GFJbPt#scrollTo=9KXo6-ahoJoM

    # palabras del español --> https://github.com/JorgeDuenasLerin/diccionario-espanol-txt

    ph = phonetics.phonetics
    payador = Payador(ph, verbose=0)  # instantiates Payador class and Silabeador class within it
    poem = payador.generate_decima(4)
    payador.print_poem(poem)
