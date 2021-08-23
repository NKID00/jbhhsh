from collections import deque
from random import choice
from sqlite3 import connect
from itertools import chain
from typing import Deque, Dict, Iterable, List, Tuple

from jieba import cut


class Jbhhsh:
    def __init__(self, filename: str = 'build/jbhhsh.db'):
        self.database = connect(
            f'file:{filename}?mode=ro', isolation_level=None, uri=True
        )
        self.cursor = self.database.cursor()

    def __del__(self):
        self.database.close()

    def _search(self, trans: str) -> Dict[str, List[str]]:
        return dict(map(
            lambda row: (row[0], row[1].split(',')),
            chain(
                self.cursor.execute(
                    'SELECT trans, abbr FROM jbhhsh WHERE trans = ?',
                    (trans,)
                ).fetchall(),
                self.cursor.execute(
                    'SELECT trans, abbr FROM jbhhsh WHERE trans LIKE ?',
                    (trans + '(%',)
                ).fetchall(),
                self.cursor.execute(
                    'SELECT trans, abbr FROM jbhhsh WHERE trans LIKE ?',
                    (trans + '（%',)
                ).fetchall()
            )
        ))

    def search(self, trans: str) -> Dict[str, List[str]]:
        result = self._search(trans)
        if len(result) > 0:
            return result
        return self._search(trans.replace('的', '滴'))

    def search_parenthesis(self, trans: str) -> Dict[str, List[str]]:
        return dict(map(
            lambda row: (row[0], row[1].split(',')),
            chain(
                self.cursor.execute(
                    'SELECT trans, abbr FROM jbhhsh WHERE trans LIKE ?',
                    ('%(' + trans + ')',)
                ).fetchall(),
                self.cursor.execute(
                    'SELECT trans, abbr FROM jbhhsh WHERE trans LIKE ?',
                    ('%（' + trans + '）',)
                ).fetchall()
            )
        ))

    def search_all(self, trans: str) -> Dict[str, List[str]]:
        return dict(**self.search(trans), **self.search_parenthesis(trans))

    def search_wildcard(self, trans: str) -> Dict[str, List[str]]:
        return dict(map(
            lambda row: (row[0], row[1].split(',')),
            self.cursor.execute(
                'SELECT trans, abbr FROM jbhhsh WHERE trans LIKE ?',
                ('%' + trans + '%',)
            ).fetchall()
        ))

    def abbreviate_line(self, line: str) -> Tuple[
        Deque[str],
        Deque[Tuple[str, str, str]]
    ]:
        words = list(cut(line))
        result_words = deque()
        replaced_words = deque()
        i = 0
        while i < len(words):
            j = len(words)
            for j in range(len(words), i, -1):
                key = ''.join(words[i:j])
                result = self.jbhhsh.search(key)
                if len(result) > 0:
                    trans, abbr = choice(list(result.items()))
                    abbr = choice(abbr)
                    result_words.append(abbr)
                    replaced_words.append((key, trans, abbr))
                    i = j
                    break
            else:
                result_words.append(words[i])
                i += 1
        return result_words, replaced_words

def join_words(words: Iterable[str]) -> str:
    latest_word_is_ascii = False
    result = ''
    for word in words:
        if word.isascii():
            if latest_word_is_ascii:
                result += ' '
            latest_word_is_ascii = True
        else:
            latest_word_is_ascii = False
        result += word
    return result
