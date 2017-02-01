#!/usr/bin/python2

"""
This script is made to maintain the htc-dictionary.json file.
If you want to add or remove words, please use this script
instead of modifying the .json file directly.
"""

import os
import sys
import argparse
import logging
import textwrap

from src.linguist import Linguist
from src.utils import get_words, is_text_file

logging.basicConfig(format='[%(asctime)s][%(levelname)8s][%(name)s]: %(message)s')
_root_log = logging.getLogger("typofinder")
_log = _root_log.getChild(__name__)


def set_logging_verbosity(level):
    if not level:
        _root_log.setLevel(logging.WARNING)
    elif level == 1:
        _root_log.setLevel(logging.INFO)
    else:
        _root_log.setLevel(logging.DEBUG)


def get_arguments():
    description = 'Update your dictionary file for the typo-finder script.'
    epilog = textwrap.dedent("""
    example usages:
      trainer.py --add hello world --delete hey ho
                            Add 'hello' and 'world' words to htc-dictionary.json
                            file and delete 'hey' and 'ho' words from this file.
      trainer.py -v -d my-dict.json -t text_file
                            Get every word from text_file and add them to
                            my-dict.json file. It will be created if it was not
                            existed previously. Use single level verbosity (few
                            additional info will be logged to standard error
                            output).
      trainer.py -vv -t text_file --add testing --delete test
                            Train htc-dictionary.json dictionary from text_file,
                            add 'testing' word (or increment the word's
                            likelihood if already known by dictionary) and
                            delete 'test' word from dictionary. Use max level
                            of verbosity (more additional info will be logged
                            to standard error output).
    """)
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=description,
                                     epilog=epilog)
    parser.add_argument('-v', '--verbose', action='count', help='increase verbosity level')
    parser.add_argument('-d', '--dictionary',
                        help='define the dictionary (in .json format) you want to update which contains '
                             'the known words (\'htc-dictionary.json\' is given by default).',
                        type=str, default='htc-dictionary.json', metavar='DICTIONARY_FILE')
    parser.add_argument('--add',
                        help='add new word(s) or increase the likelihood of suggestion.',
                        nargs='*', metavar='WORD')
    parser.add_argument('--delete',
                        help='delete word(s) from the dictionary.',
                        nargs='*', metavar='WORD')
    parser.add_argument('-t', '--train',
                        help='train dictionary from a file (add every word).',
                        type=str, metavar='TEXT_FILE')

    return parser.parse_args()


def validate_arguments(args):
    """
    :param args: Input arguments of the trainer script.
    :return:
      * False: if input arguments would cause an error in the program.
      * True: otherwise.
    """
    if args.train is not None:
        if not os.path.exists(args.train):
            _log.error('File does not exists: \'%s\'' % args.train)
            return False

        if not is_text_file(args.train):
            _log.error('File is not a simple text file: \'%s\'' % args.train)
            return False

    if not args.add and not args.delete and not args.train:
        _log.warning('No operation has been executed on dictionary: \'%s\'' % args.dictionary)
        return False

    return True


def main():
    args = get_arguments()
    set_logging_verbosity(args.verbose)
    if not validate_arguments(args):
        sys.exit(1)

    dictionary_file_path = args.dictionary
    is_dictionary_exist = os.path.exists(dictionary_file_path)

    linguist = Linguist()

    if is_dictionary_exist:
        linguist.load_dictionary_from_json(dictionary_file_path)

    if args.train is not None:
        text_file_path = args.train
        linguist.train_dictionary(get_words(file(text_file_path).read()))
        if not is_dictionary_exist:
            _log.info("New dictionary file has been created: \'%s\'" % dictionary_file_path)
        is_dictionary_exist = True

    if args.add is not None:
        add_word_list = [word.lower() for word in args.add]
        linguist.train_dictionary(add_word_list)
        if not is_dictionary_exist:
            _log.info("New dictionary file has been created: \'%s\'" % dictionary_file_path)
        is_dictionary_exist = True

    if args.delete is not None:
        delete_word_set = set(word.lower() for word in args.delete)
        if not is_dictionary_exist:
            _log.error("Could not delete from \'%s\': Dictionary does not exists." % dictionary_file_path)
            sys.exit(1)
        linguist.delete_from_dictionary(delete_word_set)

    linguist.save_dictionary_to_json(dictionary_file_path)


if __name__ == "__main__":
    main()
