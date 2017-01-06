#!/usr/bin/python2

# This script is made to automatically check the Hightec Development
# Platform's user's guide for typos. Other text files can be checked too.

import sys
import os
import argparse
import logging
from classes.typofinder import Typofinder
from classes.linguist import Linguist

logging.basicConfig(format='[%(asctime)s][%(levelname)8s][%(name)s]: %(message)s')
_root_log = logging.getLogger("driver")
_log = _root_log.getChild(__name__)


def set_logging_verbosity(level):
    if not level:
        _root_log.setLevel(logging.WARNING)
    elif level == 1:
        _root_log.setLevel(logging.INFO)
    else:
        _root_log.setLevel(logging.DEBUG)


def get_arguments():
    desc = 'Check for misspelled word in your plain text files.'
    epilog = 'Script is made to check for typos automatically ' \
             'in the users guide\'s repository.'
    parser = argparse.ArgumentParser(description=desc, epilog=epilog)
    parser.add_argument("-v", "--verbose", action="count", help="Increase verbosity level")
    parser.add_argument('-d', '--dictionary',
                    help='define a dictionary (in .json format) which contains '
                         'the known words (\'htc-dictionary.json\' is given by default).',
                    type=str, default='htc-dictionary.json', metavar='DICTIONARY')
    parser.add_argument('input', help='A file or a directory you want to check.',
                    metavar='INPUT')

    return parser.parse_args()


def validate_arguments(args):
    """
    :param args: Input arguments of the driver script.
    :return:
    * False: if file or directory does not exists or when a file would be overwritten.
    * True: otherwise.
    """
    if not os.path.exists(args.input):
        _log.error('File or directory does not exists: \'%s\'' % args.input)
        return False

    if not os.path.exists(args.dictionary):
        _log.error('Dictionary does not exists: \'%s\'' % args.dictionary)
        return False

    return True


def main():
    args = get_arguments()
    set_logging_verbosity(args.verbose)
    if not validate_arguments(args):
        sys.exit(1)

    linguist = Linguist()
    linguist.load_dictionary_from_json(args.dictionary)

    typofinder = Typofinder(linguist, args.input)
    typofinder.execute()


if __name__ == "__main__":
    main()
