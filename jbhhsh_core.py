from sqlite3 import connect
from itertools import chain
from typing import Dict, List


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
