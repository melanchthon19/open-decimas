#!/usr/bin/env python3

from string import punctuation

def read_txt(file):
    with open(file, 'r') as f:
        text = f.readlines()
    # lower casing, striping spaces and break lines, removing final punctuation only
    text_raw = [line.lower().strip().rstrip(punctuation) for line in text if line.strip()]
    
    # add further pre-processing to get rid of non-alphabetic characters.
    return text_raw


if __name__ == '__main__':
    text = read_txt('data/decima2.txt')
    print('first 5 sentences', text[:5])
    print('first line text:', text[0])
    print('amount of lines in text:', len(text))
    print('type of text:', type(text))
    print('type of line:', type(text[0]))
