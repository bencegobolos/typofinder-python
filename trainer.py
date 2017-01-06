#!/usr/bin/python2

# This file is made to maintain the htc-dictionary.json file.
# If you want to add or remove words, please use this script
# instead of modifying the .json file directly.

import os
import re
import sys
import argparse
import logging

from classes.linguist import Linguist

logging.basicConfig(format='[%(asctime)s][%(levelname)8s][%(name)s]: %(message)s')
_root_log = logging.getLogger("trainer")
_log = _root_log.getChild(__name__)


def set_logging_verbosity(level):
    if not level:
        _root_log.setLevel(logging.WARNING)
    elif level == 1:
        _root_log.setLevel(logging.INFO)
    else:
        _root_log.setLevel(logging.DEBUG)


def get_arguments():
    desc = 'Update your dictionary file for the typo-finder script.'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("-v", "--verbose", action="count", help="Increase verbosity level")
    parser.add_argument('-d', '--dictionary',
                        help='define the dictionary you want to update (in .json format) which contains '
                             'the known words (\'htc-dictionary.json\' is given by default).',
                        type=str, default='htc-dictionary.json', metavar='DICTIONARY')
    parser.add_argument('--add',
                        help='add a new word or increase the likelihood of suggestion.',
                        nargs='*', metavar='ADD')
    parser.add_argument('--delete',
                        help='delete a word from the dictionary.',
                        nargs='*', metavar='DELETE')
    parser.add_argument('-t', '--train',
                        help='train dictionary from a file (add every word).',
                        type=str, metavar='TRAIN')

    return parser.parse_args()


def validate_arguments(args):
    """
    :param args: Input arguments of the trainer script.
    :return:
    * False: if directory file does not exists or when no operations will be executed.
    * True: otherwise.
    """
    if not args.add and not args.delete and not args.train:
        _log.warning('No operation has been executed on dictionary: \'%s\'' % args.dictionary)
        return False

    if args.train is not None and not os.path.exists(args.train):
        _log.error('File does not exists: \'%s\'' % args.train)
        return False

    return True


def get_words(text):
    return re.findall('[a-z]+', text.lower())


def main():
    args = get_arguments()
    set_logging_verbosity(args.verbose)
    if not validate_arguments(args):
        sys.exit(1)

    json_dictionary_path = args.dictionary
    is_json_dictionary_exist = os.path.exists(json_dictionary_path)

    dictionary = Linguist()

    if args.train is not None:
        text_file_path = args.train
        if is_json_dictionary_exist:
            dictionary.load_dictionary_from_json(json_dictionary_path)
        dictionary.train_dictionary(get_words(file(text_file_path).read()))
        dictionary.save_dictionary_to_json(json_dictionary_path)
        is_json_dictionary_exist = True

    if args.add is not None:
        add_word_list = [word.lower() for word in args.add]
        if is_json_dictionary_exist:
            dictionary.load_dictionary_from_json(json_dictionary_path)
        else:
            _log.info("New dictionary file will be created: \'%s\'" % json_dictionary_path)
        dictionary.train_dictionary(add_word_list)
        dictionary.save_dictionary_to_json(json_dictionary_path)

    if args.delete is not None:
        delete_word_list = [word.lower() for word in args.delete]
        if not is_json_dictionary_exist:
            _log.error("Error: Could not delete from \'%s\': Dictionary does not exists." % json_dictionary_path)
            sys.exit(1)
        dictionary.load_dictionary_from_json(json_dictionary_path)
        dictionary.delete_from_dictionary(delete_word_list)
        dictionary.save_dictionary_to_json(json_dictionary_path)


if __name__ == "__main__":
    main()
