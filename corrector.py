#!/usr/bin/python

import sys
import re
import json
import os


ALPHABET = 'abcdefghijklmnopqrstuvwxyz'


def words(text): return re.findall('[a-z]+', text.lower())


def load(file_dict):
    with open(file_dict) as f:
        dict = json.load(f)

    return dict


def edits1(word):
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes = [a + b[1:] for a, b in splits if b]
    transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
    replaces = [a + c + b[1:] for a, b in splits for c in ALPHABET if b]
    inserts = [a + c + b for a, b in splits for c in ALPHABET]
    return set(deletes + transposes + replaces + inserts)


def known_edits2(word, dict):
    return set(e2 for e1 in edits1(word) for e2 in edits1(e1) if e2 in dict)


def known(words, dict): return set(w for w in words if w in dict)


def correct(word, dict):
    candidates = known([word], dict) or known(edits1(word), dict) or known_edits2(word, dict) or [word]
    return max(candidates, key=dict.get)


def main():
    if len(sys.argv) != 3:
        sys.stderr.write("Not enough arguments.\n")
        sys.exit(1)

    file_dict = sys.argv[1]
    file_text = sys.argv[2]

    if not os.path.isfile(file_dict) or not os.path.isfile(file_text):
        sys.stderr.write("Dictionary or text file does not exists.\n")
        sys.exit(1)

    result = True
    dict = load(file_dict)
    content = set(words(file(file_text).read()))
    diff = content.difference(dict)
    if diff: result = False

    for word in diff:
        suggestion = correct(word, dict)
        if word != suggestion:
            print("Unknown word: \'%s\'. Did you mean: \'%s\'?" % (word, suggestion))
        else:
            print("Unknown word: \'%s\'. Suggestion is not available." % word)

    return result


if __name__ == "__main__":
    main()