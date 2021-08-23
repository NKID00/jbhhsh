from cmd import Cmd
from collections import deque
from sqlite3 import connect
from itertools import chain
from typing import Dict, List
from random import choice

from jieba import initialize, cut

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


class JbhhshCli(Cmd):
    prompt = '>>> '

    def preloop(self):
        self.jbhhsh = Jbhhsh()

    def default(self, line: str) -> bool:
        if line == 'exit':
            return True

        # if line.startswith(('%', '(', '（', ')', '）')):
        #     line = line[1:]
        #     if line.startswith('%'):
        #         result = self.jbhhsh.search_wildcard(line)
        #     else:
        #         result = self.jbhhsh.search_parenthesis(line)
        #     if len(result) > 0:
        #         print('\n'.join(map(
        #             lambda item: f'{item[0]}: {", ".join(item[1])}',
        #             result.items()
        #         )))
        #     else:
        #         print('(none)')
        # else:
        #     result = self.jbhhsh.search(line)
        #     if len(result) > 0:
        #         print(', '.join(result))
        #     else:
        #         print('(none)')

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

        latest_word_is_ascii = False
        result = ''
        for word in result_words:
            if word.isascii():
                if latest_word_is_ascii:
                    result += ' '
                latest_word_is_ascii = True
            else:
                latest_word_is_ascii = False
            result += word
        print(' ->', result)
        print()

        for key, trans, abbr in replaced_words:
            if key == trans:
                print(f' ** {trans} -> {abbr}')
            else:
                print(f' ** {key}: {trans} -> {abbr}')

        return False


if __name__ == '__main__':
    print('jbhhsh (c) NKID00 2021')
    print('进行一个 MIT 执照的底下（under MIT License')
    print('进行一个结巴分词的初始化...')
    initialize()  # jieba
    print('进行一个主的循环...')
    print('exit可以进行一个程序的退出...')
    JbhhshCli().cmdloop()
