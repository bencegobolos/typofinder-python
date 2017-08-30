"""
This file contains the implementation of the Typofinder class.
Use this class to find typos in a file based on a dictionary.
"""

import logging

from src.utils import get_words

logging.basicConfig(format='[%(asctime)s][%(levelname)8s][%(name)s]: %(message)s')
_root_log = logging.getLogger("typofinder")
_log = _root_log.getChild(__name__)


class Typofinder(object):
    """
    Uses a Linguist to decide if a file has typos.
    """
    def __init__(self, linguist, text_file_path):
        self._log = _log.getChild(self.__class__.__name__)

        self._linguist = linguist
        self._text_file_path = text_file_path
        self._result_map = {}

    def print_result_map(self):
        """
        Prints a file's typos and suggestions for misspelled words in a table format.
        """
        if not self._result_map:
            _log.debug("Result map is empty.")
            return

        print("\n" + "+" * 72)
        print("{0:33} ==> {1:>33}".format("Unknown word", "Suggestion"))
        print("-" * 72)
        for word, suggestion in sorted(self._result_map.items()):
            if suggestion:
                print("{0:33} ==> {1:>33}".format(word, suggestion))
            else:
                print("{0:33}".format(word))
        print("+" * 72 + "\n")

    def print_affected_rows(self, is_overwrite_mode=False):
        """
        Prints the text file's lines (and it's numbers) where typos were detected.
        It is useful for logging information.
        """

        if not self._result_map:
            _log.debug("Result map is empty.")
            return

        content = file(self._text_file_path).readlines()
        content = [line.strip("\n") for line in content]

        line_number = 0

        for line in content:
            line_number += 1

            line_word_set = set(get_words(line))
            typo_list = self._result_map.keys()

            # Lowering the line's words is necessary because the Linguist's dictionary
            # contains the words in lowercase too.
            if not set([word.lower() for word in line_word_set]).intersection(typo_list):
                # Checking line is unnecessary because there is no unknown word. Skip to next line.
                continue

            for word in line_word_set:
                word_lowered = word.lower()
                if word_lowered not in typo_list:
                    continue

                suggestion = self._result_map.get(word_lowered)
                if suggestion:
                    line = line.replace(word, "[[%s ==> %s]]" % (word, suggestion))
                else:
                    line = line.replace(word, "[[%s]]" % word)

            if is_overwrite_mode:
                content[line_number - 1] = line
            else:
                print("%d:%s" % (line_number, line.strip()))

        if is_overwrite_mode:
            with open(self._text_file_path, 'w') as f:
                # The newline character is needed for the end of the file.
                f.write("\n".join(content) + "\n")
        else:
            print("")

    def execute(self):
        """
        Checks a file for typos and makes suggestions based on the Linguist.
        The typofinder's result map will contain the unknown words and a suggestion for fix if possible.
        """
        _log.info("Executing typofinder on \'%s\'" % self._text_file_path)

        if not self._linguist.get_dictionary():
            _log.error("Linguist's dictionary is empty. Couldn't recognize typos in file(s).")
            return

        content = set(get_words(file(self._text_file_path).read()))
        difference = self._linguist.not_known(content)

        if not difference:
            _log.info("No typo(s) found in file: \'%s\'" % self._text_file_path)
            return

        for word in difference:
            self._result_map[word] = self._linguist.correct(word)

        print("Unknown word(s) has been found in file: \'%s\'" % self._text_file_path)
