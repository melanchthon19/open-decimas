#!/usr/bin/env python3

import re
import random
import numpy as np
from string import punctuation
import torch
from transformers import BertForMaskedLM, BertTokenizer
import silabeador
import phonetics


def filter_tokens(tokens):
    tokens = [token for token in tokens if token != '[UNK]']
    #tokens = [token for token in tokens if token not in punctuation]
    tokens = [token for token in tokens if token.count('#') == 0]
    #tokens = [token for token in tokens if token in palabras_todas and len(token) > 1]

    if len([token for token in tokens if len(token) > 1]) > 0:
        tokens = [token for token in tokens if len(token) > 1]

    return tokens

def generate_word(text, masked_indxs):
    # converting text to BERTO format
    tokens = tokenizer.tokenize(text)
    indexed_tokens = tokenizer.convert_tokens_to_ids(tokens)
    tokens_tensor = torch.tensor([indexed_tokens])

    # getting LM predictions for [MASK] index
    predictions = model(tokens_tensor)[0]
    focus_masked_indx = masked_indxs.pop(0)
    idxs = torch.argsort(predictions[0,focus_masked_indx], descending=True)

    # retrieving only the first 20 tokens
    predicted_token = tokenizer.convert_ids_to_tokens(idxs[:200])
    #print('MASK:',predicted_token)

    # filtering retrieved tokens and choosing one token
    predicted_token_filtered = filter_tokens(predicted_token)
    chosen_word = random.choice(predicted_token_filtered)  # randomly choosing

    # assigning the new token
    new_text = text.split()
    new_text[focus_masked_indx] = chosen_word
    new_text = ' '.join(new_text)

    return new_text, masked_indxs

def generate_sentence(sentence, using_score=False):
    initial_sentence = sentence[:]
    # use score to decide if sentence is "good" or "bad" given the LM
    if using_score:
        score = 150  # set a score threshold
        # if generated sentence is greater than threshold, create another one
        while score >= 150:
            masked_indxs = [index for index, word in enumerate(initial_sentence.split()) if re.match(r'\[MASK\]', word)]
            while masked_indxs:
                sentence, masked_indxs = generate_word(sentence, masked_indxs)

            # getting the sentence's score
            score = score_sentence(sentence)
            print(sentence, score)
    else:
        # these three lines could be refactored
        masked_indxs = [index for index, word in enumerate(initial_sentence.split()) if re.match(r'\[MASK\]', word)]
        while masked_indxs:
            sentence, masked_indxs = generate_word(sentence, masked_indxs)

    return sentence

def clean_and_print(poem):
    poem = poem.replace('[CLS]', '')
    poem = poem.replace('[SEP]', '\n')
    poem = [line.strip() for line in poem.split('\n') if line]
    print('POEM')
    for i, line in enumerate(poem):
        print(line, score_sentence(line))

    return poem

def score_sentence(sentence):
    # function adapted from:
    # https://www.scribendi.ai/comparing-bert-and-gpt-2-as-language-models-to-score-the-grammatical-correctness-of-a-sentence/
    tokenize_input = tokenizer.tokenize(sentence)
    tokenize_input = ["[CLS]"]+tokenize_input+["[SEP]"]
    tensor_input = torch.tensor([tokenizer.convert_tokens_to_ids(tokenize_input)])
    with torch.no_grad():
        loss=model(tensor_input, labels=tensor_input)[0]

    return np.exp(loss.detach().numpy())


if __name__ == '__main__':
    # BETO --> https://github.com/dccuchile/beto
    # How to use it --> https://colab.research.google.com/drive/1uRwg4UmPgYIqGYY4gW_Nsw9782GFJbPt#scrollTo=9KXo6-ahoJoM

    # palabras del español --> https://github.com/JorgeDuenasLerin/diccionario-espanol-txt

    # Initialize BERTO
    tokenizer = BertTokenizer.from_pretrained("pytorch/", do_lower_case=False)
    model = BertForMaskedLM.from_pretrained("pytorch/")
    model.eval()

    with open('palabras_todas.txt', 'r') as file:
        palabras_todas = file.readlines()
        palabras_todas = [palabra.strip() for palabra in palabras_todas]

    sentence = '[CLS] la casa [MASK] [MASK] [MASK] [MASK] [MASK] [SEP]'
    added_sentence = ' [MASK] [MASK] [MASK] [MASK] [MASK] [SEP]'

    poem = ''
    text = generate_sentence(sentence)
    print(text)

    n = 1
    N = 12
    while n <= N:  # generating a 12 line's poem
        print(text)
        previous_sentence = re.findall(r'\[SEP\].*?\[SEP\]', text)
        # using the previous sentence as context for the new sentence
        if previous_sentence:
            previous_sentence = previous_sentence[-1]
            poem += previous_sentence
            previous_sentence = previous_sentence.replace('[SEP]', '[CLS]', 1)
            actual_text = previous_sentence + added_sentence
            print('previous', previous_sentence)
            actual_text = previous_sentence + added_sentence
        else:  # there is no previous sentence
            poem += text
            actual_text = text + added_sentence

        print('actual', actual_text)
        text = generate_sentence(actual_text)
        n += 1

    poem = clean_and_print(poem)
