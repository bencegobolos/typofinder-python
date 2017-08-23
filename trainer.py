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
from src.utils import get_words, is_text_file, find_text_file_abs_paths

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
                        type=str, default=os.path.join(os.path.dirname(__file__), 'htc-dictionary.json'),
                        metavar='DICTIONARY_FILE')
    parser.add_argument('--add',
                        help='add new word(s) or increase the likelihood of suggestion.',
                        nargs='*', metavar='WORD')
    parser.add_argument('--delete',
                        help='delete word(s) from the dictionary.',
                        nargs='*', metavar='WORD')
    parser.add_argument('-t', '--train',
                        help='train dictionary from a file (add every word).',
                        type=str, metavar='TEXT_FILE')
    parser.add_argument('-e', '--ext',
                        help='filter for extensions if input argument is a directory.',
                        action='append', metavar='EXTENSION_TYPE')
    parser.add_argument('--dry-run',
                        help='see the difference between the old and new version of dictionary '
                             'without actually modifying the dictionary.',
                        action='store_true')

    return parser.parse_args()


def validate_arguments(args):
    """
    :param args: Input arguments of the trainer script.
    :return:
      * False: if input arguments would cause an error in the program.
      * True: otherwise.
    """
    if args.train:
        if not os.path.exists(args.train):
            _log.error('File does not exists: \'%s\'' % args.train)
            return False

        if not os.path.isdir(args.train) and not is_text_file(args.train):
            _log.error('File is not a simple text file: \'%s\'' % args.train)
            return False

        if os.path.isdir(args.train):
            text_file_paths = find_text_file_abs_paths(args.train, args.ext)
            if not text_file_paths:
                if args.ext:
                    _log.error("No simple text file were found with the extension(s) %s in directory: \'%s\'"
                               % (args.ext, args.train))
                else:
                    _log.error("No simple text file were found in directory: \'%s\'" % args.train)
                return False

        if args.ext and '' in args.ext and os.path.isdir(args.train):
            _log.warning('Giving an empty string in extensions will ignore other extension filters. '
                         'The script operates on default: find every simple text file in folder: \'%s\'' % args.train)

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

    linguist = Linguist()

    if os.path.exists(dictionary_file_path):
        linguist.load_dictionary_from_json(dictionary_file_path)

    if args.train:
        text_file_path = args.train

        if os.path.isdir(text_file_path):
            file_path_list = find_text_file_abs_paths(text_file_path, args.ext)
        else:
            file_path_list = [text_file_path]

        for file_path in file_path_list:
            _log.debug("Training dictionary from file: \'%s\'" % file_path)
            linguist.train_dictionary(get_words(file(file_path).read()))

    if args.add:
        add_word_list = [word.lower() for word in args.add]
        linguist.train_dictionary(add_word_list)

    if args.delete:
        delete_word_set = set(word.lower() for word in args.delete)
        if not linguist.get_dictionary():
            _log.error("Could not delete from \'%s\': Dictionary does not exists." % dictionary_file_path)
            sys.exit(1)
        linguist.delete_from_dictionary(delete_word_set)

    if args.dry_run:
        linguist_old = Linguist()
        if os.path.exists(dictionary_file_path):
            linguist_old.load_dictionary_from_json(dictionary_file_path)

        added_words = linguist_old.not_known(set(linguist.get_dictionary()))

        if added_words:
            print("New words to \'%s\': %s." % (dictionary_file_path, ', '.join(added_words)))
        else:
            _log.info("No new words would be added to \'%s\'" % dictionary_file_path)
    else:
        linguist.save_dictionary_to_json(dictionary_file_path)


if __name__ == "__main__":
    main()
