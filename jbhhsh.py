from cmd import Cmd
from sqlite3 import connect
from collections import deque
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
    
    def search(self, trans: str) -> List[str]:
        return list(chain(*map(
            lambda row: row[0].split(','),
            chain(
                self.cursor.execute(
                    'SELECT abbr FROM jbhhsh WHERE trans = ?',
                    (trans,)
                ).fetchall(),
                self.cursor.execute(
                    'SELECT abbr FROM jbhhsh WHERE trans LIKE ?',
                    (trans + '(%',)
                ).fetchall(),
                self.cursor.execute(
                    'SELECT abbr FROM jbhhsh WHERE trans LIKE ?',
                    (trans + '（%',)
                ).fetchall()
            )
        )))
    
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
    
    def search_wildcard(self, trans: str) -> Dict[str, List[str]]:
        return dict(map(
            lambda row: (row[0], row[1].split(',')),
            self.cursor.execute(
                'SELECT trans, abbr FROM jbhhsh WHERE trans LIKE ?',
                ('%' + trans + '%',)
            ).fetchall()
        ))


class JbhhshCli(Cmd):
    intro = 'jbhhsh (c) NKID00 2021, under MIT License.'
    prompt = '>>> '

    def preloop(self):
        self.jbhhsh = Jbhhsh()

    def default(self, line: str) -> bool:
        if line == 'exit':
            return True
        if line.startswith(('%', '(', '（', ')', '）')):
            line = line[1:]
            if line.startswith('%'):
                result = self.jbhhsh.search_wildcard(line)
            else:
                result = self.jbhhsh.search_parenthesis(line)
            if len(result) > 0:
                print('\n'.join(map(
                    lambda item: f'{item[0]}: {", ".join(item[1])}',
                    result.items()
                )))
            else:
                print('(none)')
        else:
            result = self.jbhhsh.search(line)
            if len(result) > 0:
                print(', '.join(result))
            else:
                print('(none)')
        return False


if __name__ == '__main__':
    JbhhshCli().cmdloop()
