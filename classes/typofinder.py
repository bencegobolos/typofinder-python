import re
import logging
import os

logging.basicConfig(format='[%(asctime)s][%(levelname)8s][%(name)s]: %(message)s')
_root_log = logging.getLogger("typofinder")
_log = _root_log.getChild(__name__)


def get_words(text):
    return re.findall('[a-z]+', text.lower())


class Typofinder(object):
    """
    Uses a Linguist to decide if a file has typos.
    """
    def __init__(self, linguist, text_file_path):
        self._log = _log.getChild(self.__class__.__name__)

        self._linguist = linguist
        self._text_file_or_dir_path = text_file_path
        self._result_map = {}

    def clear_result_map(self):
        self._result_map = {}
        _log.debug("Result map has been cleared.")

    def find_text_file_paths(self):
        """
        Find paths of text files.
        :return:
        * list of the text file paths if text_file_or_dir_path property is a directory.
        * list containing one file path if text_file_or_dir_path property is a file.
        """
        if not os.path.isdir(self._text_file_or_dir_path):
            return [self._text_file_or_dir_path]

        text_file_paths = []

        for root, directories, files in os.walk(self._text_file_or_dir_path):
            for file_path in files:
                # TODO(bgobolos): Find a better way to get simple text files from a directory.
                if file_path.endswith(('.tex', '.txt')):
                    text_file_paths.append(os.path.join(root, file_path))

        return text_file_paths

    def print_result_map(self):
        """
        Prints a file's typos and suggestions for misspelled words if possible.
        """
        if not self._result_map:
            _log.info("Result map is empty.")
            return

        # TODO(bgobolos): Improve output format.
        print("\n" + "+" * 50)
        print("Unknown words has been found in file: \'%s\'." % self._text_file_or_dir_path)
        print("Typo\t:\tSuggestion")
        print("-" * 50)
        for word, suggestion in self._result_map.items():
            print("%s\t:\t%s" % (word, suggestion))
        print("+" * 50 + "\n")

    def execute(self):
        """
        Checks files for typos and makes suggestions based on the Linguist.
        :return: map file containing the unknown words and a suggestion for fix if possible.
        """
        file_path_list = self.find_text_file_paths()
        for file_path in file_path_list:

            # Executing the typofinder on multiple files, the result map must be clear before checking a new file.
            self.clear_result_map()

            content = set(get_words(file(file_path).read()))
            difference = self._linguist.not_known(content)

            if not difference:
                _log.info("There are no typos in the file: \'%s\'" % self._text_file_or_dir_path)

            for word in difference:
                self._result_map[word] = self._linguist.correct(word)

            _log.info("Typofinder's result map has been updated.")
            self.print_result_map()
