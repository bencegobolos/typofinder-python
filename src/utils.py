"""
This file contains commonly used helper functions.
"""

import re
import os
import sys


def get_words(text):
    """
    Gets every word from a text.

    :param text: text string.
    :return: list of words found in text.
    """
    return re.findall("[a-z]+", text.lower())


def is_text_file(file_path, block_size=512):
    """
    This algorithm was found here:
    http://eli.thegreenplace.net/2011/10/19/perls-guess-if-file-is-text-or-binary-implemented-in-python/
    Uses heuristics to guess whether the given file is text or binary,
    by reading a single block of bytes from the file.
    If more than 30% of the chars in the block are non-text, or there
    are NUL ('\x00') bytes in the block, assume this is a binary file.

    :param file_path: path to a file.
    :param block_size: size of block which will be tested from file on file_path.
    :return:
      * True: if file on file_path is a simple text file.
      * False: otherwise.
    """
    py3 = sys.version_info[0] == 3
    # A function that takes an integer in the 8-bit range and returns
    # a single-character byte object in py3 / a single-character string
    # in py2.
    int2byte = (lambda x: bytes((x,))) if py3 else chr

    _text_characters = (
            b''.join(int2byte(i) for i in range(32, 127)) +
            b'\n\r\t\f\b')

    block = file(file_path).read(block_size)
    if b'\x00' in block:
        # Files with null bytes are binary
        return False
    elif not block:
        # An empty file is considered a valid text file
        return True

    # Use translate's 'deletechars' argument to efficiently remove all
    # occurrences of _text_characters from the block
    non_text = block.translate(None, _text_characters)
    return float(len(non_text)) / len(block) <= 0.30


def find_text_file_abs_paths(directory_path, filter_for_ext=None):
    """
    Finds absolute paths of files in directory_path. Filter for specific extensions.

    :param directory_path: recursively searched for files.
    :param filter_for_ext: files with these extensions will be collected only. No filtering by default.
    :return: list of absolute paths of simple text files found in directory_path.
    """
    text_file_paths = []
    extensions = ''

    # If filter_for_ext is given it must be converted to a tuple because of the .endswith() function.
    if filter_for_ext:
        extensions = tuple(filter_for_ext)

    for root, directories, files in os.walk(directory_path):
        for file_name in files:
            file_path = os.path.join(os.path.abspath(root), file_name)
            if file_path.endswith(extensions) and is_text_file(file_path):
                text_file_paths.append(file_path)

    return text_file_paths
