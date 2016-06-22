#!/usr/bin/python

import re
import sys
import os
import collections
import json


def get_words(text): return re.findall('[a-z]+', text.lower())


def create_dictionary(word_list):
    model = collections.defaultdict(lambda: 1)
    for f in word_list:
        model[f] += 1

    return model


def train_dictionary(dictionary, word_list):
    for w in word_list:
        try:
            dictionary[w] += 1
        except:
            dictionary[w] = 1

    return dictionary


def delete_from_dictionary(dictionary, word_list):
    for w in word_list:
        del dictionary[w]

    return dictionary



def save(dictionary, file_dictionary):
    with open(file_dictionary, 'w') as f:
        json.dump(dictionary, f, sort_keys=True, indent=2, separators=(',', ': '))


def load(file_dictionary):
    with open(file_dictionary) as f:
        dictionary = json.load(f)

    return dictionary


def main():
    if len(sys.argv) != 3:
        sys.stderr.write("Error: Two arguments needed.\n")
        sys.exit(1)

    file_dictionary = sys.argv[1]
    input_arg = sys.argv[2]

    is_dictionary_exist = os.path.isfile(file_dictionary)
    is_text_exist = os.path.isfile(input_arg)

    if re.match("^add:[a-z]+", input_arg.lower()):
        word_list = get_words(input_arg[4:])
        if is_dictionary_exist:
            dictionary = train_dictionary(load(file_dictionary), word_list)
        else:
            dictionary = create_dictionary(get_words(str(word_list)))
        save(dictionary, file_dictionary)
        sys.exit(0)

    if re.match("^del:[a-z]+", input_arg.lower()):
        if not is_dictionary_exist:
            sys.stderr.write("Error: Could not delete from \'%s\': Dictionary does not exists.\n" % file_dictionary)
            sys.exit(1)
        word_list = get_words(input_arg[4:])
        dictionary = delete_from_dictionary(load(file_dictionary), word_list)
        save(dictionary, file_dictionary)
        sys.exit(0)

    if not is_text_exist:
        sys.stderr.write("Error: Text file does not exists.\n")
        sys.exit(1)

    if is_dictionary_exist:
        dictionary = train_dictionary(load(file_dictionary), get_words(file(input_arg).read()))
    else:
        dictionary = create_dictionary(get_words(file(input_arg).read()))

    save(dictionary, file_dictionary)


if __name__ == "__main__":
    main()
