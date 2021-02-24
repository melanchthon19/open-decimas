#!/usr/bin/env python3

import re
import random
import numpy as np
import torch
from transformers import BertForMaskedLM, BertTokenizer


class Escritor():
    def __init__(self):
        """
        Escritor is a class in charge of handling BETO model and using it as LM
        to generate new lines of text.

        It uses the previous sentence as context for the new sentence.

        Parameters that are adjustable according to different kind of texts:
        - pie_forzado: initial string to be used when creating the first line.
        - min_words_line: minimum amount of words that are in each line.
        - max_words_line: maximum amount of words that are in each line.
        - max_tokens: amount of retrieved tokens from which to choose everytime BETO is called.
        - score: threshold used to accept or reject a sentence using BETO's Language Model.
        """
        # Initialize BETO
        self.tokenizer = BertTokenizer.from_pretrained("pytorch/", do_lower_case=False)
        self.model = BertForMaskedLM.from_pretrained("pytorch/")
        self.model.eval()

        # Default parameters to generate different kind of texts
        self.pie_forzado = 'la casa'
        self.min_words_line = 8
        self.max_words_line = 12
        self.max_tokens = 20  # amount of possible tokens from which to choose
        self.score = 0  # if score is given, then it is used a threshold to accept or reject sentences

        # Initializing inner variables
        self.initial_context = self.beto_sentence()
        self.text = []

    def beto_sentence(self, sentence=False):
        if not sentence:  # creating initial context in beto format
            sentence = '[CLS] ' + self.pie_forzado + self.beto_added_sentence()

        else:  # formatting sentence in beto format
            sentence = '[CLS] ' + sentence + ' [SEP]'

        return sentence

    def beto_added_sentence(self):
        masks_to_add = self.random_masks() * '[MASK] '
        return ' ' + masks_to_add + '[SEP]'

    def random_masks(self):
        return random.randint(self.min_words_line, self.max_words_line)

    def generate_text(self, N):
        n = 0
        previous_sentence = False

        while n < N:  # generating an N line's text
            # using the previous sentence as context for the new sentence
            if previous_sentence:
                new_sentence = self.generate_sentence(actual_context)
                actual_context = self.beto_sentence(new_sentence) + self.beto_added_sentence()
                self.text.append(new_sentence)

            else:  # there is no previous sentence
                first_sentence = self.generate_sentence(self.initial_context)
                #self.text.append(first_sentence.replace('[CLS] ', ''))
                self.text.append(first_sentence)
                previous_sentence = self.beto_sentence(first_sentence)
                actual_context = previous_sentence + self.beto_added_sentence()

            n += 1

        return self.text

    def generate_sentence(self, actual_context):
        # use score to decide if sentence is "good" or "bad" given the LM
        if self.score:
            score = self.score + 1
            # if generated sentence is greater than threshold, create another one
            while score >= self.score:
                context = actual_context[:]
                sentence = self.fill_masked_indexes(context)
                # getting the sentence's score
                score = self.score_sentence(sentence)
                #print(sentence, score)
        else:
            context = actual_context[:]
            sentence = self.fill_masked_indexes(context)

        sentence = self.clean_sentence(sentence)

        return sentence

    def fill_masked_indexes(self, sentence):
        initial_sentence = sentence[:]
        masked_indxs = [index for index, word in enumerate(initial_sentence.split()) if re.match(r'\[MASK\]', word)]
        while masked_indxs:
            sentence, masked_indxs = self.generate_word(sentence, masked_indxs)

        return sentence

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
        max_tokens = self.max_tokens
        chosen_word = self.retrieve_token(idxs, max_tokens)

        # assigning the new token
        new_text = text.split()
        new_text[focus_masked_indx] = chosen_word
        new_text = ' '.join(new_text)

        return new_text, masked_indxs

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

    def filter_tokens(self, tokens):
        tokens = [token for token in tokens if token != '[UNK]']
        #tokens = [token for token in tokens if token not in punctuation]
        tokens = [token for token in tokens if token.count('#') == 0]
        tokens = [token for token in tokens if token.isalpha()]
        #tokens = [token for token in tokens if token in palabras_todas and len(token) > 1]

        if len([token for token in tokens if len(token) > 1]) > 0:
            tokens = [token for token in tokens if len(token) > 1]

        return tokens

    def score_sentence(self, sentence):
        # function adapted from:
        # https://www.scribendi.ai/comparing-bert-and-gpt-2-as-language-models-to-score-the-grammatical-correctness-of-a-sentence/
        tokenize_input = self.tokenizer.tokenize(sentence)
        tokenize_input = ["[CLS]"]+tokenize_input+["[SEP]"]
        tensor_input = torch.tensor([self.tokenizer.convert_tokens_to_ids(tokenize_input)])
        with torch.no_grad():
            loss = self.model(tensor_input, labels=tensor_input)[0]

        return np.exp(loss.detach().numpy())

    def clean_sentence(self, sentence):
        sentence = re.findall(r'\[\w{3}\] (.*?) (?=\[SEP\])', sentence)

        return sentence[-1]

    def print_text(self, text):
        print('TEXT')
        for i, line in enumerate(text):
            #print(line, self.score_sentence(line))
            print(line)


if __name__ == '__main__':
    # BETO --> https://github.com/dccuchile/beto
    # How to use it --> https://colab.research.google.com/drive/1uRwg4UmPgYIqGYY4gW_Nsw9782GFJbPt#scrollTo=9KXo6-ahoJoM

    # palabras del español --> https://github.com/JorgeDuenasLerin/diccionario-espanol-txt

    escritor = Escritor()  # instantiates Escritor class
    #escritor.score = 200  # setting a score threshold
    text = escritor.generate_text(4)
    escritor.print_text(text)
