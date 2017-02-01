"""
This file contains the implementation of the Linguist class.
Use this class to update dictionary, get not known words from a list
and make a suggestion for a not known word.
"""

import logging
import json
import collections
import os

logging.basicConfig(format='[%(asctime)s][%(levelname)8s][%(name)s]: %(message)s')
_root_log = logging.getLogger("typofinder")
_log = _root_log.getChild(__name__)


class Linguist(object):
    """
    Has a dictionary and capable of
      * handling dictionary: initialize, edit, save, load, etc.
      * checking if a set of words are in the dictionary.
      * making a suggestion for a not known word.
    """
    def __init__(self):
        self._log = _log.getChild(self.__class__.__name__)

        self._dictionary = collections.defaultdict()

    def get_dictionary(self):
        return self._dictionary

    def train_dictionary(self, word_list):
        """
        Updates the dictionary by
          * incrementing a words likelihood if a word in word_list is known.
          * adding a word from word_list to dictionary if not known.

        :param word_list: list of word which will be added to dictionary or increments it's likelihood.
        """
        if not word_list:
            _log.warning("No words will be added to dictionary: word list is empty.")
            return

        for word in word_list:
            try:
                self._dictionary[word] += 1
            except KeyError:
                self._dictionary[word] = 1

    def delete_from_dictionary(self, word_list):
        """
        Deletes words from dictionary.

        :param word_list: list of words which will be deleted from dictionary.
        """
        if not word_list:
            _log.warning("No words will be deleted from dictionary: word list is empty.")
            return

        if not self._dictionary:
            _log.warning("Can't remove word(s): dictionary is empty.")
            return

        for word in word_list:
            try:
                del self._dictionary[word]
            except KeyError:
                _log.warning("Can't remove word: \'%s\'. No such word in directory." % word)

    def save_dictionary_to_json(self, dictionary_file_path):
        """
        Saves or creates a dictionary file in json format.

        :param dictionary_file_path: path to a dictionary file (could be non-existent).
        """
        if not self._dictionary:
            _log.warning("Dictionary is empty, refusing save.")
            return

        if os.path.exists(dictionary_file_path):
            _log.info("Dictionary will be overwritten: \'%s\'" % dictionary_file_path)
        else:
            _log.info("Dictionary will be created: \'%s\'" % dictionary_file_path)

        with open(dictionary_file_path, 'w') as f:
            json.dump(self._dictionary, f, sort_keys=True, indent=2, separators=(',', ': '))

        _log.info("Dictionary has been saved: \'%s\'" % dictionary_file_path)

    def load_dictionary_from_json(self, dictionary_file_path):
        """
        Loads a dictionary from a json format file.

        :param dictionary_file_path: path to a dictionary file.
        """
        if not os.path.exists(dictionary_file_path):
            _log.error('Dictionary does not exists: \'%s\'' % dictionary_file_path)
            return

        try:
            with open(dictionary_file_path, 'r') as f:
                self._dictionary = json.load(f)
        except (ValueError, IOError):
            _log.error("Given path is not a dictionary: \'%s\'" % dictionary_file_path)
            return

        _log.info("Dictionary has been loaded: \'%s\'" % dictionary_file_path)

    def not_known(self, word_set):
        """
        Checks a set of words if they are known by the dictionary.

        :param word_set: A set of words which will be compared to the dictionary words.
        :return: A set of words which are not known from the dictionary.
        """
        if not word_set:
            _log.info("There is no known word because the given word set is empty.")
            return set()

        return word_set.difference(set(self._dictionary))

    def correct(self, word):
        """
        Implements the algorithm which will correct a word if it is not in the dictionary
        and returns a word that is maximum 2 characters away from an already known one.
        The algorithm was found here (although small changes have been made):
        http://www.learntosolveit.com/python/algorithm_spelling.html
        There is no known use-cases where the 'edits1()', 'known_edits2()' and 'known()' functions will be used
        elsewhere thus they should be nested functions.

        :param word: The word which will be corrected if possible.
        :return:
          * The most likely word from the dictionary which is maximum 2 characters away from the word if it is unknown.
          * None otherwise.
        """
        def edits1(w):
            alphabet = "abcdefghijklmnopqrstuvwxyz"

            splits = [(w[:i], w[i:]) for i in range(len(w) + 1)]
            deletes = [a + b[1:] for a, b in splits if b]
            transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b) > 1]
            replaces = [a + c + b[1:] for a, b in splits for c in alphabet if b]
            inserts = [a + c + b for a, b in splits for c in alphabet]
            return set(deletes + transposes + replaces + inserts)

        def known_edits2(w):
            return set(e2 for e1 in edits1(w) for e2 in edits1(e1) if e2 in self._dictionary)

        def known(word_list):
            return set(w for w in word_list if w in self._dictionary)

        candidates = known([word]) or known(edits1(word)) or known_edits2(word) or [word]
        suggestion = max(candidates, key=self._dictionary.get)

        if suggestion is word:
            """
            At this point the word could be:
            * known by the dictionary.
            * not known but there are no suggestions available.
            In these cases no additional information would be got by returning the word.
            Return None instead.
            """
            return None

        return suggestion
