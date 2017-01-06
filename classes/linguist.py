import logging
import json
import collections
import os

logging.basicConfig(format='[%(asctime)s][%(levelname)8s][%(name)s]: %(message)s')
_root_log = logging.getLogger("linguist")
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

        self._dictionary = collections.defaultdict(lambda: 1)

    def get_dictionary(self):
        return self._dictionary

    def train_dictionary(self, word_list):
        if not word_list:
            _log.warning("No words will be added to dictionary: word list is empty.")
            return

        for word in word_list:
            try:
                self._dictionary[word] += 1
            except KeyError:
                self._dictionary[word] = 1

    def delete_from_dictionary(self, word_list):
        if not word_list:
            _log.warning("No words will be deleted from dictionary: word list is empty.")
            return

        if not self._dictionary:
            _log.error("Can't remove words: dictionary is empty.")

        for word in word_list:
            try:
                del self._dictionary[word]
            except KeyError:
                _log.warning("Can't remove word: \'%s\'. No such word in directory." % word)

    def save_dictionary_to_json(self, json_dictionary_path):
        if os.path.exists(json_dictionary_path):
            _log.info("Overwriting dictionary file: \'%s\'" % self._dictionary)

        with open(json_dictionary_path, 'w') as f:
            json.dump(self._dictionary, f, sort_keys=True, indent=2, separators=(',', ': '))

    def load_dictionary_from_json(self, json_dictionary_path):
        if not os.path.exists(json_dictionary_path):
            _log.error('Dictionary does not exists: \'%s\'' % json_dictionary_path)
            return False

        with open(json_dictionary_path, 'r') as f:
            self._dictionary = json.load(f)

        return True

    def not_known(self, word_set):
        """
        :param word_set: A set of words which will be compared to the dictionary words.
        :return: A set of words which are not known from the dictionary.
        """
        if not word_set:
            _log.warning("There is no known word because the given word set is empty.")
            return set()

        return word_set.difference(set(self._dictionary))

    def correct(self, word):
        """
        This function implements the algorithm which will correct a word if it is not in the dictionary
        and from every entry in this dictionary the word is maximum 2 characters away from another known one.
        The algorithm was found here: http://www.learntosolveit.com/python/algorithm_spelling.html
        There is no known use-cases where the 'edits1()' and 'known_edits2()' functions will be used elsewhere
        thus they should be local functions.
        :param word: The word will be checked if it is in the dictionary otherwise it will return the most likely word
          (up to 2 character difference).
        :return:
          * The word itself if it was correct
          * A word from the dictionary which is maximum 2 characters away from the word if it is unknown
          * Empty string otherwise.
        """
        def edits1(w):
            alphabet = 'abcdefghijklmnopqrstuvwxyz'

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
        return max(candidates, key=self._dictionary.get)
