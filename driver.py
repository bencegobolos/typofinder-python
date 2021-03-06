#!/usr/bin/python2

"""
This script is made to automatically check the Hightec Development
Platform's user's guide for typos. Other text files can be checked too.
"""

import sys
import os
import argparse
import logging
import textwrap

from src.typofinder import Typofinder
from src.linguist import Linguist
from src.utils import find_text_file_abs_paths, is_text_file

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
    description = 'Check for misspelled words in your simple text files.'
    epilog = textwrap.dedent("""
    example usages:
      driver.py -v text_file
                            Find typos in a simple text file. Use single level
                            verbosity (few additional info will be logged to
                            standard error output).
      driver.py -d my-dict.json ../dir/
                            Find typos in every simple text file which can be
                            found in ../dir/. Use my-dict.json file instead of
                            htc-dictionary.json dictionary.
      driver.py -e .adoc -e .txt /home/name/dir/ -t
                            Find typos in every .adoc and .txt extension simple
                            text file which can be found in /home/name/dir/.
                            Print the unknown words and the suggestion in a
                            table format.
      driver.py -vv -e .tex ../../dir/usersguide/ -l -i htc
                            Find typos in .tex extension simple text file which
                            can be found in ../../dir/usersguide. Use max
                            level of verbosity (more additional info will be
                            logged to standard error output). Print the
                            lines with the unknown words. If the word 'htc' is
                            found in a file it will not be marked as a typo
                            even it is not in the dictionary.
    """)
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=description,
                                     epilog=epilog)
    parser.add_argument('-v', '--verbose', action='count', help='increase verbosity level.')
    parser.add_argument('-e', '--ext',
                        help='filter for extensions if input argument is a directory.',
                        action='append', metavar='EXTENSION_TYPE')
    parser.add_argument('-d', '--dictionary',
                        help='define a dictionary (in .json format) which contains '
                             'the known words (\'htc-dictionary.json\' is given by default).',
                        type=str, default=os.path.join(os.path.dirname(__file__), 'htc-dictionary.json'),
                        metavar='DICTIONARY_FILE')
    parser.add_argument('-i', '--ignore',
                        help='ignore a set of words when searching for typos. '
                             'There words will not be added to the dictionary.',
                        nargs='*', metavar='WORD')
    parser.add_argument('-l', '--line',
                        help='print to console the line where the typo was found.',
                        action='store_true')
    parser.add_argument('-t', '--table',
                        help='print to console the result table containing the unknown words '
                             'and the suggestions (if available).',
                        action='store_true')
    parser.add_argument('--overwrite',
                        help='overwrite the checked file ',
                        action='store_true')
    parser.add_argument('input', help='A file or a directory you want to check.',
                        metavar='INPUT')

    return parser.parse_args()


def validate_arguments(args):
    """
    :param args: Input arguments of the driver script.
    :return:
      * False: if input arguments would cause an error in the program.
      * True: otherwise.
    """
    if not os.path.exists(args.input):
        _log.error('File or directory does not exists: \'%s\'' % args.input)
        return False

    if not os.path.exists(args.dictionary):
        _log.error('Dictionary does not exists: \'%s\'' % args.dictionary)
        return False

    if not os.path.isdir(args.input) and not is_text_file(args.input):
        _log.error('File is not a simple text file: \'%s\'' % args.input)
        return False

    if os.path.isdir(args.input):
        text_file_paths = find_text_file_abs_paths(args.input, args.ext)
        if not text_file_paths:
            if args.ext:
                _log.error("No simple text file were found with the extension(s) %s in directory: \'%s\'"
                           % (args.ext, args.input))
            else:
                _log.error("No simple text file were found in directory: \'%s\'" % args.input)
            return False

    if args.ext and '' in args.ext and os.path.isdir(args.input):
        _log.warning('Giving an empty string in extensions will ignore other extension filters. '
                     'The script operates on default: find every simple text file in folder: \'%s\'' % args.input)

    return True


def main():
    args = get_arguments()
    set_logging_verbosity(args.verbose)
    if not validate_arguments(args):
        sys.exit(1)

    linguist = Linguist()
    linguist.load_dictionary_from_json(args.dictionary)

    if args.ignore:
        add_word_list = [word.lower() for word in args.ignore]
        linguist.train_dictionary(add_word_list)
        _log.info("The following words will be ignored: %s." % ', '.join(add_word_list))

    if os.path.isdir(args.input):
        file_path_list = find_text_file_abs_paths(args.input, args.ext)
    else:
        file_path_list = [args.input]

    for file_path in file_path_list:
        typofinder = Typofinder(linguist, file_path)
        typofinder.execute()
        if args.line:
            typofinder.print_affected_rows()
        if args.table:
            typofinder.print_result_map()
        if args.overwrite:
            typofinder.print_affected_rows(is_overwrite_mode=True)

if __name__ == "__main__":
    if sys.version_info >= (3, 0):
        sys.stdout.write("Sorry, requires Python 2.x, not Python 3.x\n")
        sys.exit(1)
    main()
