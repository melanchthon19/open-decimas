#!usr/bin/env python3

def read_txt(file):
    with open(file, 'r') as f:
        text = f.readlines()
    # add further pre-processing to get rid of empty lines and non-alphabetic characters.
    text_raw = [line.lower().strip().split() for line in text]
    # TODO: remove final punctuation only
    return text_raw
